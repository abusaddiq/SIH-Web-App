from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    code = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @classmethod
    def get(cls, code):
        return cls.objects.filter(code=code, is_active=True).first()


ROLE_SUPER_ADMIN = "super_admin"
ROLE_PROGRAMME_LEAD = "programme_lead"
ROLE_CONTENT_STAFF = "content_staff"


class User(AbstractUser):
    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, "Super Admin / Hub Administrator"),
        (ROLE_PROGRAMME_LEAD, "Programme & Training Lead"),
        (ROLE_CONTENT_STAFF, "Content & Communication Staff"),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=ROLE_CONTENT_STAFF)
    phone = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True)
    must_change_password = models.BooleanField(default=False)

    @property
    def role_label(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    @property
    def is_super_admin(self):
        return self.role == ROLE_SUPER_ADMIN or self.is_superuser

    @property
    def is_programme_lead(self):
        return self.role in (ROLE_PROGRAMME_LEAD, ROLE_SUPER_ADMIN) or self.is_superuser

    @property
    def is_content_staff(self):
        return self.role in (ROLE_CONTENT_STAFF, ROLE_SUPER_ADMIN) or self.is_superuser

    def can_access_admin(self):
        return self.is_authenticated and self.is_super_admin

    def can_access_programmes_dashboard(self):
        return self.is_authenticated and self.is_programme_lead

    def can_manage_content(self):
        return self.is_authenticated and self.is_content_staff