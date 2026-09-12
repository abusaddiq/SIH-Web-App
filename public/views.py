from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django_ratelimit.decorators import ratelimit

from blog.models import Post
from core.models import CmsPage, ContactSettings, HomepageSection, WebsiteSettings
from core.models import audit_log
from core.services import notify_admins
from facilities.models import Booking, Enquiry, Facility, Service
from programmes.models import Programme

from .forms import BookingForm, ContactForm, FacilityEnquiryForm
from .ai import get_assistant


def home(request):
    today = timezone.localdate()
    sections = {s.key: s for s in HomepageSection.objects.filter(is_active=True)}
    ctx = {
        "sections": sections,
        "services": Service.objects.filter(is_published=True, is_featured=True)[:6],
        "featured_facilities": Facility.objects.filter(status="published", is_featured=True)[:4],
        "facilities_count": Facility.objects.filter(status="published").count(),
        "upcoming_programmes": Programme.objects.filter(status="published", start_date__gte=today).order_by("start_date")[:4],
        "featured_posts": Post.objects.filter(status="published", published_at__lte=timezone.now()).order_by("-published_at")[:3],
    }
    return render(request, "public/home.html", ctx)


def about(request):
    page = CmsPage.objects.filter(slug="about", is_published=True).first()
    if not page:
        page = CmsPage(slug="about", title="About SPAK Innovation Hub", content="")
    return render(request, "public/about.html", {"page": page})


def services(request):
    return render(request, "public/services.html", {"services": Service.objects.filter(is_published=True)})


def facilities(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("category", "")
    qs = Facility.objects.filter(status="published").select_related("category")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q))
    if cat:
        qs = qs.filter(category__slug=cat)
    from facilities.models import FacilityCategory
    return render(
        request, "public/facilities/list.html",
        {"facilities": qs, "categories": FacilityCategory.objects.filter(is_active=True), "q": q, "cat": cat},
    )


def facility_detail(request, slug):
    f = get_object_or_404(Facility, slug=slug, status="published")
    return render(request, "public/facilities/detail.html", {"facility": f})


@ratelimit(key="ip", rate="20/h", block=True)
def facility_book(request, slug):
    f = get_object_or_404(Facility, slug=slug, status="published")
    form = BookingForm(request.POST or None, facility=f)
    if request.method == "POST" and form.is_valid():
        b = form.save(commit=False)
        b.facility = f
        b.save()
        audit_log(request, "create", "booking", b.ref_no, description=f"Booking request {b.ref_no} for '{f.name}'")
        notify_admins("New booking request", f"{b.full_name} requested {f.name} on {b.preferred_date}")
        return render(request, "public/facilities/booking_success.html", {"facility": f, "booking": b})
    return render(request, "public/facilities/book.html", {"facility": f, "form": form})


@ratelimit(key="ip", rate="30/h", block=True)
def facility_enquiry(request, slug):
    f = get_object_or_404(Facility, slug=slug, status="published")
    form = FacilityEnquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        e = Enquiry(
            name=form.cleaned_data["name"],
            email=form.cleaned_data["email"],
            phone=form.cleaned_data["phone"] or "",
            subject=f"Enquiry about {f.name}",
            message=form.cleaned_data["message"],
            source="facility",
            related_facility=f,
        )
        e.save()
        audit_log(request, "create", "enquiry", e.ref_no, description=f"Facility enquiry {e.ref_no} about '{f.name}'")
        notify_admins("New facility enquiry", f"{e.name} enquired about {f.name}")
        messages.success(request, "Enquiry sent. SPAK will contact you.")
        return redirect("public-facility-detail", slug=f.slug)
    return render(request, "public/facilities/enquire.html", {"facility": f, "form": form})


def meeting_rooms(request):
    qs = Facility.objects.filter(status="published", category__name__icontains="meeting")
    return render(request, "public/facilities/meeting_rooms.html", {"rooms": qs})


@ratelimit(key="ip", rate="30/h", block=True)
def contact(request):
    cs = ContactSettings.get()
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        e = Enquiry(
            name=form.cleaned_data["name"],
            email=form.cleaned_data["email"],
            phone=form.cleaned_data["phone"] or "",
            subject=form.cleaned_data["subject"],
            message=form.cleaned_data["message"],
            source="contact",
        )
        e.save()
        audit_log(request, "create", "enquiry", e.ref_no, description=f"Contact form enquiry {e.ref_no}")
        notify_admins("New contact form submission", f"{e.name} ({e.email}): {e.subject}")
        messages.success(request, "Message sent. Thank you for contacting SPAK.")
        return redirect("public-contact")
    return render(request, "public/contact.html", {"form": form, "cs": cs})


def search(request):
    query = request.GET.get("q", "").strip()
    results = {"facilities": [], "services": [], "programmes": [], "posts": []}
    if query:
        results["facilities"] = Facility.objects.filter(status="published").filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(features__icontains=query)
        )[:10]
        results["services"] = Service.objects.filter(is_published=True).filter(
            Q(name__icontains=query) | Q(short_description__icontains=query)
        )[:10]
        results["programmes"] = Programme.objects.filter(status="published").filter(
            Q(title__icontains=query) | Q(short_description__icontains=query) | Q(venue__icontains=query)
        )[:10]
        results["posts"] = Post.objects.filter(status="published").filter(
            Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(content__icontains=query)
        )[:10]
    return render(request, "public/search.html", {"query": query, "results": results})


def ai_chat(request):
    assistant = get_assistant(request)
    response = None
    question = ""
    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        if question:
            response = assistant.answer(question)
    return render(request, "public/ai_chat.html", {"response": response, "question": question})


def cms_page(request, slug):
    page = get_object_or_404(CmsPage, slug=slug, is_published=True)
    return render(request, "public/cms_page.html", {"page": page})