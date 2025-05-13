from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from park.models import Park


class ParkSerializer(serializers.ModelSerializer):
    """
    Serializer for the Park model.
    """
    class Meta:
        model = Park
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
