from django.db import models


class StaffMember(models.Model):
    full_name = models.CharField(max_length=160)
    role = models.CharField(max_length=120)
    profession = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="staff/", blank=True)
    linkedin_url = models.URLField(blank=True)
    social_links = models.JSONField(default=list, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "full_name"]
        verbose_name = "Staff member"
        verbose_name_plural = "Staff members"

    def __str__(self):
        return self.full_name

    @property
    def initials(self):
        parts = [p for p in self.full_name.split() if p]
        return "".join(p[0] for p in parts[:2]).upper() or "?"