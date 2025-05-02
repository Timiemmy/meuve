from rest_framework import serializers
from vehicle.models import Vehicle, VehicleImage, Amenity, VehicleType, VehicleStatus


class VehicleAmenitySerializer(serializers.ModelSerializer):
    """Serializer for Vehicle Amenity"""
    class Meta:
        model = Amenity
        fields = '__all__'


class VehicleTypeSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle Type"""
    class Meta:
        model = VehicleType
        fields = '__all__'


class VehicleImageSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle Image"""
    class Meta:
        model = VehicleImage
        fields = '__all__'


class VehicleStatusSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle Status"""
    class Meta:
        model = VehicleStatus
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle"""
    images = VehicleImageSerializer(many=True, required=False)
    amenities = VehicleAmenitySerializer(many=True, required=False)
    category = VehicleTypeSerializer(many=True, read_only=True)
    driver_name = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_available', 'is_booked')


    def get_driver_name(self, obj):
            # Use the related_name 'drivers' to get the driver
        driver = getattr(obj, 'drivers', None)
        if driver:
            return driver.user.get_full_name()
        return None

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        amenities_data = validated_data.pop('amenities', [])
        vehicle = Vehicle.objects.create(**validated_data)

        for image_data in images_data:
            VehicleImage.objects.create(vehicle=vehicle, **image_data)

        for amenity_data in amenities_data:
            Amenity.objects.create(vehicle=vehicle, **amenity_data)

        return vehicle