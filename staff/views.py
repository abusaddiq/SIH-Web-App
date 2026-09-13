from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.access import super_admin_required
from core.models import audit_log

from .forms import StaffMemberForm
from .models import StaffMember


@super_admin_required
def staff_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    qs = StaffMember.objects.all()
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) | Q(role__icontains=q)
            | Q(profession__icontains=q) | Q(department__icontains=q)
            | Q(email__icontains=q) | Q(phone_number__icontains=q)
        )
    if status:
        qs = qs.filter(is_active=(status == "active"))
    return render(
        request, "admin_shell/staff/list.html",
        {"members": qs, "q": q, "status": status},
    )


@super_admin_required
def staff_create(request):
    form = StaffMemberForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        m = form.save()
        audit_log(request, "create", "staff", m.pk, new={"name": m.full_name, "role": m.role},
                  description=f"Created staff member '{m.full_name}'")
        messages.success(request, "Staff member added.")
        return redirect("staff-admin-list")
    return render(request, "admin_shell/staff/form.html", {"form": form, "title": "Add Staff Member", "member": None})


@super_admin_required
def staff_update(request, pk):
    m = get_object_or_404(StaffMember, pk=pk)
    form = StaffMemberForm(request.POST or None, request.FILES or None, instance=m)
    if request.method == "POST" and form.is_valid():
        before = {"name": m.full_name, "role": m.role, "active": m.is_active}
        form.save()
        audit_log(request, "update", "staff", m.pk, previous=before,
                  new={"name": m.full_name, "role": m.role}, description=f"Updated staff member '{m.full_name}'")
        messages.success(request, "Staff member updated.")
        return redirect("staff-admin-list")
    return render(request, "admin_shell/staff/form.html", {"form": form, "title": f"Edit {m.full_name}", "member": m})


@super_admin_required
def staff_delete(request, pk):
    if request.method == "POST":
        m = get_object_or_404(StaffMember, pk=pk)
        audit_log(request, "delete", "staff", pk, previous={"name": m.full_name}, description=f"Deleted staff member '{m.full_name}'")
        m.delete()
        messages.success(request, "Staff member removed.")
    return redirect("staff-admin-list")


@super_admin_required
def staff_toggle_active(request, pk):
    if request.method == "POST":
        m = get_object_or_404(StaffMember, pk=pk)
        before = m.is_active
        m.is_active = not m.is_active
        before_vals = {"active": before}
        m.save(update_fields=["is_active", "updated_at"])
        audit_log(request, "update", "staff", pk, previous=before_vals,
                  new={"active": m.is_active},
                  description=f"{'Deactivated' if not m.is_active else 'Activated'} staff member '{m.full_name}'")
        messages.success(request, f"{m.full_name} is now {'active' if m.is_active else 'hidden'} on the site.")
    return redirect("staff-admin-list")


@super_admin_required
def staff_move(request, pk, direction):
    m = get_object_or_404(StaffMember, pk=pk)
    qs = list(StaffMember.objects.order_by("display_order", "id"))
    idx = next((i for i, x in enumerate(qs) if x.pk == m.pk), None)
    swap = None
    if direction == "up" and idx and idx > 0:
        swap = qs[idx - 1]
    elif direction == "down" and idx is not None and idx < len(qs) - 1:
        swap = qs[idx + 1]
    if swap:
        m.display_order, swap.display_order = swap.display_order, m.display_order
        m.save(update_fields=["display_order", "updated_at"])
        swap.save(update_fields=["display_order", "updated_at"])
    return redirect("staff-admin-list")