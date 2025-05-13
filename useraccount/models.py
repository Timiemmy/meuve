from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import TimeStampedModel, UUIDModel
from park.models import Park
from vehicle.models import Vehicle
from .managers import CustomUserManager


class CustomUser(AbstractUser, TimeStampedModel, UUIDModel):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(
        null=True, blank=True, verbose_name='Birthday')
    phone_number = models.CharField(max_length=15, blank=True)
    phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.groups.filter(name='admin').exists()

    @property
    def is_agent(self):
        return self.groups.filter(name='agent').exists()

    @property
    def is_fleet_manager(self):
        return self.groups.filter(name='fleetmanager').exists()

    @property
    def is_driver(self):
        return self.groups.filter(name='driver').exists()

    def save(self, *args, **kwargs):
        # Check if this is a new user or an existing one being updated
        is_new = self._state.adding

        # Save the user first to get the ID
        super().save(*args, **kwargs)

        # Handle AdminUser
        if self.is_admin:
            if not hasattr(self, 'admin_profile'):
                AdminUser.objects.create(user=self)

        # Handle Agent
        if self.is_agent:
            if not hasattr(self, 'agent_profile'):
                Agent.objects.create(user=self)

        # Handle FleetManager
        if self.is_fleet_manager:
            if not hasattr(self, 'fleetmanager_profile'):
                FleetManager.objects.create(user=self)

        # Handle Driver
        if self.is_driver:
            if not hasattr(self, 'driver_profile'):
                # Note: Driver creation requires additional fields
                # This is just a basic creation, you might want to handle this differently
                Driver.objects.create(
                    user=self,
                    license_number='TEMP_LICENSE',  # This should be updated later
                    license_expiry_date='2099-12-31',  # This should be updated later
                    driver_license_image=None  # This should be updated later
                )


class AdminUser(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='admin_profile')
    service_region = models.ForeignKey(
        Park, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_location')

    class Meta:
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'

    def __str__(self):
        return f"Admin: {self.user.email}"


class Agent(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='agent_profile')
    service_region = models.OneToOneField(
        Park, on_delete=models.SET_NULL, null=True, blank=True, related_name='agent_location')

    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'

    def __str__(self):
        return f"Agent: {self.user.email}"


class FleetManager(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='fleetmanager_profile')
    service_region = models.OneToOneField(
        Park, on_delete=models.SET_NULL, null=True, blank=True, related_name='fleetmanager_location')

    class Meta:
        verbose_name = 'Fleet Manager'
        verbose_name_plural = 'Fleet Managers'

    def __str__(self):
        return f"Fleet Manager: {self.user.email}"


class Driver(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='driver_profile')
    vehicle = models.OneToOneField(
        Vehicle, on_delete=models.CASCADE, related_name='drivers')
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry_date = models.DateField()
    is_available = models.BooleanField(default=True)
    total_trips = models.PositiveIntegerField(default=0)
    driver_license_image = models.ImageField(
        upload_to='drivers_licenses/')
    service_region = models.OneToOneField(
        Park, on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_location')

    class Meta:
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.vehicle.make} {self.vehicle.model}"


class DriverVerification(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    driver = models.OneToOneField(
        Driver, on_delete=models.CASCADE, related_name='verification')
    id_document = models.FileField(upload_to='driver_verification/id/')
    license_document = models.FileField(
        upload_to='driver_verification/license/')
    address_proof = models.FileField(
        upload_to='driver_verification/address/', null=True, blank=True)
    background_check_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    background_check_report = models.FileField(
        upload_to='verification/background/', null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Driver Verification'
        verbose_name_plural = 'Driver Verifications'

    def __str__(self):
        return f"Verification for {self.driver.user.get_full_name()}"


class EmergencyContact(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    relationship = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Emergency Contact'
        verbose_name_plural = 'Emergency Contacts'

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.phone_number}"


class Address(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='addresses')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', 'city']

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}, {self.postal_code}, {self.country}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other addresses of this user to non-default
            Address.objects.filter(user=self.user).exclude(
                pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
