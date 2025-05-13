from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Booking


@admin.register(Booking)
class BookingAdminClass(ModelAdmin):
    list_display = ('passenger__email',
                    'booking_date', 'payment_status', 'trip_type')
    search_fields = ['booking_date', 'trip_type']
    list_filter = ['payment_status', 'trip_type']
