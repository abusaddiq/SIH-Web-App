from django.contrib import admin

from .models import (
    FacilityCategory,
    Facility,
    FacilityPrice,
    Service,
    Booking,
    Enquiry,
)


class FacilityPriceInline(admin.TabularInline):
    model = FacilityPrice
    extra = 0


@admin.register(FacilityCategory)
class FacilityCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "sort_order")
    list_filter = ("is_active",)


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "capacity", "status", "is_featured", "updated_at")
    list_filter = ("status", "category", "is_featured")
    search_fields = ("name", "description")
    inlines = [FacilityPriceInline]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(FacilityPrice)
class FacilityPriceAdmin(admin.ModelAdmin):
    list_display = ("facility", "price_type", "amount", "currency", "is_active", "effective_date")
    list_filter = ("price_type", "is_active", "currency")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "is_featured", "sort_order", "price_text")
    list_filter = ("is_published", "is_featured")
    search_fields = ("name", "short_description")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("ref_no", "full_name", "facility", "preferred_date", "status", "submitted_at")
    list_filter = ("status", "submitted_at")
    search_fields = ("ref_no", "full_name", "email", "organization")
    readonly_fields = ("ref_no", "submitted_at")


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("ref_no", "name", "subject", "source", "status", "created_at")
    list_filter = ("status", "source", "created_at")
    search_fields = ("ref_no", "name", "email", "subject", "message", "phone")
    readonly_fields = ("ref_no", "created_at")