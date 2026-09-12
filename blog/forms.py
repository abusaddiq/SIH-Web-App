from django import forms

from .models import Category, Tag, Post


class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Comma-separated, e.g. innovation, technology"}
        ),
        label="Tags",
    )
    new_category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Or create a new category"}),
        label="New category (optional)",
    )

    class Meta:
        model = Post
        fields = [
            "title", "category", "new_category", "excerpt", "content", "featured_image",
            "tags_input", "status", "scheduled_for", "seo_title", "seo_description",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "excerpt": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 14}),
            "featured_image": forms.FileInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "scheduled_for": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "seo_title": forms.TextInput(attrs={"class": "form-control"}),
            "seo_description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["tags_input"].initial = ", ".join(self.instance.tags.values_list("name", flat=True))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_extra_fields(instance)
        return instance

    def save_extra_fields(self, instance):
        """Persist new-category and comma-separated tags (safe to call after save)."""
        new_cat = (self.cleaned_data.get("new_category") or "").strip()
        if new_cat and not self.cleaned_data.get("category"):
            cat, _ = Category.objects.get_or_create(name=new_cat)
            instance.category = cat
            instance.save(update_fields=["category"])
        tags = [t.strip() for t in (self.cleaned_data.get("tags_input") or "").split(",") if t.strip()]
        tag_objs = [Tag.objects.get_or_create(name=t)[0] for t in tags]
        if tag_objs:
            instance.tags.set(tag_objs)
        return instance


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}