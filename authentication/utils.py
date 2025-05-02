import random
from django.core.mail import send_mail
from .models import EmailVerificationCode


def generate_verification_code():
    return f"{random.randint(100000, 999999)}"


def send_verification_email(user):
    code = generate_verification_code()
    EmailVerificationCode.objects.create(user=user, code=code)
    send_mail(
        subject='Your Email Verification Code',
        message=f'Your verification code is {code}',
        from_email='no-reply@yourapp.com',
        recipient_list=[user.email],
        fail_silently=False,
    )
