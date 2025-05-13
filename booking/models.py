from django.db import models
from django.utils import timezone
from useraccount.models import CustomUser
from vehicle.models import Vehicle
from park.models import Park
import uuid


class Booking(models.Model):
    TRIP_TYPES = (
        ('ONEWAY', 'One Way'),
        ('ROUND', 'Round Trip')
    )

    passenger = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    trip_type = models.CharField(max_length=10, choices=TRIP_TYPES)

    # Location information
    source_park = models.ForeignKey(
        Park, on_delete=models.PROTECT, related_name='departures')
    destination_park = models.ForeignKey(
        Park, on_delete=models.PROTECT, related_name='arrivals')

    # Round trip specific fields
    return_date = models.DateTimeField(null=True, blank=True)

    pickup_type = models.CharField(max_length=10, choices=[
        ('HOME', 'Home Pickup'),
        ('PARK', 'Park Meeting')
    ])
    pickup_address = models.TextField(blank=True, null=True)
    adult_count = models.PositiveIntegerField(
        default=1)  # how many people booking for
    children_count = models.PositiveIntegerField(default=0)
    return_adult_count = models.PositiveIntegerField(default=1)
    return_children_count = models.PositiveIntegerField(default=0)

    booking_date = models.DateTimeField(auto_now_add=True)
    travel_date = models.DateTimeField()
    luggage_count = models.PositiveIntegerField()
    special_requests = models.TextField(blank=True)
    payment_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ])

    actual_pickup_time = models.DateTimeField(null=True, blank=True)
    actual_dropoff_time = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancellation_time = models.DateTimeField(null=True, blank=True)

    # for more security
    booking_code = models.CharField(max_length=10, unique=True, blank=True)
    is_checked_in = models.BooleanField(default=False)
    is_checked_out = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking {self.booking_code}: {self.source_park} to {self.destination_park}"

    def save(self, *args, **kwargs):
        # Handle check-in
        if self.is_checked_in and not self.check_in_time:
            self.check_in_time = timezone.now()

        # Handle check-out
        if self.is_checked_out and not self.check_out_time:
            self.check_out_time = timezone.now()
            # Expire booking code by setting it to None
            self.booking_code = None

        super().save(*args, **kwargs)

    @property
    def is_booking_code_valid(self):
        """
        Check if the booking code is valid (not expired)
        """
        return bool(self.booking_code) and not self.is_checked_out

    @property
    def booking_status(self):
        """
        Get the current status of the booking
        """
        if self.is_checked_out:
            return "Completed"
        elif self.is_checked_in:
            return "In Progress"
        elif self.payment_status == 'confirmed':
            return "Confirmed"
        elif self.payment_status == 'canceled':
            return "Canceled"
        else:
            return "Pending"
