from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.access import super_admin_required, content_staff_required
from core.models import audit_log

from .models import Category, Tag, Post
from .forms import PostForm, CategoryForm, TagForm


STATUS_ORDER = {"published": 0, "scheduled": 1, "draft": 2, "unpublished": 3, "archived": 4}


def post_list(request):
    qs = Post.objects.filter(status="published", published_at__lte=timezone.now())
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(content__icontains=q))
    if category:
        qs = qs.filter(category__slug=category)
    qs = qs.order_by("-published_at")
    paginator = Paginator(qs, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "public/blog/list.html",
        {
            "posts": page_obj,
            "page_obj": page_obj,
            "categories": Category.objects.all(),
            "q": q,
            "category_slug": category,
        },
    )


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.status != "published" or (post.published_at and post.published_at > timezone.now()):
        raise Http404("Not found.")
    Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
    post.views += 1
    related = (
        Post.objects.filter(status="published", category=post.category)
        .exclude(pk=post.pk)
        .order_by("-published_at")[:3]
    )
    return render(request, "public/blog/detail.html", {"post": post, "related": related})


@content_staff_required
def content_dashboard(request):
    return render(request, "admin_shell/blog/content_dashboard.html", {"posts": Post.objects.filter(author=request.user)})


@content_staff_required
def content_posts(request):
    q = request.GET.get("q", "").strip()
    qs = Post.objects.filter(author=request.user)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q))
    return render(request, "admin_shell/blog/content_list.html", {"posts": qs})


@content_staff_required
def content_post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        p = form.save(commit=False)
        p.author = request.user
        action = request.POST.get("action", "save")
        if action == "publish":
            p.status = "published"
            p.published_at = p.scheduled_for or timezone.now()
        else:
            p.status = "draft"
        p.save()
        form.save_extra_fields(p)
        audit_log(request, "create", "blog_post", p.pk, new={"status": p.status, "title": p.title}, description=f"Content staff created '{p.title}'")
        messages.success(request, "Post saved.")
        return redirect("blog-content-detail", pk=p.pk)
    return render(request, "admin_shell/blog/content_form.html", {"form": form, "post": None})


@content_staff_required
def content_post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        p = form.save(commit=False)
        p.author = request.user
        action = request.POST.get("action", "save")
        if action == "publish":
            p.status = "published"
            p.published_at = p.scheduled_for or timezone.now()
        elif action == "unpublish":
            p.status = "unpublished"
        else:
            p.status = "draft"
        p.save()
        form.save_extra_fields(p)
        audit_log(request, "update", "blog_post", p.pk, new={"status": p.status}, description=f"Content staff updated '{p.title}'")
        messages.success(request, "Post saved.")
        return redirect("blog-content-detail", pk=p.pk)
    return render(request, "admin_shell/blog/content_form.html", {"form": form, "post": post})


@content_staff_required
def content_post_delete(request, pk):
    if request.method == "POST":
        Post.objects.filter(pk=pk, author=request.user).delete()
        messages.success(request, "Post deleted.")
    return redirect("blog-content-posts")


@super_admin_required
def admin_posts(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    qs = Post.objects.select_related("category", "author").all()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(content__icontains=q))
    if status:
        qs = qs.filter(status=status)
    qs = sorted(qs, key=lambda p: STATUS_ORDER.get(p.status, 9))
    return render(request, "admin_shell/blog/list.html", {"posts": qs, "q": q, "status": status, "statuses": Post.STATUS_CHOICES})


@super_admin_required
@super_admin_required
def admin_post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        action = request.POST.get("action", "save")
        p = form.save(commit=False)
        p.author = request.user
        if action == "publish":
            p.status = "published"
            p.published_at = p.scheduled_for or timezone.now()
        elif action == "unpublish":
            p.status = "unpublished"
        elif action == "schedule":
            p.status = "scheduled"
            p.published_at = None
        elif action == "archive":
            p.status = "archived"
        else:
            p.status = "draft"
        p.save()
        form.save_extra_fields(p)
        audit_log(request, "update", "blog_post", p.pk, new={"status": p.status, "title": p.title}, description=f"Blog '{p.title}' -> {p.status}")
        messages.success(request, "Post saved.")
        return redirect("blog-admin-detail", pk=p.pk)
    default_status = request.GET.get("status", "draft")
    return render(request, "admin_shell/blog/form.html", {"form": form, "post": post, "default_status": default_status})


@super_admin_required
def admin_post_create(request):
    default_status = request.GET.get("status", "draft")
    form = PostForm(request.POST or None, request.FILES or None, initial={"status": default_status})
    if request.method == "POST" and form.is_valid():
        action = request.POST.get("action", "save")
        p = form.save(commit=False)
        p.author = request.user
        if action == "publish":
            p.status = "published"
            p.published_at = p.scheduled_for or timezone.now()
        elif action == "unpublish":
            p.status = "unpublished"
        elif action == "schedule":
            p.status = "scheduled"
            p.published_at = None
        elif action == "archive":
            p.status = "archived"
        else:
            p.status = "draft"
        p.save()
        form.save_extra_fields(p)
        audit_log(request, "create", "blog_post", p.pk, new={"status": p.status, "title": p.title}, description=f"Created blog '{p.title}'")
        messages.success(request, "Post created.")
        return redirect("blog-admin-detail", pk=p.pk)
    return render(request, "admin_shell/blog/form.html", {"form": form, "post": None, "default_status": default_status})


@super_admin_required
def admin_post_delete(request, pk):
    if request.method == "POST":
        p = get_object_or_404(Post, pk=pk)
        audit_log(request, "delete", "blog_post", pk, new={"title": p.title}, description=f"Deleted blog '{p.title}'")
        p.delete()
        messages.success(request, "Post deleted.")
    return redirect("blog-admin-posts")


@super_admin_required
def admin_categories(request):
    cats = Category.objects.all()
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category added.")
        return redirect("blog-admin-categories")
    return render(request, "admin_shell/blog/categories.html", {"categories": cats, "form": form})


@super_admin_required
def admin_tags(request):
    tags = Tag.objects.all()
    form = TagForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tag added.")
        return redirect("blog-admin-tags")
    return render(request, "admin_shell/blog/tags.html", {"tags": tags, "form": form})


# Content-staff friendly entry points delegated to the same management views.
blog_content_dashboard = _noop = lambda request: redirect("blog-admin-posts")