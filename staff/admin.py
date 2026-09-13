from django.contrib import admin

from .models import StaffMember


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "profession", "department", "is_active", "display_order")
    list_filter = ("is_active", "department")
    search_fields = ("full_name", "role", "email", "profession")
    ordering = ("display_order", "full_name")