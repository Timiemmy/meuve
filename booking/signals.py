from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Booking


@receiver(post_save, sender=Booking)
def send_booking_confirmation_email(sender, instance, created, **kwargs):
    """
    Send email when a new booking is created
    """
    if created:
        subject = f'Booking Confirmation - {instance.booking_code}'
        html_message = render_to_string('booking/email/booking_confirmation.html', {
            'booking': instance,
            'user': instance.passenger,
        })
        
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.passenger.email],
            html_message=html_message,
            fail_silently=False,
        )


@receiver(pre_save, sender=Booking)
def send_booking_update_email(sender, instance, **kwargs):
    """
    Send email when a booking is updated (check-in, check-out, or general updates)
    """
    if instance.pk:  # Only for existing bookings
        old_instance = Booking.objects.get(pk=instance.pk)

        # Check if booking was checked in
        if instance.is_checked_in and not old_instance.is_checked_in:
            subject = f'Booking Check-in Confirmation - {instance.booking_code}'
            html_message = render_to_string('booking/email/booking_checkin.html', {
                'booking': instance,
                'user': instance.passenger,
            })
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.passenger.email],
                html_message=html_message,
                fail_silently=False,
            )

        # Check if booking was checked out
        elif instance.is_checked_out and not old_instance.is_checked_out:
            subject = f'Booking Check-out Confirmation - {instance.booking_code}'
            html_message = render_to_string('booking/email/booking_checkout.html', {
                'booking': instance,
                'user': instance.passenger,
            })
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.passenger.email],
                html_message=html_message,
                fail_silently=False,
            )

        # Handle general updates (excluding check-in/check-out)
        elif not (instance.is_checked_in != old_instance.is_checked_in or
                  instance.is_checked_out != old_instance.is_checked_out or
                  instance.cancellation_time != old_instance.cancellation_time):
            # Get changed fields
            changed_fields = []
            for field in ['pickup_address', 'special_requests', 'adult_count',
                          'children_count', 'return_adult_count', 'return_children_count',
                          'luggage_count', 'travel_date', 'return_date']:
                if getattr(instance, field) != getattr(old_instance, field):
                    changed_fields.append(field)

            if changed_fields:  # Only send if there are actual changes
                subject = f'Booking Update - {instance.booking_code}'
                html_message = render_to_string('booking/email/booking_update.html', {
                    'booking': instance,
                    'user': instance.passenger,
                    'old_booking': old_instance,
                    'changed_fields': changed_fields,
                })
                plain_message = strip_tags(html_message)

                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.passenger.email],
                    html_message=html_message,
                    fail_silently=False,
                )


@receiver(pre_save, sender=Booking)
def send_booking_cancellation_email(sender, instance, **kwargs):
    """
    Send email when a booking is cancelled
    """
    if instance.pk:  # Only for existing bookings
        old_instance = Booking.objects.get(pk=instance.pk)

        # Check if booking was cancelled
        if instance.cancellation_time and not old_instance.cancellation_time:
            subject = f'Booking Cancellation - {instance.booking_code}'
            html_message = render_to_string('booking/email/booking_cancellation.html', {
                'booking': instance,
                'user': instance.passenger,
            })
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.passenger.email],
                html_message=html_message,
                fail_silently=False,
            )
