from django.db import models
from useraccount.models import CustomUser
from vehicle.models import Vehicle
from park.models import Park


class Booking(models.Model):
    TRIP_TYPES = (
        ('ONEWAY', 'One Way'),
        ('ROUND', 'Round Trip'),
        ('HOURLY', 'Hourly Rental'),
        ('DAILY', 'Daily Rental')
    )

    passenger = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    trip_type = models.CharField(max_length=10, choices=TRIP_TYPES)

    # Location information
    source_park = models.ForeignKey(Park, on_delete=models.PROTECT, related_name='departures')
    destination_park = models.ForeignKey(Park, on_delete=models.PROTECT, related_name='arrivals')

    # Round trip specific fields
    return_date = models.DateTimeField(null=True, blank=True)

    pickup_type = models.CharField(max_length=10, choices=[
        ('HOME', 'Home Pickup'),
        ('PARK', 'Park Meeting')
    ])
    pickup_address = models.TextField(blank=True, null=True)
    adult_count = models.PositiveIntegerField(default=1)  # how many people booking for
    children_count = models.PositiveIntegerField(default=0)
    return_adult_count = models.PositiveIntegerField(default=1)
    return_children_count = models.PositiveIntegerField(default=0)

    booking_date = models.DateTimeField(auto_now_add=True)
    travel_date = models.DateTimeField()
    luggage_count = models.PositiveIntegerField()
    need_entourage = models.BooleanField(default=False)
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ])

    actual_pickup_time = models.DateTimeField(null=True, blank=True)
    actual_dropoff_time = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancellation_time = models.DateTimeField(null=True, blank=True)

    # for more security
    booking_code = models.CharField(max_length=10, unique=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    is_checked_in = models.BooleanField(default=False)
    is_checked_out = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=True)

    def __str__(self):
        return f"Booking {self.booking_code}: {self.origin_address} to {self.destination_address}"

    def is_round_trip(self):
        return self.trip_type == 'ROUND'
