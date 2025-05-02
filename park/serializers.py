from rest_framework import serializers
from park.models import Park


class ParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Park
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']