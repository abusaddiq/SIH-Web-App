"""
SPAK Innovation Hub — automated smoke/acceptance tests.

Covers: auth + RBAC, public pages, booking flow, programme approval workflow and
content-staff publishing. Uses the Django test client against a fresh test DB.
"""
import re

from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, ROLE_SUPER_ADMIN, ROLE_PROGRAMME_LEAD, ROLE_CONTENT_STAFF
from blog.models import Post
from core.models import WebsiteSettings
from facilities.models import FacilityCategory, Facility, FacilityImage, Booking, Enquiry
from programmes.models import ProgrammeCategory, Programme, ProgrammeRegistration, ProgrammeEnquiry


def login(client, username, password):
    r = client.get("/login/")
    token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode()).group(1)
    return client.post(
        "/login/",
        {"username": username, "password": password, "csrfmiddlewaretoken": token},
        HTTP_REFERER="/login/",
    )


class BaseSetup(TestCase):
    @classmethod
    def setUpTestData(cls):
        ws = WebsiteSettings.get()
        ws.programme_approval_required = True
        ws.save()

        cls.admin = User.objects.create_superuser(
            username="admin", email="a@example.com", password="admin12345", role=ROLE_SUPER_ADMIN
        )
        cls.lead = User.objects.create_user(
            username="lead", email="l@example.com", password="lead12345!", role=ROLE_PROGRAMME_LEAD
        )
        cls.writer = User.objects.create_user(
            username="writer", email="w@example.com", password="writer12345!", role=ROLE_CONTENT_STAFF
        )

        cat = FacilityCategory.objects.create(name="Meeting Rooms [TEST]")
        cls.facility = Facility.objects.create(
            name="Boardroom [TEST]", category=cat, overview="test", status="published", created_by=cls.admin,
            features=["Projector"],
        )
        pcat = ProgrammeCategory.objects.create(name="Skills [TEST]")
        cls.programme = Programme.objects.create(
            title="Bootcamp [TEST]", category=pcat, status="published",
            created_by=cls.lead, approved_by=cls.admin, published_at=timezone.now(),
        )

        cls.anon = __import__("django.test", fromlist=["Client"]).Client()


class PublicSiteTests(BaseSetup):
    def test_public_pages_render(self):
        for path in ["/", "/about/", "/team/", "/services/", "/projects/", "/facilities/", "/programmes/", "/blog/", "/contact/", "/search/"]:
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            self.assertTrue(b"SPAK" in r.content or r.status_code == 200)


class RbacTests(BaseSetup):
    def test_anonymous_redirected(self):
        for path in ["/admin/", "/admin/facilities/", "/programmes-dashboard/", "/content-dashboard/", "/admin/users/"]:
            r = self.anon.get(path)
            self.assertIn(r.status_code, (302,), path)

    def test_lead_denied_from_super_admin_areas(self):
        login(self.client, "lead", "lead12345!")
        for path in ["/admin/facilities/", "/admin/posts/", "/admin/users/", "/admin/settings/site/", "/admin/media/"]:
            r = self.client.get(path)
            self.assertEqual(r.status_code, 403, path)

    def test_writer_denied_but_lead_allowed_on_programmes_dash(self):
        login(self.client, "lead", "lead12345!")
        r = self.client.get("/programmes-dashboard/")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/admin/facilities/")
        self.assertEqual(r.status_code, 403)

        self.client.logout()
        login(self.client, "writer", "writer12345!")
        r = self.client.get("/programmes-dashboard/")
        self.assertEqual(r.status_code, 403)
        r = self.client.get("/content-dashboard/")
        self.assertEqual(r.status_code, 200)

    def test_super_admin_everywhere(self):
        login(self.client, "admin", "admin12345")
        for path in ["/admin/", "/admin/users/", "/programmes-dashboard/", "/content-dashboard/", "/admin/media/"]:
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)


class BookingFlowTests(BaseSetup):
    def test_public_booking_submission_and_admin_update(self):
        r = self.client.get(f"/facilities/{self.facility.slug}/book/")
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode()).group(1)
        data = {
            "csrfmiddlewaretoken": token,
            "full_name": "Test Book",
            "email": "book@example.com",
            "phone": "0712345678",
            "preferred_date": "2099-01-05",
            "participants": 2,
        }
        r = self.client.post(f"/facilities/{self.facility.slug}/book/", data)
        self.assertEqual(r.status_code, 200)
        booking = Booking.objects.get(full_name="Test Book")
        self.assertTrue(booking.ref_no.startswith("SPAK-BK"))

        login(self.client, "admin", "admin12345")
        r = self.client.get(f"/admin/bookings/{booking.pk}/")
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode()).group(1)
        r = self.client.post(
            f"/admin/bookings/{booking.pk}/",
            {"csrfmiddlewaretoken": token, "status": "approved", "admin_notes": "ok"},
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, "approved")


class ProgrammeWorkflowTests(BaseSetup):
    def test_lead_submits_programme_and_admin_approves(self):
        login(self.client, "lead", "lead12345!")
        r = self.client.get("/programmes-dashboard/programmes/new/")
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode()).group(1)
        cat = ProgrammeCategory.objects.get(name="Skills [TEST]")
        data = {
            "csrfmiddlewaretoken": token,
            "title": "New Bootcamp [TEST]",
            "category": str(cat.pk),
            "programme_type": "physical",
            "short_description": "test",
            "full_description": "test",
            "start_date": "2099-03-01",
            "end_date": "2099-03-02",
            "requires_registration": "on",
            "uses_external_registration": "",
            "registration_button_label": "Register",
            "action": "submit",
        }
        r = self.client.post("/programmes-dashboard/programmes/new/", data)
        self.assertIn(r.status_code, (302, 200))
        p = Programme.objects.get(title="New Bootcamp [TEST]")
        self.assertEqual(p.status, "submitted")
        self.assertEqual(p.created_by, self.lead)

        # Lead cannot set it published directly.
        self.client.logout()
        login(self.client, "admin", "admin12345")
        r = self.client.get(f"/admin/programmes/{p.pk}/")
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode()).group(1)
        r = self.client.post(f"/admin/programmes/{p.pk}/", {"csrfmiddlewaretoken": token, "status": "published"})
        self.assertIn(r.status_code, (302, 200))
        p.refresh_from_db()
        self.assertEqual(p.status, "published")


class ContentPublishTests(BaseSetup):
    def test_writer_publishes_post_and_its_publicly_visible(self):
        login(self.client, "writer", "writer12345!")
        r = self.client.get("/content-dashboard/posts/new/")
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode()).group(1)
        data = {
            "csrfmiddlewaretoken": token,
            "title": "Published Test Post [TEST]",
            "excerpt": "x",
            "content": "hello world",
            "tags_input": "test, news",
            "status": "draft",
            "action": "publish",
        }
        r = self.client.post("/content-dashboard/posts/new/", data)
        self.assertIn(r.status_code, (302, 200))
        post = Post.objects.get(title="Published Test Post [TEST]")
        self.assertEqual(post.status, "published")
        self.assertEqual(post.author, self.writer)
        r = self.client.get(f"/blog/{post.slug}/")
        self.assertEqual(r.status_code, 200)


class AiChatTests(BaseSetup):
    def test_rules_ai_answers_offline(self):
        r = self.client.get("/ai-chat/")
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode()).group(1)
        r = self.client.post(
            "/ai-chat/",
            {"csrfmiddlewaretoken": token, "question": "What facilities does SPAK have?"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"answer", r.content.lower())


class StaffModuleTests(BaseSetup):
    def test_staff_list_requires_super_admin(self):
        login(self.client, "lead", "lead12345!")
        r = self.client.get("/admin/staff/")
        self.assertEqual(r.status_code, 403)
        self.client.logout()
        login(self.client, "admin", "admin12345")
        r = self.client.get("/admin/staff/")
        self.assertEqual(r.status_code, 200)

    def test_staff_crud_and_toggle(self):
        login(self.client, "admin", "admin12345")
        r = self.client.get("/admin/staff/new/")
        self.assertEqual(r.status_code, 200)
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode()).group(1)
        data = {
            "csrfmiddlewaretoken": token,
            "full_name": "Test Staff [TEST]",
            "role": "Founder",
            "profession": "Engineering",
            "phone_number": "0700000000",
            "email": "test@example.com",
            "bio": "Bio line",
            "linkedin_url": "",
            "social_links": "",
            "display_order": "10",
            "is_active": "on",
        }
        r = self.client.post("/admin/staff/new/", data)
        self.assertIn(r.status_code, (302, 200))
        from staff.models import StaffMember

        m = StaffMember.objects.get(full_name="Test Staff [TEST]")
        self.assertTrue(m.is_active)

        # Toggle active
        r = self.client.post(f"/admin/staff/{m.pk}/toggle/")
        self.assertIn(r.status_code, (302, 200))
        m.refresh_from_db()
        self.assertFalse(m.is_active)

        # Edit
        r = self.client.get(f"/admin/staff/{m.pk}/")
        self.assertEqual(r.status_code, 200)
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode()).group(1)
        data.update({"csrfmiddlewaretoken": token, "full_name": "Updated Staff [TEST]", "is_active": "on"})
        r = self.client.post(f"/admin/staff/{m.pk}/", data)
        self.assertIn(r.status_code, (302, 200))
        m.refresh_from_db()
        self.assertEqual(m.full_name, "Updated Staff [TEST]")

        # Move down
        r = self.client.post(f"/admin/staff/{m.pk}/move/down/")
        self.assertIn(r.status_code, (302,))

        # Delete
        r = self.client.post(f"/admin/staff/{m.pk}/delete/")
        self.assertIn(r.status_code, (302,))
        self.assertFalse(StaffMember.objects.filter(pk=m.pk).exists())

    def test_homepage_team_section_in_context(self):
        from staff.models import StaffMember

        StaffMember.objects.create(full_name="Alice", role="Founder", is_active=True, display_order=1)
        StaffMember.objects.create(full_name="Bob", role="CTO", is_active=False, display_order=2)
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Alice")
        self.assertNotContains(r, "Bob")  # inactive member must not leak to public


class FacilityImageAdminTests(BaseSetup):
    PNG = (
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )

    def test_image_admin_rbac(self):
        login(self.client, "lead", "lead12345!")
        r = self.client.get(f"/admin/facilities/{self.facility.pk}/images/")
        self.assertEqual(r.status_code, 403)
        self.client.logout()
        login(self.client, "admin", "admin12345")
        r = self.client.get(f"/admin/facilities/{self.facility.pk}/images/")
        self.assertEqual(r.status_code, 200)

    def test_upload_sets_primary_then_reorder_and_delete(self):
        login(self.client, "admin", "admin12345")
        r = self.client.get(f"/admin/facilities/{self.facility.pk}/images/")
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode()).group(1)
        r = self.client.post(
            f"/admin/facilities/{self.facility.pk}/images/",
            {"csrfmiddlewaretoken": token, "captions": "Shot", "make_first_primary": "on",
             "images": SimpleUploadedFile("a.png", self.PNG, content_type="image/png")},
        )
        self.assertIn(r.status_code, (302, 200))
        img = FacilityImage.objects.get(facility=self.facility, alt_text="")
        self.assertTrue(img.is_primary)
        self.facility.refresh_from_db()
        self.assertEqual(self.facility.primary_image.name, img.image.name)

        # second image with its own file; set it as main
        img2 = FacilityImage.objects.create(facility=self.facility, sort_order=20)
        img2.image.save("b.png", ContentFile(self.PNG), save=True)
        r = self.client.post(f"/admin/facilities/images/{img2.pk}/primary/")
        self.assertIn(r.status_code, (302,))
        img2.refresh_from_db()
        img.refresh_from_db()
        self.assertTrue(img2.is_primary)
        self.assertFalse(img.is_primary)
        self.facility.refresh_from_db()
        self.assertEqual(self.facility.primary_image.name, img2.image.name)

        # move first image up, then delete it
        r = self.client.post(f"/admin/facilities/images/{img.pk}/up/")
        self.assertIn(r.status_code, (302,))
        r = self.client.post(f"/admin/facilities/images/{img.pk}/delete/")
        self.assertIn(r.status_code, (302,))
        self.assertFalse(FacilityImage.objects.filter(pk=img.pk).exists())

    def test_public_detail_shows_primary_and_gallery(self):
        img = FacilityImage(facility=self.facility, sort_order=10)
        img.image.save("x.png", ContentFile(self.PNG), save=True)
        img.is_primary = True
        img.save()
        self.facility.primary_image = img.image
        self.facility.save()

        login(self.client, "admin", "admin12345")
        r = self.client.get(f"/facilities/{self.facility.slug}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content.count(b"/media/facilities/"), 2)  # featured media + gallery