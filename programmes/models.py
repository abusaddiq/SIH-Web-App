import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class ProgrammeCategory(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Programme categories"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 1
            while ProgrammeCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)


class Person(models.Model):
    KIND_CHOICES = [("trainer", "Trainer"), ("facilitator", "Facilitator"), ("speaker", "Speaker")]
    name = models.CharField(max_length=160)
    title = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="people/", blank=True)
    email = models.EmailField(blank=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="trainer")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Programme(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted for Review"),
        ("published", "Published"),
        ("cancelled", "Cancelled"),
        ("archived", "Archived"),
    ]
    TYPE_CHOICES = [("physical", "Physical"), ("online", "Online"), ("hybrid", "Hybrid")]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        ProgrammeCategory, on_delete=models.PROTECT, related_name="programmes"
    )
    programme_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="physical")
    short_description = models.CharField(max_length=300, blank=True)
    full_description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    trainers = models.ManyToManyField(Person, blank=True, related_name="trainer_programmes")
    facilitators = models.ManyToManyField(Person, blank=True, related_name="facilitator_programmes")
    speakers = models.ManyToManyField(Person, blank=True, related_name="speaker_programmes")
    target_audience = models.CharField(max_length=300, blank=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    registration_deadline = models.DateField(null=True, blank=True)
    requires_registration = models.BooleanField(default=True)
    uses_external_registration = models.BooleanField(default=False)
    registration_link = models.URLField(blank=True)
    registration_button_label = models.CharField(max_length=40, default="Register")
    contact_info = models.CharField(max_length=200, blank=True)
    requirements = models.TextField(blank=True)
    image = models.ImageField(upload_to="programmes/", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_programmes"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_programmes"
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug, n = base, 1
            while Programme.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        return self.status == "published" and bool(self.start_date) and self.start_date >= timezone.localdate()

    @property
    def is_ongoing(self):
        return (
            self.status == "published"
            and self.start_date
            and self.end_date
            and self.start_date <= timezone.localdate() <= self.end_date
        )

    @property
    def is_past(self):
        return self.status == "published" and self.end_date and self.end_date < timezone.localdate()


def make_ref(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


class ProgrammeRegistration(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]
    ref_no = models.CharField(max_length=30, unique=True, editable=False)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name="registrations")
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.ref_no

    def save(self, *args, **kwargs):
        if not self.ref_no:
            self.ref_no = make_ref("SPAK-REG")
        super().save(*args, **kwargs)


class ProgrammeEnquiry(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("read", "Read"),
        ("replied", "Replied"),
        ("archived", "Archived"),
    ]
    ref_no = models.CharField(max_length=30, unique=True, editable=False)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name="enquiries")
    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    admin_reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.ref_no

    def save(self, *args, **kwargs):
        if not self.ref_no:
            self.ref_no = make_ref("SPAK-PEQ")
        super().save(*args, **kwargs)