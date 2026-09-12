from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .access import super_admin_required
from .forms import WebsiteSettingsForm as _u, ContactSettingsForm as _u2  # noqa: F401
from django import forms
from .models import CmsPage, audit_log


class PageForm(forms.ModelForm):
    class Meta:
        model = CmsPage
        fields = ["title", "slug", "summary", "content", "image", "seo_title", "seo_description", "is_published"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "summary": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 14}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "seo_title": forms.TextInput(attrs={"class": "form-control"}),
            "seo_description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


@super_admin_required
def pages_list(request):
    return render(request, "admin_shell/pages/list.html", {"pages": CmsPage.objects.all()})


@super_admin_required
def page_create(request):
    form = PageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        p = form.save()
        audit_log(request, "create", "cms_page", p.pk, new={"title": p.title}, description=f"Created page '{p.title}'")
        messages.success(request, "Page created.")
        return redirect("core-page-edit", pk=p.pk)
    return render(request, "admin_shell/pages/form.html", {"form": form, "title": "New Page", "page": None})


@super_admin_required
def page_edit(request, pk):
    p = get_object_or_404(CmsPage, pk=pk)
    form = PageForm(request.POST or None, request.FILES or None, instance=p)
    if request.method == "POST" and form.is_valid():
        form.save()
        audit_log(request, "update", "cms_page", p.pk, new={"title": p.title, "slug": p.slug}, description=f"Updated page '{p.title}'")
        messages.success(request, "Page updated.")
        return redirect("core-page-edit", pk=p.pk)
    return render(request, "admin_shell/pages/form.html", {"form": form, "title": f"Edit {p.title}", "page": p})


@super_admin_required
def page_delete(request, pk):
    if request.method == "POST":
        p = get_object_or_404(CmsPage, pk=pk)
        audit_log(request, "delete", "cms_page", pk, description=f"Deleted page '{p.title}'")
        p.delete()
        messages.success(request, "Page deleted.")
    return redirect("core-pages-list")