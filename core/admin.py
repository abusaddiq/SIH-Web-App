from django.contrib import admin

from .models import (
    WebsiteSettings,
    ContactSettings,
    HomepageSection,
    MediaItem,
    AuditLog,
    Notification,
)


@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactSettings)
class ContactSettingsAdmin(admin.ModelAdmin):
    pass


@admin.register(HomepageSection)
class HomepageSectionAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ("file", "alt_text", "uploaded_by", "created_at")
    search_fields = ("alt_text", "caption")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "entity_type", "entity_id", "ip_address")
    list_filter = ("action", "entity_type", "created_at")
    search_fields = ("entity_type", "entity_id", "description")
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    date_hierarchy = "created_at"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "title", "is_read", "created_at")
    list_filter = ("is_read", "created_at")