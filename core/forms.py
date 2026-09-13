from django import forms

from .models import WebsiteSettings, ContactSettings, HomepageSection, MediaItem


class WebsiteSettingsForm(forms.ModelForm):
    class Meta:
        model = WebsiteSettings
        fields = [
            "site_name", "tagline", "logo", "logo_alt", "favicon", "default_social_image",
            "seo_title", "seo_description", "footer_text", "copyright",
            "programme_approval_required", "content_staff_enabled", "ai_enabled",
        ]
        widgets = {
            "site_name": forms.TextInput(attrs={"class": "form-control"}),
            "tagline": forms.TextInput(attrs={"class": "form-control"}),
            "logo_alt": forms.TextInput(attrs={"class": "form-control"}),
            "seo_title": forms.TextInput(attrs={"class": "form-control"}),
            "seo_description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "footer_text": forms.TextInput(attrs={"class": "form-control"}),
            "copyright": forms.TextInput(attrs={"class": "form-control"}),
        }


class ContactSettingsForm(forms.ModelForm):
    class Meta:
        model = ContactSettings
        fields = [
            "address", "address_map_link", "map_embed_html", "phone_1", "phone_2", "phone_3",
            "email_1", "email_2", "whatsapp", "working_hours",
            "office_hours", "office_hours_closed", "coworking_hours", "coworking_hours_closed",
            "emergency_contact",
            "facebook", "twitter_x", "instagram", "linkedin", "youtube", "contact_page_text",
        ]
        widgets = {
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "address_map_link": forms.TextInput(attrs={"class": "form-control"}),
            "map_embed_html": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "phone_1": forms.TextInput(attrs={"class": "form-control"}),
            "phone_2": forms.TextInput(attrs={"class": "form-control"}),
            "phone_3": forms.TextInput(attrs={"class": "form-control"}),
            "email_1": forms.EmailInput(attrs={"class": "form-control"}),
            "email_2": forms.EmailInput(attrs={"class": "form-control"}),
            "whatsapp": forms.TextInput(attrs={"class": "form-control"}),
            "working_hours": forms.TextInput(attrs={"class": "form-control"}),
            "office_hours": forms.TextInput(attrs={"class": "form-control"}),
            "office_hours_closed": forms.TextInput(attrs={"class": "form-control"}),
            "coworking_hours": forms.TextInput(attrs={"class": "form-control"}),
            "coworking_hours_closed": forms.TextInput(attrs={"class": "form-control"}),
            "emergency_contact": forms.TextInput(attrs={"class": "form-control"}),
            "facebook": forms.URLInput(attrs={"class": "form-control"}),
            "twitter_x": forms.URLInput(attrs={"class": "form-control"}),
            "instagram": forms.URLInput(attrs={"class": "form-control"}),
            "linkedin": forms.URLInput(attrs={"class": "form-control"}),
            "youtube": forms.URLInput(attrs={"class": "form-control"}),
            "contact_page_text": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class HomepageSectionForm(forms.ModelForm):
    class Meta:
        model = HomepageSection
        fields = ["key", "title", "subtitle", "content", "image", "cta_text", "cta_link", "is_active", "sort_order"]


class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = ["file", "alt_text", "caption"]


class MediaEditForm(forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = ["alt_text", "caption"]

    def clean(self):
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({"class": "form-control"})


class MediaReplaceForm(forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = ["file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs.update({"class": "form-control"})