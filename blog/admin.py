from django.contrib import admin

from .models import Category, Tag, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "status", "published_at", "views")
    list_filter = ("status", "category", "published_at")
    search_fields = ("title", "excerpt", "content")
    filter_horizontal = ("tags",)
    date_hierarchy = "created_at"