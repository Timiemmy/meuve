from django.contrib import admin
from django import forms
from unfold.admin import ModelAdmin
from .models import Vehicle, VehicleImage, VehicleType, Amenity


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1  # Number of empty forms to display


@admin.register(Vehicle)
class VehicleAdminClass(ModelAdmin):
    inlines = [VehicleImageInline]
    list_display = ['name', 'model', 'year', 'license_plate']
    list_filter = ['is_available', 'category']
    search_fields = ['name', 'model', 'license_plate', 'vin']


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class VehicleImageAdminForm(forms.ModelForm):
    additional_images = MultipleFileField(
        required=False,
        help_text='Upload multiple images at once'
    )

    class Meta:
        model = VehicleImage
        fields = '__all__'


@admin.register(VehicleImage)
class VehicleImageAdminClass(ModelAdmin):
    form = VehicleImageAdminForm
    list_display = ['vehicle', 'caption']
    list_filter = ['vehicle']
    search_fields = ['vehicle__name', 'vehicle__model', 'caption']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Handle additional images
        files = request.FILES.getlist('additional_images')
        for file in files:
            VehicleImage.objects.create(
                vehicle=obj.vehicle,
                image=file,
                caption=obj.caption
            )


@admin.register(VehicleType)
class VehicleTypeAdminClass(ModelAdmin):
    pass


@admin.register(Amenity)
class AmenityAdminClass(ModelAdmin):
    pass
