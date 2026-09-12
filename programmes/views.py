from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from blog.models import Post
from core.access import programme_lead_required, super_admin_required
from core.models import audit_log, WebsiteSettings
from core.services import notify_admins, notify_user

from .forms import (
    ProgrammeForm,
    ProgrammeCategoryForm,
    PersonForm,
    ProgrammeRegistrationForm,
    ProgrammeEnquiryForm,
    ProgrammeStatusForm,
    ProgrammeReplyForm,
)
from .models import (
    ProgrammeCategory,
    Person,
    Programme,
    ProgrammeRegistration,
    ProgrammeEnquiry,
)


@programme_lead_required
def dashboard(request):
    today = timezone.localdate()
    mine = Programme.objects.filter(created_by=request.user)
    ctx = {
        "my_programmes_total": mine.exclude(status="archived").count(),
        "drafts": mine.filter(status="draft").count(),
        "submitted": mine.filter(status="submitted").count(),
        "published": mine.filter(status="published").count(),
        "upcoming": mine.filter(status="published", start_date__gte=today).count(),
        "past": mine.filter(status="published", end_date__lt=today).count(),
        "recent": mine.exclude(status="archived").order_by("-updated_at")[:8],
        "registrations": ProgrammeRegistration.objects.filter(programme__created_by=request.user).count(),
        "pending_registrations": ProgrammeRegistration.objects.filter(
            programme__created_by=request.user, status="pending"
        ).count(),
        "enquiries": ProgrammeEnquiry.objects.filter(programme__created_by=request.user).count(),
        "requires_approval": WebsiteSettings.get().programme_approval_required,
    }
    return render(request, "programmes_dash/dashboard.html", ctx)


@programme_lead_required
def programme_list(request):
    q = request.GET.get("q", "").strip()
    mine = Programme.objects.filter(created_by=request.user)
    if q:
        mine = mine.filter(Q(title__icontains=q) | Q(category__name__icontains=q) | Q(venue__icontains=q))
    return render(request, "programmes_dash/programmes_list.html", {"programmes": mine})


@programme_lead_required
def programme_create(request):
    form = ProgrammeForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        p = form.save(commit=False)
        p.created_by = request.user
        if request.POST.get("action") == "submit":
            p.status = "submitted"
        else:
            p.status = "draft"
        p.save()
        form.save_m2m()
        audit_log(request, "create", "programme", p.pk, new={"title": p.title, "status": p.status}, description=f"Programme Lead created '{p.title}'")
        if p.status == "submitted":
            notify_admins("Programme submitted for review", f"'{p.title}' by {request.user}")
        messages.success(request, "Programme saved.")
        return redirect("prog-dash-programme-edit", pk=p.pk)
    return render(request, "programmes_dash/programme_form.html", {"form": form, "title": "Create New Programme", "programme": None, "requires_approval": WebsiteSettings.get().programme_approval_required})


@programme_lead_required
def programme_edit(request, pk):
    p = get_object_or_404(Programme, pk=pk)
    if p.created_by_id not in (request.user.pk,) and not request.user.is_super_admin:
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("You can only edit programmes you created.")
    form = ProgrammeForm(request.POST or None, request.FILES or None, instance=p)
    if request.method == "POST" and form.is_valid():
        action = request.POST.get("action")
        if action == "submit":
            p.status = "submitted"
            notify_admins("Programme submitted for review", f"'{p.title}' by {request.user}")
            messages.success(request, "Submitted for review.")
        elif action == "archive":
            p.status = "archived"
        elif action == "cancel":
            p.status = "cancelled"
        elif action == "draft":
            p.status = "draft"
        form.save()
        # form.save(commit=True) already persisted trainers/facilitators/speakers
        audit_log(request, "update", "programme", p.pk, new={"title": p.title, "status": p.status}, description=f"Updated programme '{p.title}' -> {p.status}")
        return redirect("prog-dash-programme-edit", pk=p.pk)
    return render(
        request, "programmes_dash/programme_form.html",
        {"form": form, "title": f"Edit {p.title}", "programme": p, "requires_approval": WebsiteSettings.get().programme_approval_required},
    )


@programme_lead_required
def registrations(request):
    qs = ProgrammeRegistration.objects.filter(programme__created_by=request.user)
    if not request.user.is_super_admin:
        qs = qs.filter(programme__created_by=request.user)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    return render(request, "programmes_dash/registrations.html", {"registrations": qs, "status": status, "statuses": ProgrammeRegistration.STATUS_CHOICES})


@programme_lead_required
def registration_update(request, pk):
    r = get_object_or_404(ProgrammeRegistration, pk=pk)
    if r.programme.created_by_id != request.user.pk and not request.user.is_super_admin:
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied
    if request.method == "POST":
        status = request.POST.get("status")
        if status in dict(ProgrammeRegistration.STATUS_CHOICES):
            old = r.status
            r.status = status
            r.save(update_fields=["status"])
            audit_log(request, "update", "programme_registration", r.ref_no, previous={"status": old}, new={"status": r.status}, description=f"Registration {r.ref_no} -> {r.status}")
            messages.success(request, "Registration updated.")
    return redirect("prog-dash-registrations")


@programme_lead_required
def enquiries(request):
    qs = ProgrammeEnquiry.objects.filter(programme__created_by=request.user)
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    return render(request, "programmes_dash/programme_enquiries.html", {"enquiries": qs, "status": status, "statuses": ProgrammeEnquiry.STATUS_CHOICES})


@programme_lead_required
def enquiry_detail(request, pk):
    e = get_object_or_404(ProgrammeEnquiry, pk=pk)
    if e.programme.created_by_id != request.user.pk and not request.user.is_super_admin:
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied
    form = ProgrammeReplyForm(request.POST or None, initial={"status": e.status, "admin_reply": e.admin_reply})
    if request.method == "POST" and form.is_valid():
        e.status = form.cleaned_data["status"]
        e.admin_reply = form.cleaned_data["admin_reply"]
        e.replied_at = timezone.now()
        e.save(update_fields=["status", "admin_reply", "replied_at"])
        audit_log(request, "update", "programme_enquiry", e.ref_no, new={"status": e.status}, description=f"Replied to programme enquiry {e.ref_no}")
        messages.success(request, "Enquiry updated.")
        return redirect("prog-dash-enquiry-detail", pk=e.pk)
    return render(request, "programmes_dash/enquiry_detail.html", {"enquiry": e, "form": form})


@programme_lead_required
def trainers(request):
    qs = Person.objects.all()
    return render(request, "programmes_dash/trainers.html", {"people": qs})


@programme_lead_required
def trainer_create(request):
    form = PersonForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        audit_log(request, "create", "person", None, new={"name": form.cleaned_data["name"]}, description=f"Added trainer/facilitator/speaker")
        messages.success(request, "Person added.")
        return redirect("prog-dash-trainers")
    return render(request, "programmes_dash/person_form.html", {"form": form, "title": "Add Trainer / Facilitator / Speaker"})


@programme_lead_required
def trainer_edit(request, pk):
    person = get_object_or_404(Person, pk=pk)
    form = PersonForm(request.POST or None, request.FILES or None, instance=person)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Person updated.")
        return redirect("prog-dash-trainers")
    return render(request, "programmes_dash/person_form.html", {"form": form, "title": f"Edit {person.name}"})


@programme_lead_required
def trainer_delete(request, pk):
    if request.method == "POST":
        Person.objects.filter(pk=pk).delete()
        messages.success(request, "Person removed.")
    return redirect("prog-dash-trainers")


@programme_lead_required
def categories(request):
    cats = ProgrammeCategory.objects.all()
    form = ProgrammeCategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category added.")
        return redirect("prog-dash-categories")
    return render(request, "programmes_dash/categories.html", {"categories": cats, "form": form})


@super_admin_required
def admin_programmes(request):
    qs = Programme.objects.select_related("category", "created_by").all()
    status = request.GET.get("status", "")
    q = request.GET.get("q", "").strip()
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(venue__icontains=q))
    return render(
        request, "admin_shell/programmes/list.html",
        {"programmes": qs, "status": status, "statuses": Programme.STATUS_CHOICES},
    )


@super_admin_required
def admin_programme_detail(request, pk):
    p = get_object_or_404(Programme, pk=pk)
    form = ProgrammeStatusForm(request.POST or None, initial={"status": p.status})
    if request.method == "POST" and form.is_valid():
        old = p.status
        p.status = form.cleaned_data["status"]
        if p.status == "published" and old != "published":
            p.published_at = timezone.now()
            p.approved_by = request.user
            if p.created_by_id:
                notify_user(p.created_by, "Programme approved", f"'{p.title}' has been approved and published.")
        p.save()
        audit_log(request, "update", "programme", p.pk, previous={"status": old}, new={"status": p.status}, description=f"Admin set programme '{p.title}' to {p.status}")
        if p.created_by_id:
            notify_user(
                p.created_by,
                f"Programme '{p.title}' status changed",
                f"New status: {p.get_status_display()}.",
            )
        messages.success(request, "Programme status updated.")
        return redirect("prog-admin-detail", pk=p.pk)
    return render(request, "admin_shell/programmes/detail.html", {"programme": p, "form": form})


# ---------------------------------------------------------------------------
# Public programme views
# ---------------------------------------------------------------------------
def public_programmes(request):
    today = timezone.localdate()
    qs = Programme.objects.filter(status="published", published_at__lte=timezone.now())
    category = request.GET.get("category", "")
    if category:
        qs = qs.filter(category__slug=category)
    upcoming = qs.filter(start_date__gte=today).order_by("start_date")
    ongoing = qs.filter(start_date__lte=today, end_date__gte=today).order_by("start_date")
    past = qs.filter(end_date__lt=today).order_by("-end_date")
    return render(
        request, "public/programmes/list.html",
        {
            "upcoming": upcoming,
            "ongoing": ongoing,
            "past": past,
            "categories": ProgrammeCategory.objects.filter(is_active=True),
            "category_slug": category,
        },
    )


def public_programme_detail(request, slug):
    p = get_object_or_404(Programme, slug=slug, status="published", published_at__lte=timezone.now())

    reg_form = ProgrammeRegistrationForm(request.POST or None, prefix="reg") if p.requires_registration else None
    enq_form = ProgrammeEnquiryForm(request.POST or None, prefix="enq")
    if request.method == "POST":
        if "register" in request.POST and reg_form and reg_form.is_valid():
            r = reg_form.save(commit=False)
            r.programme = p
            r.save()
            audit_log(request, "create", "programme_registration", r.ref_no, description=f"Public registration {r.ref_no} for '{p.title}'")
            notify_admins("New programme registration", f"{r.full_name} registered for '{p.title}'")
            messages.success(request, "Registration received. You will be contacted upon confirmation.")
            return redirect("public-programme-detail", slug=p.slug)
        if "enquire" in request.POST and enq_form.is_valid():
            e = enq_form.save(commit=False)
            e.programme = p
            e.save()
            audit_log(request, "create", "programme_enquiry", e.ref_no, description=f"Programme enquiry {e.ref_no} for '{p.title}'")
            notify_admins("New programme enquiry", f"{e.name} enquired about '{p.title}'")
            messages.success(request, "Enquiry sent. SPAK will respond shortly.")
            return redirect("public-programme-detail", slug=p.slug)
    return render(
        request, "public/programmes/detail.html",
        {"programme": p, "reg_form": reg_form, "enq_form": enq_form},
    )


def public_training(request):
    today = timezone.localdate()
    qs = Programme.objects.filter(status="published", category__slug__in=["training", "workshop", "bootcamp", "seminar", "clinic"])
    return render(request, "public/programmes/training.html", {"programmes": qs, "today": today})