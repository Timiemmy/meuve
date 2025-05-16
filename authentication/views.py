# views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import EmailVerificationCode
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from .utils import send_verification_email
from django.utils import timezone

User = get_user_model()


class VerifyEmailCodeView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        code = request.data.get('code')
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
            record = EmailVerificationCode.objects.filter(
                user=user, code=code, is_used=False).last()
            if not record:
                return Response({'detail': 'Invalid code.'}, status=status.HTTP_400_BAD_REQUEST)
            if record.is_expired():
                return Response({'detail': 'Code expired.'}, status=status.HTTP_400_BAD_REQUEST)

            # Verify email in allauth system
            email_address = EmailAddress.objects.get_for_user(user, email)
            email_address.verified = True
            email_address.save()

            user.is_active = True
            user.save()
            record.is_used = True
            record.save()

            return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
        except EmailAddress.DoesNotExist:
            return Response({'detail': 'Email address not found.'}, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)

            # Check if there's a recent verification code (within last 1 minute)
            recent_code = EmailVerificationCode.objects.filter(
                user=user,
                created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
            ).first()

            if recent_code:
                return Response(
                    {'detail': 'Please wait at least 1 minute before requesting a new code.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Send new verification email
            send_verification_email(user)

            return Response(
                {'detail': 'Verification code has been resent.'},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
