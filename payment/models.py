from django.db import models
from booking.models import Booking
from useraccount.models import CustomUser
# Create your models here.

class Payment(models.Model):
    booking_id = models.OneToOneField(Booking, on_delete = models.PROTECT)
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'


    def __str__(self):
        return f'{self.booking_id} - {self.user} - {self.verified}'
    
    