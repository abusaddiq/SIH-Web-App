from django.urls import path

from . import views

urlpatterns = [
    path("posts/", views.admin_posts, name="blog-admin-posts"),
    path("posts/new/", views.admin_post_create, name="blog-admin-post-create"),
    path("posts/<int:pk>/", views.admin_post_detail, name="blog-admin-detail"),
    path("posts/<int:pk>/delete/", views.admin_post_delete, name="blog-admin-delete"),
    path("categories/", views.admin_categories, name="blog-admin-categories"),
    path("tags/", views.admin_tags, name="blog-admin-tags"),
]