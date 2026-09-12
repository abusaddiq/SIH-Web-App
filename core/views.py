from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from blog.models import Post
from facilities.models import Booking, Enquiry, Facility
from programmes.models import Programme

from .access import super_admin_required
from .forms import (
    WebsiteSettingsForm,
    ContactSettingsForm,
    HomepageSectionForm,
    MediaUploadForm,
    MediaEditForm,
    MediaReplaceForm,
)
from .models import (
    WebsiteSettings,
    ContactSettings,
    HomepageSection,
    MediaItem,
    AuditLog,
    Notification,
)

def admin_dashboard_view(request):
    if not request.user.is_authenticated or not request.user.is_super_admin:
        return redirect("login")
    today = timezone.localdate()
    ctx = {
        "facilities_total": Facility.objects.count(),
        "facilities_published": Facility.objects.filter(status="published").count(),
        "programmes_total": Programme.objects.exclude(status__in=["archived"]).count(),
        "upcoming_programmes": Programme.objects.filter(status="published", start_date__gte=today).count(),
        "pending_bookings": Booking.objects.filter(status="pending").count(),
        "under_review_bookings": Booking.objects.filter(status="under_review").count(),
        "approved_bookings": Booking.objects.filter(status="approved").count(),
        "new_enquiries": Enquiry.objects.filter(status="new").count(),
        "recent_enquiries": Enquiry.objects.filter(status__in=["new", "read"])[:6],
        "recent_bookings": Booking.objects.filter(status__in=["pending", "under_review"])[:6],
        "recent_programmes_submitted": Programme.objects.filter(status="submitted")[:6],
        "recent_blog": Post.objects.all()[:6],
        "blog_posts_published": Post.objects.filter(status="published").count(),
        "blog_posts_drafts": Post.objects.filter(status="draft").count(),
        "recent_audit": AuditLog.objects.all()[:8],
        "active_users": None,
    }
    return render(request, "admin_shell/dashboard.html", ctx)


@super_admin_required
def site_settings_view(request):
    obj = WebsiteSettings.get()
    form = WebsiteSettingsForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        before = {"site_name": obj.site_name, "programme_approval_required": obj.programme_approval_required}
        form.save()
        from .models import audit_log

        audit_log(
            request, "update", "website_settings", obj.pk,
            previous=before, new={"site_name": obj.site_name}, description="Updated website/branding settings",
        )
        messages.success(request, "Website settings updated.")
        return redirect("core-site-settings")
    return render(request, "admin_shell/settings_site.html", {"form": form, "obj": obj})


@super_admin_required
def contact_settings_view(request):
    obj = ContactSettings.get()
    form = ContactSettingsForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        before = {"phone_1": obj.phone_1, "email_1": obj.email_1, "address": obj.address}
        form.save()
        from .models import audit_log

        audit_log(
            request, "update", "contact_settings", obj.pk,
            previous=before, new={"phone_1": obj.phone_1}, description="Updated contact information",
        )
        messages.success(request, "Contact settings updated.")
        return redirect("core-contact-settings")
    return render(request, "admin_shell/settings_contact.html", {"form": form, "obj": obj})


@super_admin_required
def homepage_sections_view(request):
    sections = HomepageSection.objects.all()
    return render(request, "admin_shell/settings_homepage.html", {"sections": sections})


@super_admin_required
def homepage_section_detail_view(request, slug):
    obj = get_object_or_404(HomepageSection, key=slug)
    form = HomepageSectionForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        from .models import audit_log

        audit_log(request, "update", "homepage_section", obj.key, description=f"Edited homepage section '{obj.key}'")
        messages.success(request, "Section updated.")
        return redirect("core-homepage-sections")
    return render(request, "admin_shell/settings_homepage_edit.html", {"form": form, "obj": obj})


@super_admin_required
def media_library_view(request):
    media = MediaItem.objects.all()
    upload_form = MediaUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and upload_form.is_valid():
        item = upload_form.save(commit=False)
        item.uploaded_by = request.user
        if item.file:
            item.file_size = item.file.size
        item.save()
        messages.success(request, "File uploaded.")
        return redirect("core-media")
    return render(request, "admin_shell/media.html", {"media": media, "upload_form": upload_form})


@super_admin_required
def media_delete_view(request, pk):
    if request.method == "POST":
        item = get_object_or_404(MediaItem, pk=pk)
        from .models import audit_log

        audit_log(request, "delete", "media", pk, description=f"Deleted media {item.file.name}")
        item.file.delete(save=False)
        item.delete()
        messages.success(request, "File deleted.")
    return redirect("core-media")


@super_admin_required
def media_edit_view(request, pk):
    item = get_object_or_404(MediaItem, pk=pk)
    form = MediaEditForm(request.POST or None, instance=item)
    replace_form = MediaReplaceForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if "save_alt" in request.POST and form.is_valid():
            form.save()
            messages.success(request, "Alt text updated.")
            return redirect("core-media")
        if "replace_file" in request.POST and replace_form.is_valid():
            item.file = replace_form.cleaned_data["file"]
            item.file_size = item.file.size
            item.save()
            messages.success(request, "File replaced.")
            return redirect("core-media")
    return render(
        request, "admin_shell/media_edit.html",
        {"item": item, "form": form, "replace_form": replace_form},
    )


@super_admin_required
def audit_logs_view(request):
    qs = AuditLog.objects.all()
    action = request.GET.get("action")
    q = request.GET.get("q")
    if action:
        qs = qs.filter(action=action)
    if q:
        qs = qs.filter(Q(entity_type__icontains=q) | Q(description__icontains=q) | Q(entity_id__icontains=q))
    logs = qs[:200]
    return render(request, "admin_shell/audit_logs.html", {"logs": logs, "actions": AuditLog.ACTIONS})


@super_admin_required
def notifications_view(request):
    qs = (request.user.notifications if request.user.is_authenticated else Notification.objects.none()).all()
    qs = qs[:100]
    return render(request, "admin_shell/notifications.html", {"notifications": qs})


@super_admin_required
def notifications_mark_read(request, pk):
    if request.method == "POST":
        Notification.objects.filter(pk=pk, recipient=request.user).update(is_read=True)
    return redirect("core-notifications")


@super_admin_required
def notifications_mark_all(request):
    if request.method == "POST":
        request.user.notifications.update(is_read=True)
    return redirect("core-notifications")