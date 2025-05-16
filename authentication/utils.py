import random
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import EmailVerificationCode


def generate_verification_code():
    return f"{random.randint(100000, 999999)}"


def send_verification_email(user):
    code = generate_verification_code()
    EmailVerificationCode.objects.create(user=user, code=code)

    # HTML email template
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4a90e2;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #ffffff;
                padding: 20px;
                border: 1px solid #dddddd;
                border-radius: 0 0 5px 5px;
            }}
            .verification-code {{
                background-color: #f5f5f5;
                padding: 15px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                color: #4a90e2;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                color: #666666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Email Verification</h1>
            </div>
            <div class="content">
                <p>Hello {user.username},</p>
                <p>Thank you for registering. Please use the following verification code to complete your registration:</p>
                <div class="verification-code">
                    {code}
                </div>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this verification code, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Create plain text version for email clients that don't support HTML
    plain_message = strip_tags(html_message)

    # Send the email
    send_mail(
        subject='Email Verification Code',
        message=plain_message,
        from_email='hello@meuve.com',
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
