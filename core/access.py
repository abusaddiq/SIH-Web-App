from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from accounts.models import ROLE_SUPER_ADMIN, ROLE_PROGRAMME_LEAD, ROLE_CONTENT_STAFF


def _user(request):
    u = getattr(request, "user", None)
    if u is None or not u.is_authenticated:
        return None
    return u


def role_required(required_callable, view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        u = _user(request)
        if u is None or not required_callable(u):
            raise PermissionDenied("You do not have permission to access this area.")
        return view(request, *args, **kwargs)

    return wrapped


def super_admin_required(view):
    return role_required(lambda u: u.is_super_admin, view)


def programme_lead_required(view):
    return role_required(lambda u: u.is_programme_lead, view)


def content_staff_required(view):
    return role_required(lambda u: u.is_content_staff, view)


def programme_lead_or_superadmin(view):
    return role_required(lambda u: u.is_programme_lead, view)


def ensure_super_admin(u):
    return u.is_super_admin


def ensure_programme_lead(u):
    return u.is_programme_lead


def ensure_content_staff(u):
    return u.is_content_staff