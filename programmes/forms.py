from django import forms

from .models import (
    ProgrammeCategory,
    Person,
    Programme,
    ProgrammeRegistration,
    ProgrammeEnquiry,
)


class ProgrammeForm(forms.ModelForm):
    trainers = forms.ModelMultipleChoiceField(
        queryset=None, required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
    )
    facilitators = forms.ModelMultipleChoiceField(
        queryset=None, required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
    )
    speakers = forms.ModelMultipleChoiceField(
        queryset=None, required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
    )

    class Meta:
        model = Programme
        fields = [
            "title", "category", "programme_type", "short_description", "full_description",
            "start_date", "end_date", "start_time", "end_time", "venue",
            "trainers", "facilitators", "speakers",
            "target_audience", "max_participants", "registration_deadline",
            "requires_registration", "uses_external_registration", "registration_link",
            "registration_button_label", "contact_info", "requirements", "image",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "programme_type": forms.Select(attrs={"class": "form-select"}),
            "short_description": forms.TextInput(attrs={"class": "form-control"}),
            "full_description": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "venue": forms.TextInput(attrs={"class": "form-control", "placeholder": "Physical venue or 'Online'"}),
            "target_audience": forms.TextInput(attrs={"class": "form-control"}),
            "max_participants": forms.NumberInput(attrs={"class": "form-control"}),
            "registration_deadline": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "registration_link": forms.URLInput(attrs={"class": "form-control"}),
            "registration_button_label": forms.TextInput(attrs={"class": "form-control"}),
            "contact_info": forms.TextInput(attrs={"class": "form-control"}),
            "requirements": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["trainers"].queryset = Person.objects.filter(kind="trainer")
        self.fields["facilitators"].queryset = Person.objects.filter(kind="facilitator")
        self.fields["speakers"].queryset = Person.objects.filter(kind="speaker")

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get("start_date")
        end_date = cleaned.get("end_date")
        deadline = cleaned.get("registration_deadline")
        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "End date cannot be before the start date.")
        if start_date and deadline and deadline < start_date:
            self.add_error("registration_deadline", "Registration deadline cannot be after the start date.")
        uses_external = cleaned.get("uses_external_registration")
        if uses_external and not cleaned.get("registration_link"):
            self.add_error("registration_link", "Please provide a registration link when using external registration.")
        return cleaned


class ProgrammeCategoryForm(forms.ModelForm):
    class Meta:
        model = ProgrammeCategory
        fields = ["name", "description", "is_active", "sort_order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "sort_order": forms.NumberInput(attrs={"class": "form-control"}),
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["name", "title", "bio", "image", "email", "kind"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "kind": forms.Select(attrs={"class": "form-select"}),
        }


class ProgrammeRegistrationForm(forms.ModelForm):
    class Meta:
        model = ProgrammeRegistration
        fields = ["full_name", "email", "phone", "organization", "message"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "organization": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ProgrammeEnquiryForm(forms.ModelForm):
    class Meta:
        model = ProgrammeEnquiry
        fields = ["name", "email", "phone", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ProgrammeStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=Programme.STATUS_CHOICES, widget=forms.Select(attrs={"class": "form-select"})
    )


class ProgrammeReplyForm(forms.Form):
    from .models import ProgrammeEnquiry as _PE

    status = forms.ChoiceField(
        choices=_PE.STATUS_CHOICES, widget=forms.Select(attrs={"class": "form-select"})
    )
    admin_reply = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}), required=False
    )