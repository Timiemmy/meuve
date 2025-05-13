from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Payment


@admin.register(Payment)
class ParkAdminClass(ModelAdmin):
    list_display = ('booking_id',
                    'user', 'verified', 'created_at')
    search_fields = ['booking_id', 'user']
    list_filter = ['verified']
