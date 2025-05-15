from django.db.models import F, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, generics, permissions, status
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Booking
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    BookingDetailSerializer,
    BookingUpdateSerializer
)
from vehicle.models import Vehicle
from park.models import Park
from datetime import datetime, timedelta
from django.db import transaction
from rest_framework.filters import SearchFilter, OrderingFilter
from useraccount.permissions import IsAdmin, IsAdminOrFleetManager, IsOwner, IsAgent
from .filters import BookingFilter


class BookingListView(generics.ListAPIView):
    """
    List all bookings with filtering and search capabilities.
    Only accessible by admin users or agents.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin | IsAgent]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookingFilter
    search_fields = ['booking_code', 'passenger__email']
    ordering_fields = ['booking_date', 'travel_date',
                       'check_in_time', 'check_out_time']
    ordering = ['-booking_date']

    def get_queryset(self):
        return Booking.objects.select_related(
            'passenger',
            'vehicle',
            'source_park',
            'destination_park'
        ).all()


class UserBookingListView(generics.ListAPIView):
    """
    List bookings for the authenticated user.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookingFilter
    search_fields = ['booking_code', 'vehicle__license_plate']
    ordering_fields = ['booking_date', 'travel_date',
                       'check_in_time', 'check_out_time']
    ordering = ['-booking_date']

    def get_queryset(self):
        return Booking.objects.select_related(
            'vehicle',
            'source_park',
            'destination_park'
        ).filter(passenger=self.request.user)


class BookingCreateView(generics.CreateAPIView):
    """
    Create a new booking.
    The vehicle is selected from the vehicle page, so it's passed in the request.
    """
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)


class BookingDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific booking.
    """
    serializer_class = BookingDetailSerializer
    permission_classes = [permissions.IsAuthenticated,
                          IsOwner | IsAdmin | IsAgent]
    queryset = Booking.objects.select_related(
        'passenger',
        'vehicle',
        'source_park',
        'destination_park'
    )


class BookingUpdateView(generics.UpdateAPIView):
    """
    Update a booking.
    Handles check-in and check-out operations.
    """
    serializer_class = BookingUpdateSerializer
    permission_classes = [permissions.IsAuthenticated,
                          IsOwner | IsAdmin | IsAgent]
    queryset = Booking.objects.all()

    def perform_update(self, serializer):
        with transaction.atomic():
            instance = serializer.instance

            # Handle check-in
            if serializer.validated_data.get('is_checked_in') and not instance.is_checked_in:
                serializer.validated_data['check_in_time'] = timezone.now()

            # Handle check-out
            if serializer.validated_data.get('is_checked_out') and not instance.is_checked_out:
                serializer.validated_data['check_out_time'] = timezone.now()
                # Expire booking code
                serializer.validated_data['booking_code'] = None

            serializer.save()


class BookingDeleteView(generics.DestroyAPIView):
    """
    Delete a booking.
    Only allowed for admin users or if the booking is not checked in.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated,
                          IsOwner | IsAdmin | IsAgent]
    queryset = Booking.objects.all()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and instance.is_checked_in:
            raise permissions.PermissionDenied(
                "Cannot delete a booking that has been checked in.")
        instance.delete()


class BookingCheckInView(generics.UpdateAPIView):
    """
    Check in a passenger for their booking.
    """
    serializer_class = BookingUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin | IsAgent]
    queryset = Booking.objects.all()

    def update(self, request, *args, **kwargs):
        booking = self.get_object()

        if booking.is_checked_in:
            return Response(
                {'error': 'Booking is already checked in'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.travel_date.date() != timezone.now().date():
            return Response(
                {'error': 'Cannot check in before travel date'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.is_checked_in = True
        booking.check_in_time = timezone.now()
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class BookingCheckOutView(generics.UpdateAPIView):
    """
    Check out a passenger from their booking.
    """
    serializer_class = BookingUpdateSerializer
    permission_classes = [permissions.IsAuthenticated,
                          IsAgent | IsAdminOrFleetManager]
    queryset = Booking.objects.all()

    def update(self, request, *args, **kwargs):
        booking = self.get_object()

        if not booking.is_checked_in:
            return Response(
                {'error': 'Cannot check out before checking in'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.is_checked_out:
            return Response(
                {'error': 'Booking is already checked out'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.is_checked_out = True
        booking.check_out_time = timezone.now()
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class BookingCancelView(generics.UpdateAPIView):
    """
    Cancel a booking with reason.
    """
    serializer_class = BookingUpdateSerializer
    permission_classes = [permissions.IsAuthenticated,
                          IsOwner | IsAgent | IsAdmin]
    queryset = Booking.objects.all()

    def update(self, request, *args, **kwargs):
        booking = self.get_object()

        if booking.is_checked_in:
            return Response(
                {'error': 'Cannot cancel a checked-in booking'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cancellation_reason = request.data.get('cancellation_reason')
        if not cancellation_reason:
            return Response(
                {'error': 'Cancellation reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.cancellation_reason = cancellation_reason
        booking.cancellation_time = timezone.now()
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class UpcomingBookingsView(generics.ListAPIView):
    """
    Get upcoming bookings for the user.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            Q(passenger=self.request.user) &
            Q(travel_date__gte=timezone.now()) &
            Q(cancellation_time__isnull=True)
        ).order_by('travel_date')


class PastBookingsView(generics.ListAPIView):
    """
    Get past bookings for the user.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            Q(passenger=self.request.user) &
            Q(travel_date__lt=timezone.now())
        ).order_by('-travel_date')


class ActiveBookingsView(generics.ListAPIView):
    """
    Get active bookings (checked in but not checked out).
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            Q(passenger=self.request.user) &
            Q(is_checked_in=True) &
            Q(is_checked_out=False)
        ).order_by('-check_in_time')
