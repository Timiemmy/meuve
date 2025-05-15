from rest_framework import serializers
from django.utils import timezone
from .models import Booking
from booking.utils import generate_booking_code
from vehicle.models import Vehicle
from useraccount.serializers import CustomUserSerializer
from vehicle.serializers import VehicleSerializer
from datetime import datetime


class BookingSerializer(serializers.ModelSerializer):
    """
    Base serializer for Booking model.
    """
    passenger_details = CustomUserSerializer(
        source='passenger', read_only=True)
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)
    booking_status = serializers.CharField(
        source='get_booking_status', read_only=True)
    is_booking_code_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'passenger', 'passenger_details', 'vehicle', 'vehicle_details',
            'trip_type', 'source_park', 'destination_park', 'return_date',
            'pickup_type', 'pickup_address', 'adult_count', 'children_count',
            'return_adult_count', 'return_children_count', 'booking_date',
            'travel_date', 'luggage_count', 'special_requests', 'payment_status',
            'actual_pickup_time', 'actual_dropoff_time', 'cancellation_reason',
            'cancellation_time', 'booking_code', 'is_checked_in', 'is_checked_out',
            'check_in_time', 'check_out_time', 'amount', 'is_paid',
            'booking_status', 'is_booking_code_valid'
        ]
        read_only_fields = [
            'booking_date', 'booking_code', 'is_checked_in', 'is_checked_out',
            'check_in_time', 'check_out_time', 'amount'
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new bookings.
    Vehicle is selected from the vehicle page and passed in the request.
    """
    class Meta:
        model = Booking
        fields = [
            'trip_type', 'source_park', 'destination_park', 'travel_date',
            'return_date', 'pickup_type', 'pickup_address', 'adult_count',
            'children_count', 'return_adult_count', 'return_children_count',
            'luggage_count', 'special_requests', 'vehicle'
        ]

    def validate(self, data):
        """
        Validate booking data based on trip type and other requirements.
        """
        # Validate round trip data
        if data['trip_type'] == 'ROUND':
            if not data.get('return_date'):
                raise serializers.ValidationError({
                    'return_date': 'Return date is required for round trips'
                })

            if data['return_date'] <= data['travel_date']:
                raise serializers.ValidationError({
                    'return_date': 'Return date must be after travel date'
                })

            if not data.get('return_adult_count'):
                raise serializers.ValidationError({
                    'return_adult_count': 'Return adult count is required for round trips'
                })

        # Validate home pickup
        if data['pickup_type'] == 'HOME' and not data.get('pickup_address'):
            raise serializers.ValidationError({
                'pickup_address': 'Pickup address is required for home pickup'
            })

        # Validate travel date
        if data['travel_date'] < timezone.now():
            raise serializers.ValidationError({
                'travel_date': 'Travel date cannot be in the past'
            })

        # Validate passenger counts
        if data.get('adult_count', 0) + data.get('children_count', 0) <= 0:
            raise serializers.ValidationError({
                'adult_count': 'At least one passenger is required'
            })

        return data

    def calculate_amount(self, vehicle, adult_count, children_count, is_round_trip=False):
        """
        Calculate the total amount based on vehicle trip amount and passenger counts.
        Children are charged at 50% of adult fare.
        """
        adult_fare = vehicle.trip_amount
        child_fare = vehicle.trip_amount * 0.5  # 50% of adult fare

        # Calculate one-way amount
        one_way_amount = (adult_count * adult_fare) + \
            (children_count * child_fare)

        # Double the amount for round trip
        if is_round_trip:
            return one_way_amount * 2
        return one_way_amount

    def create(self, validated_data):
        """
        Create a new booking with transaction atomic to ensure proper rollback.
        """
        from django.db import transaction

        with transaction.atomic():
            # Get the vehicle from the validated data
            vehicle = validated_data.pop('vehicle')
            if not vehicle:
                raise serializers.ValidationError(
                    "Vehicle is required for booking creation.")

            # Validate vehicle availability
            if not vehicle.is_available or vehicle.is_booked:
                raise serializers.ValidationError(
                    "Selected vehicle is not available.")

            # Calculate total passengers
            total_passengers = (
                validated_data.get('adult_count', 0) +
                validated_data.get('children_count', 0)
            )

            # Validate seat availability
            if vehicle.seats < total_passengers:
                raise serializers.ValidationError(
                    "Not enough seats available in the selected vehicle.")

            # Calculate the total amount
            is_round_trip = validated_data.get('trip_type') == 'ROUND'
            amount = self.calculate_amount(
                vehicle,
                validated_data.get('adult_count', 0),
                validated_data.get('children_count', 0),
                is_round_trip
            )

            # Generate booking code
            booking_code = generate_booking_code()

            # Create booking with the selected vehicle
            booking = Booking.objects.create(
                vehicle=vehicle,
                booking_date=timezone.now(),
                amount=amount,
                booking_code=booking_code,
                **validated_data
            )

            # Update vehicle seats
            vehicle.seats -= total_passengers
            if vehicle.seats <= 0:
                vehicle.is_available = False
                vehicle.is_booked = True
            vehicle.save()

            return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating bookings.
    Handles check-in and check-out operations.
    """
    class Meta:
        model = Booking
        fields = [
            'is_checked_in', 'is_checked_out', 'special_requests',
            'cancellation_reason'
        ]

    def validate(self, data):
        """
        Validate update operations.
        """
        instance = self.instance

        # Validate check-out can't happen before check-in
        if data.get('is_checked_out') and not instance.is_checked_in:
            raise serializers.ValidationError({
                'is_checked_out': 'Cannot check out before checking in'
            })

        # Validate cancellation
        if data.get('cancellation_reason') and not data.get('cancellation_reason').strip():
            raise serializers.ValidationError({
                'cancellation_reason': 'Cancellation reason is required'
            })

        return data


class BookingDetailSerializer(BookingSerializer):
    """
    Detailed serializer for booking information.
    Includes additional vehicle and passenger details.
    """
    class Meta(BookingSerializer.Meta):
        fields = BookingSerializer.Meta.fields + [
            'source_park_details',
            'destination_park_details'
        ]

    def get_vehicle_info(self, obj):
        return {
            "name": obj.vehicle.name,
            "model": obj.vehicle.model,
            "license_plate": obj.vehicle.license_plate,
            "total_seats": obj.vehicle.total_seats,
            "available_seats": obj.vehicle.seats,
            "departure_time": obj.vehicle.departure_time,
            "arrival_time": obj.vehicle.arrival_time
        }

    def validate(self, data):
        """
        Validates:
        - Pickup address for home pickup
        - Return counts only for round trips
        - Vehicle availability and seat capacity
        """
        trip_type = data.get('trip_type')
        departure_park = data.get('source_park')
        arrival_park = data.get('destination_park')
        travel_date = data.get('travel_date')
        return_date = data.get('return_date')
        pickup_type = data.get('pickup_type')
        pickup_address = data.get('pickup_address')
        adult = data.get('adult_count', 0)
        children = data.get('children_count', 0)
        return_adult = data.get('return_adult_count', 0)
        return_children = data.get('return_children_count', 0)

        # Pickup address required for home pickup
        if pickup_type == 'HOME' and not pickup_address:
            raise serializers.ValidationError(
                "Pickup address is required for home pickup.")

        if trip_type == 'ROUND':
            if not return_date:
                raise serializers.ValidationError(
                    "Return date is required for round trip.")
            if return_adult + return_children <= 0:
                raise serializers.ValidationError(
                    "Return trip must have at least one passenger.")
        else:
            # Clear return values for non-round trips
            data['return_date'] = None
            data['return_adult_count'] = 0
            data['return_children_count'] = 0

        total_departing = adult + children
        total_returning = return_adult + return_children if trip_type == 'ROUND' else 0

        # VEHICLE VALIDATION — DEPARTING LEG
        travel_start = travel_date.replace(hour=0, minute=0, second=0)
        travel_end = travel_date.replace(hour=23, minute=59, second=59)

        available_vehicle = Vehicle.objects.filter(
            departure_park=departure_park,
            arrival_park=arrival_park,
            departure_time__range=(travel_start, travel_end),
            is_available=True,
            is_booked=False,
            seats__gte=total_departing
        ).first()

        if not available_vehicle:
            raise serializers.ValidationError(
                "No vehicle available for departure trip with enough seats. Try another day.")

        # If ROUND TRIP, VALIDATE RETURN LEG TOO
        if trip_type == 'ROUND':
            return_start = return_date.replace(hour=0, minute=0, second=0)
            return_end = return_date.replace(hour=23, minute=59, second=59)

            return_vehicle = Vehicle.objects.filter(
                departure_park=arrival_park,
                arrival_park=departure_park,
                departure_time__range=(return_start, return_end),
                is_available=True,
                is_booked=False,
                seats__gte=total_returning
            ).first()

            if not return_vehicle:
                raise serializers.ValidationError(
                    "No vehicle available for return trip with enough seats. Try another day.")

            data['return_vehicle'] = return_vehicle

        data['vehicle'] = available_vehicle
        return data

    def create(self, validated_data):
        """
        Handles:
        - Reducing seat count on both outbound and return vehicles
        - Booking creation with booking_code and QR
        """
        from django.db import transaction
        total_departing = validated_data['adult_count'] + \
            validated_data['children_count']
        total_returning = validated_data.get(
            'return_adult_count', 0) + validated_data.get('return_children_count', 0)
        vehicle = validated_data['vehicle']
        return_vehicle = validated_data.pop('return_vehicle', None)

        with transaction.atomic():
            # Lock and update departing vehicle
            vehicle = Vehicle.objects.select_for_update().get(id=vehicle.id)
            if vehicle.seats < total_departing:
                raise serializers.ValidationError(
                    "Departure vehicle just got fully booked. Try again.")
            vehicle.seats -= total_departing
            if vehicle.seats <= 0:
                vehicle.is_available = False
                vehicle.is_booked = True
            vehicle.save()

            # Lock and update return vehicle (if any)
            if return_vehicle:
                return_vehicle = Vehicle.objects.select_for_update().get(id=return_vehicle.id)
                if return_vehicle.seats < total_returning:
                    raise serializers.ValidationError(
                        "Return vehicle just got fully booked. Try again.")
                return_vehicle.seats -= total_returning
                if return_vehicle.seats <= 0:
                    return_vehicle.is_available = False
                    return_vehicle.is_booked = True
                return_vehicle.save()

            # Create the booking
            booking = Booking.objects.create(
                booking_code=generate_booking_code(),
                **validated_data
            )

            qr = generate_qr_code(booking.booking_code)
            booking.qr_code.save(f"{booking.booking_code}_qr.png", qr)
            booking.save()
            return booking
