from django_filters import rest_framework as filters
from .models import Booking


class BookingFilter(filters.FilterSet):
    """
    Filter set for Booking model.
    Enables filtering by various fields and date ranges.
    """
    min_travel_date = filters.DateFilter(
        field_name='travel_date', lookup_expr='gte')
    max_travel_date = filters.DateFilter(
        field_name='travel_date', lookup_expr='lte')
    min_booking_date = filters.DateFilter(
        field_name='booking_date', lookup_expr='gte')
    max_booking_date = filters.DateFilter(
        field_name='booking_date', lookup_expr='lte')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    booking_code = filters.CharFilter(
        field_name='booking_code', lookup_expr='exact')
    passenger = filters.CharFilter(
        field_name='passenger__email', lookup_expr='icontains')
    vehicle = filters.CharFilter(
        field_name='vehicle__plate_number', lookup_expr='icontains')
    source_park = filters.CharFilter(
        field_name='source_park__name', lookup_expr='icontains')
    destination_park = filters.CharFilter(
        field_name='destination_park__name', lookup_expr='icontains')
    is_checked_in = filters.BooleanFilter(field_name='is_checked_in')
    is_checked_out = filters.BooleanFilter(field_name='is_checked_out')
    is_paid = filters.BooleanFilter(field_name='is_paid')
    trip_type = filters.CharFilter(field_name='trip_type', lookup_expr='exact')
    pickup_type = filters.CharFilter(
        field_name='pickup_type', lookup_expr='exact')

    class Meta:
        model = Booking
        fields = [
            'trip_type', 'pickup_type', 'is_checked_in', 'is_checked_out',
            'is_paid', 'booking_code', 'passenger', 'vehicle', 'source_park',
            'destination_park'
        ]
