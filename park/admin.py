from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Park


@admin.register(Park)
class ParkAdminClass(ModelAdmin):
    list_display = ('name',
                    'code', 'address', 'is_active')
    search_fields = ['code', 'name']
    list_filter = ['is_active']