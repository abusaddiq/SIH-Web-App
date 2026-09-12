from django import forms

from facilities.models import Booking, Enquiry


class ContactForm(forms.Form):
    name = forms.CharField(max_length=160, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone = forms.CharField(max_length=40, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    subject = forms.CharField(max_length=220, widget=forms.TextInput(attrs={"class": "form-control"}))
    message = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 5}))


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "full_name", "organization", "email", "phone",
            "preferred_date", "start_time", "end_time", "participants",
            "purpose", "requirements", "message",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "organization": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "required": True}),
            "phone": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "preferred_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "participants": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "purpose": forms.TextInput(attrs={"class": "form-control"}),
            "requirements": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, facility=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.facility = facility

    def clean_preferred_date(self):
        from django.utils import timezone

        date = self.cleaned_data["preferred_date"]
        if date < timezone.localdate():
            raise forms.ValidationError("The preferred date cannot be in the past.")
        return date

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        if start and end and end <= start:
            raise forms.ValidationError("The end time must be later than the start time.")
        return cleaned


class FacilityEnquiryForm(forms.Form):
    name = forms.CharField(max_length=160, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone = forms.CharField(max_length=40, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    message = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}))