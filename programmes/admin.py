from django.contrib import admin

from .models import (
    ProgrammeCategory,
    Person,
    Programme,
    ProgrammeRegistration,
    ProgrammeEnquiry,
)


@admin.register(ProgrammeCategory)
class ProgrammeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "sort_order")
    list_filter = ("is_active",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "kind", "email")
    list_filter = ("kind",)
    search_fields = ("name", "title", "bio")


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "start_date", "programme_type", "created_by")
    list_filter = ("status", "category", "programme_type")
    search_fields = ("title", "short_description", "venue")
    readonly_fields = ("created_at", "updated_at", "published_at")
    filter_horizontal = ("trainers", "facilitators", "speakers")


@admin.register(ProgrammeRegistration)
class ProgrammeRegistrationAdmin(admin.ModelAdmin):
    list_display = ("ref_no", "programme", "full_name", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("ref_no", "full_name", "email", "organization")


@admin.register(ProgrammeEnquiry)
class ProgrammeEnquiryAdmin(admin.ModelAdmin):
    list_display = ("ref_no", "programme", "name", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("ref_no", "name", "email", "message")