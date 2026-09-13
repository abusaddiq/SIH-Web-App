import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)


class WebsiteSettings(models.Model):
    """Single-row singleton (row with id=1)."""
    site_name = models.CharField(max_length=120, default="SPAK Innovation Hub")
    tagline = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to="branding/", blank=True)
    logo_alt = models.CharField(max_length=120, blank=True)
    favicon = models.ImageField(upload_to="branding/", blank=True)
    default_social_image = models.ImageField(upload_to="branding/", blank=True)
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    footer_text = models.CharField(max_length=300, blank=True)
    copyright = models.CharField(max_length=160, blank=True)
    programme_approval_required = models.BooleanField(default=False)
    content_staff_enabled = models.BooleanField(default=False)
    ai_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website settings"

    def __str__(self):
        return self.site_name

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactSettings(models.Model):
    """Single-row singleton (row with id=1) for contact information."""
    address = models.CharField(max_length=300, blank=True)
    address_map_link = models.CharField(max_length=500, blank=True)
    map_embed_html = models.TextField(blank=True)
    phone_1 = models.CharField(max_length=40, blank=True)
    phone_2 = models.CharField(max_length=40, blank=True)
    phone_3 = models.CharField(max_length=40, blank=True)
    email_1 = models.EmailField(blank=True)
    email_2 = models.EmailField(blank=True)
    whatsapp = models.CharField(max_length=40, blank=True)
    working_hours = models.CharField(max_length=200, blank=True)
    office_hours = models.CharField(max_length=200, blank=True)
    office_hours_closed = models.CharField(max_length=200, blank=True)
    coworking_hours = models.CharField(max_length=200, blank=True)
    coworking_hours_closed = models.CharField(max_length=200, blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    facebook = models.URLField(blank=True)
    twitter_x = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    contact_page_text = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contact settings"

    def __str__(self):
        return "Contact settings"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def socials(self):
        return [
            (k, getattr(self, k))
            for k in ("facebook", "twitter_x", "instagram", "linkedin", "youtube")
            if getattr(self, k)
        ]


class HomepageSection(models.Model):
    key = models.SlugField(max_length=80, unique=True)
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="homepage/", blank=True)
    cta_text = models.CharField(max_length=80, blank=True)
    cta_link = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "key"]
        verbose_name = "Homepage section"

    def __str__(self):
        return f"{self.key}: {self.title or '(untitled)'}"


class CmsPage(models.Model):
    """Editable static pages: About, Privacy Policy, Terms of Use, etc."""
    slug = models.SlugField(max_length=120, unique=True)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="pages/", blank=True)
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class MediaItem(models.Model):
    file = models.ImageField(upload_to="media/%Y/%m/")
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    file_size = models.PositiveIntegerField(default=0)
    mime = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.file.name


class AuditLog(models.Model):
    ACTIONS = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("approve", "Approve"),
        ("reject", "Reject"),
        ("cancel", "Cancel"),
        ("publish", "Publish"),
        ("unpublish", "Unpublish"),
        ("archive", "Archive"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("other", "Other"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    action = models.CharField(max_length=20, choices=ACTIONS, default="other")
    entity_type = models.CharField(max_length=120, blank=True)
    entity_id = models.CharField(max_length=80, blank=True)
    previous_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at} {self.user or 'anon'} {self.action} {self.entity_type}"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=200)
    body = models.CharField(max_length=500, blank=True)
    entity_type = models.CharField(max_length=120, blank=True)
    entity_id = models.CharField(max_length=80, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


def create_notification(recipient, title, body="", entity_type="", entity_id=""):
    if not recipient:
        return
    Notification.objects.create(
        recipient=recipient, title=title, body=body, entity_type=entity_type, entity_id=entity_id
    )


def audit_log(request, action, entity_type, entity_id="", previous=None, new=None, description=""):
    """Write an audit-log entry, anonymising IP defensively."""
    ip = None
    if request and request.META.get("REMOTE_ADDR"):
        ip = request.META.get("REMOTE_ADDR", "")[:45]
    user = request.user if request and hasattr(request, "user") and request.user.is_authenticated else None
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id or "")[:80],
            previous_value=previous,
            new_value=new,
            ip_address=ip,
            description=description[:500],
        )
    except Exception:  # pragma: no cover - audit must never break the app
        logger.exception("Failed to write audit log")


def stable_digest(value):
    return hmac.new(settings.SECRET_KEY.encode(), str(value).encode(), hashlib.sha256).hexdigest()[:32]