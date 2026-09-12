from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from core.models import WebsiteSettings
from core.services import notify_admins

from .forms import LoginForm, UserForm, PasswordChangeRequiredForm, SelfUpdateForm
from .models import User


class SpakLoginView(LoginView):
    form_class = LoginForm
    template_name = "auth/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()
        request = self.request
        ip = request.META.get("REMOTE_ADDR", "")
        from core.models import AuditLog

        try:
            AuditLog.objects.create(
                user=user, action="login", entity_type="user", entity_id=user.pk, ip_address=ip[:45]
            )
        except Exception:
            pass
        if getattr(user, "must_change_password", False) and not user.is_superuser:
            return redirect("/password/change/")
        if user.is_super_admin:
            return redirect("/admin/")
        if user.is_programme_lead:
            return redirect("/programmes-dashboard/")
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["site_settings"] = WebsiteSettings.get()
        return ctx


_login_cbv = SpakLoginView.as_view()


@ratelimit(key="ip", rate="10/m", block=True)
def login_view(request):
    return _login_cbv(request)


@require_POST
def logout_view(request):
    user = request.user if request.user.is_authenticated else None
    from core.models import AuditLog

    auth_logout(request)
    if user is not None:
        try:
            AuditLog.objects.create(
                user=user, action="logout", entity_type="user", entity_id=user.pk
            )
        except Exception:
            pass
    return redirect("/")


@login_required
def password_change_view(request):
    form_cls = PasswordChangeRequiredForm if request.user.must_change_password else PasswordChangeForm
    form = form_cls(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        user.must_change_password = False
        user.save(update_fields=["must_change_password"])
        update_session_auth_hash(request, user)
        from core.models import AuditLog

        AuditLog.objects.create(user=user, action="update", entity_type="user", entity_id=user.pk)
        if user.is_super_admin:
            return redirect("/admin/")
        if user.is_programme_lead:
            return redirect("/programmes-dashboard/")
        return redirect("/")
    return render(request, "auth/password_change.html", {"form": form})


@login_required
def my_account(request):
    form = SelfUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        from core.models import AuditLog

        AuditLog.objects.create(
            user=request.user, action="update", entity_type="user", entity_id=request.user.pk
        )
        return redirect("/my-account/")
    return render(request, "auth/my_account.html", {"form": form})


# ---------------------------------------------------------------------------
# Admin: user management
# ---------------------------------------------------------------------------
from django.core.exceptions import PermissionDenied
from django.db.models import Q


def _admin_only(request):
    u = getattr(request, "user", None)
    if not u or not u.is_authenticated:
        from django.shortcuts import redirect

        return redirect("/login/")
    if not u.is_super_admin:
        raise PermissionDenied("Only Super Admin can manage users.")
    return None


def __aa(request):
    from django.shortcuts import redirect

    r = _admin_only(request)
    if r is not None:
        return r
    return None


def user_list(request):
    r = __aa(request)
    if r:
        return r
    q = request.GET.get("q", "").strip()
    qs = User.objects.all()
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
    return render(request, "admin_shell/users/list.html", {"users": qs, "q": q})


def user_create(request):
    r = __aa(request)
    if r:
        return r
    form = UserForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        if form.cleaned_data.get("password"):
            user.set_password(form.cleaned_data["password"])
        else:
            user.set_unusable_password()
        if not user.username:
            user.username = user.email.split("@")[0]
        user.is_staff = True
        user.save()
        from core.models import AuditLog

        AuditLog.objects.create(
            user=request.user, action="create", entity_type="user", entity_id=user.pk,
            description=f"Created user '{user.username}'",
        )
        return redirect("/admin/users/")
    return render(request, "admin_shell/users/form.html", {"form": form, "title": "Add User", "user_obj": None})


def user_edit(request, pk):
    r = __aa(request)
    if r:
        return r
    u = User.objects.filter(pk=pk).first()
    if not u:
        return redirect("/admin/users/")
    form = UserForm(request.POST or None, request.FILES or None, instance=u)
    if request.method == "POST" and form.is_valid():
        form.save()
        from core.models import AuditLog

        AuditLog.objects.create(
            user=request.user, action="update", entity_type="user", entity_id=u.pk,
            description=f"Updated user '{u.username}'",
        )
        return redirect("/admin/users/")
    return render(request, "admin_shell/users/form.html", {"form": form, "title": f"Edit {u.username}", "user_obj": u})


def user_toggle(request, pk):
    r = __aa(request)
    if r:
        return r
    if request.method == "POST":
        User.objects.filter(pk=pk).update(is_active=request.POST.get("is_active") == "1")
    return redirect("/admin/users/")