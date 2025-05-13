from rest_framework import serializers
from payment.models import Payment
from booking.models import Booking


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'booking_id', 'amount',
                  'reference', 'verified', 'created_at']
        read_only_fields = ['id', 'reference', 'verified', 'created_at']

    def validate(self, data):
        """
        Validate payment data
        """
        # Check if booking exists and belongs to user
        booking = data.get('booking_id')
        if not booking:
            raise serializers.ValidationError("Booking is required")

        if booking.passenger != self.context['request'].user:
            raise serializers.ValidationError(
                "You can only pay for your own bookings")

        # Check if booking is already paid
        if booking.is_paid:
            raise serializers.ValidationError(
                "This booking has already been paid for")

        # Check if amount matches booking amount
        if float(data.get('amount', 0)) != float(booking.amount):
            raise serializers.ValidationError(
                "Payment amount must match booking amount")

        return data
