from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from notices.models import Notification


def notify_user(user, message, link=""):
    Notification.objects.create(user=user, message=message, link=link)


def email_user(subject, body, recipient):
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
    except Exception:
        pass


def notify_complaint_status(complaint):
    link = reverse("complaint_detail", args=[complaint.pk])
    message = f"{complaint.code} status changed to {complaint.get_status_display()}."
    notify_user(complaint.resident, message, link)
    email_user("Complaint status updated", f"{message}\n\nOpen the tracker to view notes and history.", complaint.resident.email)
