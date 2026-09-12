from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Notification, WebsiteSettings


def notify_admins(title, body="", entity_type="", entity_id=""):
    """Create in-app notifications for all active Super Admins."""
    from accounts.models import User, ROLE_SUPER_ADMIN

    for admin in User.objects.filter(role=ROLE_SUPER_ADMIN, is_active=True):
        Notification.objects.create(
            recipient=admin, title=title, body=body, entity_type=entity_type, entity_id=str(entity_id)
        )
    send_notification_email(title, body)


def notify_user(user, title, body="", entity_type="", entity_id=""):
    if not user:
        return
    Notification.objects.create(
        recipient=user, title=title, body=body, entity_type=entity_type, entity_id=str(entity_id)
    )


def send_notification_email(subject, body):
    """Email channel (stub). Enabled via NOTIFICATION_EMAIL_ENABLED."""
    if not settings.NOTIFICATION_EMAIL_ENABLED:
        return
    try:
        ws = WebsiteSettings.get()
        send_mail(
            f"[{ws.site_name}] {subject}",
            body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )
    except Exception:
        # Notification email must never break the request flow.
        pass