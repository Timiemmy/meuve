from rest_framework import serializers
from useraccount import models



class AddressSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = models.Address
        fields = '__all__'
        read_only_fields = ['id', 'user']



class EmergencyContactSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = models.EmergencyContact
        fields = '__all__'
        read_only_fields = ['id', 'user']

class CustomUserSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()

    class Meta:
        model = models.CustomUser
        fields = '__all__'
        extra_kwargs = {
            'is_staff': {'read_only': True},
            'is_active': {'read_only': True},
        }
        read_only_fields = ['id', 'date_joined']

    def get_address(self, obj):
        try:
            address = models.Address.objects.get(user=obj)
            return AddressSerializer(address, context=self.context).data
        except models.Address.DoesNotExist:
            return None


class DriverSerializer(serializers.ModelSerializer):
    vehicle_name = serializers.CharField(source='vehicle.name', read_only=True)
    vehicle_model = serializers.CharField(source='vehicle.model', read_only=True)
    driver_name = serializers.SerializerMethodField()
    class Meta:
        model = models.Driver
        fields = [
            'id', 'driver_email', 'driver_name', 'vehicle', 'vehicle_name', 'vehicle_model', 'license_number',
            'license_expiry_date', 'is_available', 'total_trips',
            'driver_license_image'
        ]

    def get_driver_name(self, obj):
        return obj.user.get_full_name() if obj.user else None


class DriverVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DriverVerification
        fields = [
            'id', 'driver', 'driver_name', 'id_document',
            'license_document', 'address_proof', 'background_check_status',
            'background_check_report', 'verification_notes', 'verified_at',
            'verified_by', 'verified_by_id', 'rejection_reason'
        ]


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdminUser
        fields = '__all__'


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Agent
        fields = '__all__'


class FleetManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FleetManager
        fields = '__all__'