# views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import EmailVerificationCode
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

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
