from django.urls import path

from . import views

urlpatterns = [
    path("", views.content_dashboard, name="blog-content-dashboard"),
    path("posts/", views.content_posts, name="blog-content-posts"),
    path("posts/new/", views.content_post_create, name="blog-content-post-create"),
    path("posts/<int:pk>/", views.content_post_detail, name="blog-content-detail"),
    path("posts/<int:pk>/delete/", views.content_post_delete, name="blog-content-delete"),
]