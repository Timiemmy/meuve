from django.db import models
from core.models import TimeStampedModel, UUIDModel
from park.models import Park
from datetime import timedelta


class VehicleType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Vehicle Type'
        verbose_name_plural = 'Vehicle Types'
        ordering = ['name']

    def __str__(self):
        return self.name


class VehicleStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    IN_SERVICE = 'in_service', 'In Service'
    MAINTENANCE = 'maintenance', 'Under Maintenance'
    OUT_OF_SERVICE = 'out_of_service', 'Out of Service'


class Vehicle(TimeStampedModel, UUIDModel):
    name = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    category = models.ManyToManyField(VehicleType)
    color = models.CharField(max_length=30, null=True, blank=True)
    license_plate = models.CharField(max_length=15, unique=True)
    vin = models.CharField(max_length=17, unique=True)
    amenities = models.ManyToManyField('Amenity')
    total_seats = models.PositiveIntegerField(default=1, null=True, blank=True)
    seats = models.PositiveIntegerField(default=1, blank=True)
    status = models.CharField(
        max_length=20, choices=VehicleStatus.choices, default=VehicleStatus.AVAILABLE)
    park_location = models.ForeignKey(
        Park, on_delete=models.PROTECT, related_name='vehicles')
    departure_park = models.OneToOneField(
        Park, on_delete=models.PROTECT, related_name='from_park', null=True, blank=True)
    arrival_park = models.OneToOneField(
        Park, on_delete=models.PROTECT, related_name='to_park', null=True, blank=True)

    is_departed = models.BooleanField(default=False)
    departure_time = models.DateTimeField(null=True, blank=True)

    is_arrived = models.BooleanField(default=False)
    arrival_time = models.DateTimeField(null=True, blank=True)

    is_available = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False)
    has_entourage_option = models.BooleanField(default=False)
    has_security_option = models.BooleanField(default=False)

    fuel_type = models.CharField(max_length=20, blank=True)
    fuel_efficiency = models.FloatField(null=True, blank=True)

    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    daily_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    trip_amount = models.FloatField(null=True, blank=True)

    trip_count = models.PositiveIntegerField(default=0)

    def rotate_schedule(self):
        """
        Rotate the vehicle's schedule by swapping departure and arrival parks
        and updating the times by 6 hours.
        """
        if not self.departure_park or not self.arrival_park:
            return False

        # Only rotate if vehicle has both departed and arrived
        if not self.is_departed or not self.is_arrived:
            return False

        # Swap departure and arrival parks
        current_departure = self.departure_park
        self.departure_park = self.arrival_park
        self.arrival_park = current_departure

        # Update times by adding 6 hours
        if self.departure_time and self.arrival_time:
            self.departure_time = self.arrival_time + timedelta(hours=6)
            self.arrival_time = self.departure_time + timedelta(hours=6)

        if self.is_departed and self.is_arrived:
            self.trip_count += 1

        # Reset the flags after rotation
        self.is_departed = False
        self.is_arrived = False

        self.save()
        return True

    def update_schedule(self, departure_park, arrival_park, departure_time):
        """
        Update the vehicle's schedule with new departure and arrival parks and times.
        """
        self.departure_park = departure_park
        self.arrival_park = arrival_park
        self.departure_time = departure_time
        self.arrival_time = departure_time + timedelta(hours=6)
        # Reset flags when updating schedule
        self.is_departed = False
        self.is_arrived = False
        self.save()

    def check_and_rotate(self):
        """
        Check if the vehicle has arrived and rotate the schedule if needed.
        This should be called periodically (e.g., via a scheduled task).
        """
        from django.utils import timezone
        now = timezone.now()

        # Check if vehicle has both departed and arrived
        if self.is_departed and self.is_arrived:
            return self.rotate_schedule()
        return False

    class Meta:
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'

    def __str__(self):
        make = self.make or "Unknown Make"
        model = self.model or "Unknown Model"
        year = self.year or "Unknown Year"
        return f"{make} {model} ({year})"


class Amenity(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    icon = models.CharField(max_length=30, null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class VehicleImage(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='vehicle_images/')
    caption = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.vehicle}"
