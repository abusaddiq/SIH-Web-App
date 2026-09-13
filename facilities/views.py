from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.access import super_admin_required
from core.models import audit_log
from core.services import notify_admins

from .forms import (
    FacilityForm,
    FacilityCategoryForm,
    FacilityImageForm,
    FacilityImageUploadForm,
    FacilityPriceForm,
    ServiceForm,
    BookingStatusForm,
    EnquiryReplyForm,
)
from .models import (
    Facility,
    FacilityCategory,
    FacilityImage,
    FacilityPrice,
    Service,
    Booking,
    Enquiry,
)


@super_admin_required
def facilities_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    qs = Facility.objects.select_related("category").all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q))
    if status:
        qs = qs.filter(status=status)
    return render(
        request, "admin_shell/facilities/list.html",
        {"facilities": qs, "q": q, "status": status, "statuses": Facility.STATUS_CHOICES},
    )


@super_admin_required
def facility_create(request):
    form = FacilityForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        f = form.save(commit=False)
        f.created_by = request.user
        f.save()
        audit_log(request, "create", "facility", f.pk, new={"name": f.name}, description=f"Created facility '{f.name}'")
        messages.success(request, f"Facility '{f.name}' created.")
        return redirect("fac-admin-prices", pk=f.pk)
    return render(request, "admin_shell/facilities/form.html", {"form": form, "title": "Add Facility", "facility": None})


@super_admin_required
def facility_update(request, pk):
    f = get_object_or_404(Facility, pk=pk)
    form = FacilityForm(request.POST or None, request.FILES or None, instance=f)
    if request.method == "POST" and form.is_valid():
        before = {"name": f.name, "status": f.status, "capacity": f.capacity}
        form.save()
        audit_log(request, "update", "facility", f.pk, previous=before, new={"name": f.name}, description=f"Updated facility '{f.name}'")
        messages.success(request, "Facility updated.")
        return redirect("fac-admin-prices", pk=f.pk)
    return render(request, "admin_shell/facilities/form.html", {"form": form, "title": f"Edit {f.name}", "facility": f})


@super_admin_required
def facility_delete(request, pk):
    if request.method == "POST":
        f = get_object_or_404(Facility, pk=pk)
        audit_log(request, "delete", "facility", pk, previous={"name": f.name}, description=f"Deleted facility '{f.name}'")
        f.delete()
        messages.success(request, "Facility deleted.")
    return redirect("fac-admin-facilities")


@super_admin_required
def facility_prices(request, pk):
    f = get_object_or_404(Facility, pk=pk)
    prices = f.prices.all()
    form = FacilityPriceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        old = None
        existing = FacilityPrice.objects.filter(
            facility=f, price_type=form.cleaned_data["price_type"], is_active=True
        ).exclude(pk=request.POST.get("price_pk") or 0)
        for e in existing:
            old = {"type": e.price_type, "amount": str(e.amount)}
            e.is_active = False
            e.save()
        p = form.save(commit=False)
        p.facility = f
        p.save()
        audit_log(
            request, "update", "facility_price", p.pk,
            previous=old, new={"type": p.price_type, "amount": str(p.amount), "facility": f.name},
            description=f"Set {f.name} {p.get_price_type_display()} price to {p.amount}",
        )
        messages.success(request, "Price saved. The public website now shows the new price.")
        return redirect("fac-admin-prices", pk=f.pk)
    return render(request, "admin_shell/facilities/prices.html", {"facility": f, "prices": prices, "form": form})


@super_admin_required
def facility_price_delete(request, pk):
    if request.method == "POST":
        p = get_object_or_404(FacilityPrice, pk=pk)
        audit_log(request, "delete", "facility_price", pk, description=f"Deleted price for {p.facility.name} ({p.get_price_type_display()})")
        p.delete()
        messages.success(request, "Price removed.")
        return redirect("fac-admin-prices", pk=p.facility.pk)
    return redirect("fac-admin-facilities")


@super_admin_required
def facility_images(request, pk):
    f = get_object_or_404(Facility, pk=pk)
    images = f.facility_images.all()
    form = FacilityImageUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        made_primary = False
        start = (images.last().sort_order + 10) if images.exists() else 10
        for i, image_file in enumerate(form.cleaned_data["images"]):
            img = FacilityImage(facility=f, image=image_file, sort_order=start + i * 10)
            if form.cleaned_data["captions"]:
                img.caption = form.cleaned_data["captions"]
            img.save()
            if form.cleaned_data["make_first_primary"] and i == 0:
                img.is_primary = True
                img.save(update_fields=["is_primary"])
                f.primary_image = img.image
                f.save(update_fields=["primary_image"])
                made_primary = True
        audit_log(
            request, "create", "facility_image", f.pk,
            new={"facility": f.name}, description=f"Uploaded {len(form.cleaned_data['images'])} image(s) to '{f.name}'",
        )
        messages.success(request, f"{len(form.cleaned_data['images'])} image(s) uploaded." +
                         (" First image is now the main image." if made_primary else ""))
        return redirect("fac-admin-facility-images", pk=f.pk)
    return render(request, "admin_shell/facilities/images.html", {"facility": f, "images": images, "form": form})


@super_admin_required
def facility_image_edit(request, pk):
    img = get_object_or_404(FacilityImage, pk=pk)
    form = FacilityImageForm(request.POST or None, request.FILES or None, instance=img)
    if request.method == "POST" and form.is_valid():
        form.save()
        if form.cleaned_data["is_primary"]:
            FacilityImage.objects.filter(facility=img.facility).exclude(pk=img.pk).update(is_primary=False)
            if not img.facility.primary_image:
                img.facility.primary_image = img.image
                img.facility.save(update_fields=["primary_image"])
        audit_log(request, "update", "facility_image", img.pk, description=f"Edited image for '{img.facility.name}'")
        messages.success(request, "Image updated.")
        return redirect("fac-admin-facility-images", pk=img.facility.pk)
    return render(request, "admin_shell/facilities/image_edit.html", {"form": form, "image": img, "facility": img.facility})


@super_admin_required
def facility_image_delete(request, pk):
    if request.method == "POST":
        img = get_object_or_404(FacilityImage, pk=pk)
        facility = img.facility
        audit_log(request, "delete", "facility_image", pk, description=f"Deleted image for '{facility.name}'")
        if facility.primary_image and img.image and facility.primary_image.name == img.image.name:
            facility.primary_image = ""
            facility.save(update_fields=["primary_image"])
        img.delete()
        messages.success(request, "Image deleted.")
        return redirect("fac-admin-facility-images", pk=facility.pk)
    return redirect("fac-admin-facilities")


def _swap_image_order(request, pk, direction):
    img = get_object_or_404(FacilityImage, pk=pk)
    order_qs = FacilityImage.objects.filter(facility=img.facility)
    if direction == "up":
        other = order_qs.filter(sort_order__lt=img.sort_order).order_by("-sort_order").first()
    else:
        other = order_qs.filter(sort_order__gt=img.sort_order).order_by("sort_order").first()
    if other:
        img.sort_order, other.sort_order = other.sort_order, img.sort_order
        img.save(update_fields=["sort_order"])
        other.save(update_fields=["sort_order"])
        audit_log(request, "update", "facility_image", img.pk, description=f"Reordered image in '{img.facility.name}' ({direction})")
    return redirect("fac-admin-facility-images", pk=img.facility.pk)


@super_admin_required
def facility_image_up(request, pk):
    return _swap_image_order(request, pk, "up")


@super_admin_required
def facility_image_down(request, pk):
    return _swap_image_order(request, pk, "down")


@super_admin_required
def facility_image_set_primary(request, pk):
    if request.method == "POST":
        img = get_object_or_404(FacilityImage, pk=pk)
        FacilityImage.objects.filter(facility=img.facility).update(is_primary=False)
        img.is_primary = True
        img.save(update_fields=["is_primary"])
        if img.image:
            img.facility.primary_image = img.image
            img.facility.save(update_fields=["primary_image"])
        audit_log(request, "update", "facility_image", img.pk, description=f"Set main image for '{img.facility.name}'")
        messages.success(request, "Main image updated — the public page now shows this photo first.")
        return redirect("fac-admin-facility-images", pk=img.facility.pk)
    return redirect("fac-admin-facilities")


@super_admin_required
def facility_categories(request):
    cats = FacilityCategory.objects.all()
    form = FacilityCategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category added.")
        return redirect("fac-admin-categories")
    return render(request, "admin_shell/facilities/categories.html", {"categories": cats, "form": form})


@super_admin_required
def services_list(request):
    q = request.GET.get("q", "").strip()
    qs = Service.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(short_description__icontains=q))
    return render(request, "admin_shell/services/list.html", {"services": qs, "q": q})


@super_admin_required
def service_create(request):
    form = ServiceForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        s = form.save()
        audit_log(request, "create", "service", s.pk, new={"name": s.name}, description=f"Created service '{s.name}'")
        messages.success(request, "Service created.")
        return redirect("fac-admin-services")
    return render(request, "admin_shell/services/form.html", {"form": form, "title": "Add Service", "service": None})


@super_admin_required
def service_update(request, pk):
    s = get_object_or_404(Service, pk=pk)
    form = ServiceForm(request.POST or None, request.FILES or None, instance=s)
    if request.method == "POST" and form.is_valid():
        form.save()
        audit_log(request, "update", "service", s.pk, description=f"Updated service '{s.name}'")
        messages.success(request, "Service updated.")
        return redirect("fac-admin-services")
    return render(request, "admin_shell/services/form.html", {"form": form, "title": f"Edit {s.name}", "service": s})


@super_admin_required
def service_delete(request, pk):
    if request.method == "POST":
        s = get_object_or_404(Service, pk=pk)
        audit_log(request, "delete", "service", pk, description=f"Deleted service '{s.name}'")
        s.delete()
        messages.success(request, "Service deleted.")
    return redirect("fac-admin-services")


@super_admin_required
def bookings_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    qs = Booking.objects.select_related("facility").all()
    if q:
        qs = qs.filter(
            Q(ref_no__icontains=q) | Q(full_name__icontains=q) | Q(email__icontains=q)
            | Q(organization__icontains=q) | Q(phone__icontains=q) | Q(facility__name__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)
    return render(
        request, "admin_shell/bookings/list.html",
        {"bookings": qs, "q": q, "status": status, "statuses": Booking.STATUS_CHOICES},
    )


@super_admin_required
def booking_detail(request, pk):
    b = get_object_or_404(Booking, pk=pk)
    form = BookingStatusForm(request.POST or None, initial={"status": b.status, "admin_notes": b.admin_notes})
    if request.method == "POST" and form.is_valid():
        before = {"status": b.status}
        b.status = form.cleaned_data["status"]
        b.admin_notes = form.cleaned_data["admin_notes"]
        b.reviewed_by = request.user
        b.reviewed_at = timezone.now()
        b.save(update_fields=["status", "admin_notes", "reviewed_by", "reviewed_at"])
        audit_log(
            request, "update", "booking", b.ref_no,
            previous=before, new={"status": b.status}, description=f"Booking {b.ref_no} set to {b.status}",
        )
        notify_admins(f"Booking {b.ref_no} updated to {b.status}", f"By {request.user} for {b.facility.name}")
        messages.success(request, "Booking updated.")
        return redirect("fac-admin-booking-detail", pk=b.pk)
    return render(request, "admin_shell/bookings/detail.html", {"booking": b, "form": form})


@super_admin_required
def enquiries_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    qs = Enquiry.objects.select_related("related_facility").all()
    if q:
        qs = qs.filter(
            Q(ref_no__icontains=q) | Q(name__icontains=q) | Q(email__icontains=q)
            | Q(subject__icontains=q) | Q(message__icontains=q) | Q(phone__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)
    return render(
        request, "admin_shell/enquiries/list.html",
        {"enquiries": qs, "q": q, "status": status, "statuses": Enquiry.STATUS_CHOICES},
    )


@super_admin_required
def enquiry_detail(request, pk):
    e = get_object_or_404(Enquiry, pk=pk)
    if e.status == "new":
        e.status = "read"
        e.save(update_fields=["status"])
    form = EnquiryReplyForm(request.POST or None, initial={"status": e.status, "admin_reply": e.admin_reply})
    if request.method == "POST" and form.is_valid():
        e.status = form.cleaned_data["status"]
        e.admin_reply = form.cleaned_data["admin_reply"]
        e.replied_by = request.user
        e.replied_at = timezone.now()
        e.save(update_fields=["status", "admin_reply", "replied_by", "replied_at"])
        audit_log(request, "update", "enquiry", e.ref_no, new={"status": e.status}, description=f"Enquiry {e.ref_no} -> {e.status}")
        messages.success(request, "Enquiry updated.")
        return redirect("fac-admin-enquiry-detail", pk=e.pk)
    return render(request, "admin_shell/enquiries/detail.html", {"enquiry": e, "form": form})