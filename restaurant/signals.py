from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Booking)
def booking_status_email(sender, instance, **kwargs):
    # Make sure the email exists
    if not instance.email:
        return

    # Send email if booking is accepted
    if instance.status == 'accepted':
        send_mail(
            subject="Booking Accepted",
            message=f"Hello {instance.name}, your booking has been accepted!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False
        )

    # Send email if booking is rejected
    elif instance.status == 'rejected':
        send_mail(
            subject="Booking Rejected",
            message=f"Hello {instance.name}, we are sorry. Your booking has been rejected.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False
        )