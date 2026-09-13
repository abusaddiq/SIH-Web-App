from django import forms

from .models import StaffMember


class StaffMemberForm(forms.ModelForm):
    social_links = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": 'Optional JSON array of links, e.g. [{"platform": "X", "url": "https://x.com/user"}]',
            }
        ),
        help_text="JSON array of link objects (platform + url). You can leave this empty.",
    )

    class Meta:
        model = StaffMember
        fields = [
            "full_name", "role", "profession", "department", "phone_number", "email",
            "bio", "profile_image", "linkedin_url", "social_links",
            "display_order", "is_active",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.TextInput(attrs={"class": "form-control"}),
            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "profile_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "linkedin_url": forms.URLInput(attrs={"class": "form-control"}),
            "display_order": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.social_links:
            import json

            self.fields["social_links"].initial = json.dumps(self.instance.social_links)

    def clean_social_links(self):
        import json

        value = (self.cleaned_data.get("social_links") or "").strip()
        if not value:
            return []
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            raise forms.ValidationError("Social links must be valid JSON.")
        if not isinstance(parsed, list):
            raise forms.ValidationError("Social links must be a JSON array.")
        return parsed