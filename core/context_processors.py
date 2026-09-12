from django.conf import settings
from django.utils import timezone

from .models import WebsiteSettings, ContactSettings, AuditLog


def site_globals(request):
    ws = WebsiteSettings.get()
    cs = ContactSettings.get()
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False).count()
    nav_facilities = []
    from facilities.models import Facility

    nav_facilities = list(
        Facility.objects.filter(status="published").order_by("sort_order", "name")[:6]
    )
    nav_programme_categories = []
    from programmes.models import ProgrammeCategory

    nav_programme_categories = list(ProgrammeCategory.objects.filter(is_active=True))
    return {
        "site_settings": ws,
        "contact_settings": cs,
        "unread_notifications": unread_notifications,
        "nav_facilities": nav_facilities,
        "nav_programme_categories": nav_programme_categories,
        "now": timezone.now(),
    }


class AuditAccessLogMiddleware:
    """Log login/logout events at the request level."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.contrib.auth import signals
        from django.contrib.auth.models import User as DefaultUser

        response = self.get_response(request)
        return response


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if not settings.DEBUG:
            response["Strict-Transport-Security"] = "max-age=31536000"
        return response