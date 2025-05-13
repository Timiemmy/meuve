from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
from django.db import transaction
from .serializers import PaymentSerializer
from .models import Payment
from booking.models import Booking


paystack_secret_key = settings.PAYSTACK_SECRET_KEY


def initialize_transaction(email, amount, secret_key):
    """
    Initialize a Paystack transaction.

    Args:
        email (str): Customer's email address.
        amount (int or str): Amount in kobo (e.g., 20000 for ₦200).
        secret_key (str): Your Paystack secret key.

    Returns:
        dict: JSON response from Paystack API.
    """
    url = "https://api.paystack.co/transaction/initialize/"

    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "amount": str(amount),
        # "callback_url": f"{settings.FRONTEND_URL}/payment/verify",  # Add your frontend callback URL
        "metadata": {
            "custom_fields": [
                {
                    "display_name": "Payment For",
                    "variable_name": "payment_for",
                    "value": "Booking Payment",
                    "channel": "card",
                }
            ]
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return {
            'status': False,
            'message': f'HTTP error: {str(http_err)}'
        }
    except Exception as err:
        print(f"An error occurred: {err}")
        return {
            'status': False,
            'message': f'Error: {str(err)}'
        }


class PaymentCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Get the validated data
            payment = serializer.save(user=self.request.user)

            # Convert amount to kobo (multiply by 100)
            amount_in_kobo = int(float(payment.amount) * 100)

            # Initialize Paystack transaction
            response = initialize_transaction(
                email=self.request.user.email,
                amount=amount_in_kobo,
                secret_key=paystack_secret_key
            )

            if response and response.get('status'):
                # Update payment with reference from Paystack
                payment.reference = response['data']['reference']
                payment.save()

                # Return the authorization URL and other data
                return Response({
                    'status': True,
                    'message': 'Payment initialized successfully',
                    'data': {
                        'authorization_url': response['data']['authorization_url'],
                        'access_code': response['data']['access_code'],
                        'reference': response['data']['reference'],
                        'payment': self.get_serializer(payment).data
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': False,
                    'message': 'Failed to initialize payment',
                    'error': response.get('message', 'Unknown error occurred')
                }, status=status.HTTP_400_BAD_REQUEST)


def verify_transaction(reference, secret_key):
    """
    Verify a Paystack transaction by its reference.

    Args:
        reference (str): The transaction reference.
        secret_key (str): Your Paystack secret key.

    Returns:
        dict: JSON response from Paystack API if successful, else None.
    """
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {secret_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None


class VerifyPaymentView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    lookup_field = 'reference'

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    @transaction.atomic
    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()

        # Verify the transaction with Paystack
        response = verify_transaction(
            reference=payment.reference,
            secret_key=paystack_secret_key
        )

        if response and response.get('status'):
            # Check if transaction was successful
            if response['data']['status'] == 'success':
                # Update payment status
                payment.verified = True
                payment.save()

                # Update booking status
                booking = payment.booking_id
                booking.payment_status = 'confirmed'
                booking.is_paid = True
                booking.save()

                return Response({
                    'status': 'success',
                    'message': 'Payment verified successfully',
                    'data': {
                        'payment': self.get_serializer(payment).data,
                        # 'booking_status': booking.booking_status,
                        'payment_status': booking.payment_status
                    }
                })
            else:
                return Response({
                    'status': 'failed',
                    'message': 'Payment verification failed',
                    'data': response['data']
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'status': 'error',
            'message': 'Could not verify payment'
        }, status=status.HTTP_400_BAD_REQUEST)
