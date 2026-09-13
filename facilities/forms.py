from django import forms

from core.models import MediaItem

from .models import (
    Facility,
    FacilityCategory,
    FacilityImage,
    FacilityPrice,
    Service,
    Booking,
    Enquiry,
)


class FacilityImageForm(forms.ModelForm):
    class Meta:
        model = FacilityImage
        fields = ["image", "alt_text", "caption", "sort_order", "is_active", "is_primary"]
        widgets = {
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "alt_text": forms.TextInput(attrs={"class": "form-control"}),
            "caption": forms.TextInput(attrs={"class": "form-control"}),
            "sort_order": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["image"].required = False
            self.fields["image"].widget = forms.ClearableFileInput(
                attrs={"class": "form-control", "aria-describedby": "keepImageHelp"}
            )

    def clean(self):
        cleaned = super().clean()
        if not self.instance or not self.instance.pk:
            if not cleaned.get("image"):
                self.add_error("image", "Please choose an image file to upload.")
        return cleaned


class _MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class _MultipleFileField(forms.FileField):
    widget = _MultipleFileInput

    def clean(self, data, initial=None):
        if isinstance(data, (list, tuple)):
            return [f for f in (super(_MultipleFileField, self).clean(item, initial) for item in data) if f]
        return [super(_MultipleFileField, self).clean(data, initial)]


class FacilityImageUploadForm(forms.Form):
    images = _MultipleFileField(required=True, label="Images")
    make_first_primary = forms.BooleanField(required=False, initial=True, label="Make the first uploaded image the main image")
    captions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Optional caption applied to every file (you can edit each image afterwards)"}),
        label="Caption",
    )

    def clean_images(self):
        files = self.cleaned_data["images"]
        if not isinstance(files, (list, tuple)):
            files = [files]
        files = [f for f in files if f]
        if not files:
            raise forms.ValidationError("Choose at least one image file.")
        for f in files:
            if not (getattr(f, "content_type", "") or "").startswith("image/"):
                raise forms.ValidationError(f"'{getattr(f, 'name', 'file')}' is not an image file.")
        return files


class FacilityForm(forms.ModelForm):
    features_text = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "One feature per line, e.g.\nHigh-speed internet\n24/7 power backup",
            }
        ),
        label="Features (one per line)",
    )
    gallery_ids = forms.ModelMultipleChoiceField(
        queryset=None, required=False, label="Gallery images",
        widget=forms.CheckboxSelectMultiple, help_text="Pick from the media library.",
    )

    class Meta:
        model = Facility
        fields = [
            "name", "category", "overview", "description", "features_text",
            "capacity", "availability_text", "status", "terms",
            "primary_image", "is_featured", "sort_order",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "overview": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
            "capacity": forms.NumberInput(attrs={"class": "form-control"}),
            "availability_text": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "terms": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "primary_image": forms.FileInput(attrs={"class": "form-control"}),
            "sort_order": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["gallery_ids"].queryset = MediaItem.objects.all()
        if self.instance and self.instance.pk:
            self.fields["features_text"].initial = "\n".join(self.instance.features or [])
            self.fields["gallery_ids"].initial = self.instance.gallery.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.features = [
            line.strip() for line in (self.cleaned_data.get("features_text") or "").splitlines() if line.strip()
        ]
        if commit:
            instance.save()
            self.save_m2m()
            instance.gallery.set(self.cleaned_data.get("gallery_ids") or [])
        return instance


class FacilityCategoryForm(forms.ModelForm):
    class Meta:
        model = FacilityCategory
        fields = ["name", "description", "is_active", "sort_order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "sort_order": forms.NumberInput(attrs={"class": "form-control"}),
        }


class FacilityPriceForm(forms.ModelForm):
    class Meta:
        model = FacilityPrice
        fields = ["price_type", "amount", "currency", "billing_period", "effective_date", "is_active", "notes"]
        widgets = {
            "price_type": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "currency": forms.Select(attrs={"class": "form-select"}),
            "billing_period": forms.TextInput(attrs={"class": "form-control"}),
            "effective_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "notes": forms.TextInput(attrs={"class": "form-control"}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            "name", "icon", "short_description", "full_description", "image",
            "price_text", "cta_label", "cta_link", "is_published", "is_featured", "sort_order",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "icon": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. bi-wifi, bi-person-workspace"}),
            "short_description": forms.TextInput(attrs={"class": "form-control"}),
            "full_description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "price_text": forms.TextInput(attrs={"class": "form-control"}),
            "cta_label": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Book Now, Make Enquiry"}),
            "cta_link": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. /facilities/, /contact/"}),
            "sort_order": forms.NumberInput(attrs={"class": "form-control"}),
        }


def _datetime_format(v):
    return v.strftime("%d %b %Y") if v else "—"


class BookingStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=Booking.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    admin_notes = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}), required=False)


class EnquiryReplyForm(forms.Form):
    status = forms.ChoiceField(
        choices=Enquiry.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    admin_reply = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}), required=False
    )