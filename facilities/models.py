import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class FacilityCategory(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Facility categories"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 1
            while FacilityCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)


def facility_feature_default():
    return list


def price_json_default():
    return list


class Facility(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.ForeignKey(FacilityCategory, on_delete=models.PROTECT, related_name="facilities")
    overview = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    features = models.JSONField(default=facility_feature_default, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    availability_text = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True)
    terms = models.TextField(blank=True)
    primary_image = models.ImageField(upload_to="facilities/", blank=True)
    gallery = models.ManyToManyField("core.MediaItem", blank=True, related_name="facilities")
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 1
            while Facility.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def current_prices(self):
        return self.prices.filter(is_active=True)

    @property
    def images_active(self):
        return self.facility_images.filter(is_active=True).order_by("sort_order", "id")


class FacilityImage(models.Model):
    """Gallery image for a Facility, managed by Super Admins from the admin shell."""
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="facility_images")
    image = models.ImageField(upload_to="facilities/")
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name_plural = "Facility images"
        constraints = [
            models.UniqueConstraint(
                fields=["facility"], condition=models.Q(is_primary=True), name="unique_primary_image_per_facility"
            )
        ]

    def __str__(self):
        return self.alt_text or self.image.name


class FacilityPrice(models.Model):
    PRICE_TYPES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("membership", "Membership"),
        ("special", "Special"),
    ]
    CURRENCIES = [("KES", "KES (Kenyan Shilling)"), ("USD", "USD"), ("NGN", "NGN")]
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="prices")
    price_type = models.CharField(max_length=20, choices=PRICE_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCIES, default="KES")
    billing_period = models.CharField(max_length=80, blank=True, default="per day")
    effective_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["facility", "price_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["facility", "price_type"], condition=models.Q(is_active=True), name="unique_active_price_per_type"
            )
        ]

    def __str__(self):
        return f"{self.facility} - {self.get_price_type_display()} {self.amount} {self.currency}"


class Service(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    icon = models.CharField(max_length=120, blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    full_description = models.TextField(blank=True)
    image = models.ImageField(upload_to="services/", blank=True)
    price_text = models.CharField(max_length=160, blank=True, default="Contact SPAK for pricing")
    cta_label = models.CharField(max_length=60, blank=True)
    cta_link = models.CharField(max_length=200, blank=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 1
            while Service.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)


def make_ref(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    ref_no = models.CharField(max_length=30, unique=True, editable=False)
    full_name = models.CharField(max_length=160)
    organization = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT, related_name="bookings")
    preferred_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    participants = models.PositiveIntegerField(default=1)
    purpose = models.CharField(max_length=300, blank=True)
    requirements = models.TextField(blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return self.ref_no

    def save(self, *args, **kwargs):
        if not self.ref_no:
            self.ref_no = make_ref("SPAK-BK")
        super().save(*args, **kwargs)


class Enquiry(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("read", "Read"),
        ("replied", "Replied"),
        ("archived", "Archived"),
    ]
    SOURCE_CHOICES = [
        ("contact", "Contact form"),
        ("facility", "Facility"),
        ("programme", "Programme"),
        ("booking", "Booking"),
        ("ai", "AI assistant"),
    ]
    ref_no = models.CharField(max_length=30, unique=True, editable=False)
    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=220, blank=True)
    message = models.TextField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="contact")
    related_facility = models.ForeignKey(
        Facility, null=True, blank=True, on_delete=models.SET_NULL, related_name="enquiries"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", db_index=True)
    admin_reply = models.TextField(blank=True)
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.ref_no

    def save(self, *args, **kwargs):
        if not self.ref_no:
            self.ref_no = make_ref("SPAK-ENQ")
        super().save(*args, **kwargs)