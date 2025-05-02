from django.core.files import File
from io import BytesIO
import qrcode
import uuid
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, generics, permissions, status
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from booking.models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer, BookingDetailSerializer
from vehicle.models import Vehicle
from park.models import Park
from datetime import datetime, timedelta


class BookingListView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'trip_type', 'is_paid']

    def get_queryset(self):
        # Only return bookings for the authenticated user
        return Booking.objects.filter(passenger__user=self.request.user)


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow users to access their own bookings
        return Booking.objects.filter(passenger__user=self.request.user)

    def perform_update(self, serializer):
        # Add any additional logic needed when updating a booking
        serializer.save()

    def perform_destroy(self, instance):
        # Add any additional logic needed when deleting a booking
        instance.delete()


class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Get the data from request
        data = request.data.copy()

        # Get trip type and validate required fields
        trip_type = data.get('trip_type')
        travel_date = data.get('travel_date')
        return_date = data.get('return_date')
        source_park_id = data.get('source_park')
        destination_park_id = data.get('destination_park')
        adult_count = int(data.get('adult_count', 1))
        children_count = int(data.get('children_count', 0))
        return_adult_count = int(data.get('return_adult_count', 1))
        return_children_count = int(data.get('return_children_count', 0))

        # Validate round trip data
        if trip_type == 'ROUND':
            if not return_date:
                return Response(
                    {"error": "Return date is required for round trips"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Convert string dates to datetime objects
            try:
                travel_date = datetime.strptime(
                    travel_date, '%Y-%m-%dT%H:%M:%S')
                return_date = datetime.strptime(
                    return_date, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if return_date <= travel_date:
                return Response(
                    {"error": "Return date must be after travel date"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Find available vehicles for the travel date
        available_vehicles = Vehicle.objects.filter(
            departure_park_id=source_park_id,
            arrival_park_id=destination_park_id,
            departure_time__date=travel_date.date(),
            is_available=True,
            status='available'
        ).annotate(
            booked_seats=F('total_seats') - F('seats')
        ).filter(
            booked_seats__gte=adult_count + children_count
        )

        if not available_vehicles.exists():
            return Response(
                {"error": "No vehicles available for the selected date and route. Please try another date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # For round trips, check return date availability
        if trip_type == 'ROUND':
            return_vehicles = Vehicle.objects.filter(
                departure_park_id=destination_park_id,
                arrival_park_id=source_park_id,
                departure_time__date=return_date.date(),
                is_available=True,
                status='available'
            ).annotate(
                booked_seats=F('total_seats') - F('seats')
            ).filter(
                booked_seats__gte=return_adult_count + return_children_count
            )

            if not return_vehicles.exists():
                return Response(
                    {"error": "No vehicles available for the return date. Please try another date."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Select the first available vehicle
        vehicle = available_vehicles.first()

        # Create booking code
        booking_code = str(uuid.uuid4())[:8].upper()

        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(booking_code)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Save QR code to BytesIO
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)

        # Create booking
        booking_data = {
            'passenger': request.user.passenger.id,
            'vehicle': vehicle.id,
            'trip_type': trip_type,
            'source_park': source_park_id,
            'destination_park': destination_park_id,
            'travel_date': travel_date,
            'return_date': return_date if trip_type == 'ROUND' else None,
            'pickup_type': data.get('pickup_type'),
            'pickup_address': data.get('pickup_address'),
            'adult_count': adult_count,
            'children_count': children_count,
            'return_adult_count': return_adult_count if trip_type == 'ROUND' else None,
            'return_children_count': return_children_count if trip_type == 'ROUND' else None,
            'luggage_count': data.get('luggage_count', 0),
            'need_entourage': data.get('need_entourage', False),
            'special_requests': data.get('special_requests', ''),
            'booking_code': booking_code,
            'amount': vehicle.trip_amount * (2 if trip_type == 'ROUND' else 1)
        }

        serializer = self.get_serializer(data=booking_data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        # Update vehicle seats
        vehicle.seats = F('seats') + (adult_count + children_count)
        vehicle.save()

        # For round trips, update return vehicle seats
        if trip_type == 'ROUND':
            return_vehicle = return_vehicles.first()
            return_vehicle.seats = F(
                'seats') + (return_adult_count + return_children_count)
            return_vehicle.save()

        # Save QR code
        booking.qr_code.save(f'{booking_code}.png', File(qr_buffer), save=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
