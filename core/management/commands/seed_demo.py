import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

User = get_user_model()

ABOUT_PARA_1 = (
    "SPAK Innovation Hub is an innovation-driven environment committed to providing a professional, "
    "flexible, and productive space where creators, innovators, entrepreneurs, and professionals can "
    "connect, create, collaborate, and grow."
)
ABOUT_PARA_2 = (
    "We support our community through accessible workspaces, facilities, programmes, training, "
    "workshops, and learning opportunities designed to develop skills, encourage innovation, "
    "strengthen collaboration, and transform ideas into meaningful outcomes."
)
MANTRA = "Connect. Create. Collaborate. Grow."
TAGLINE = "A place where ideas move forward."

FACILITY_FEATURES = ["Round Table", "Refreshment on Request", "Electricity/Solar 24/7", "Functional Toilet"]


class Command(BaseCommand):
    help = (
        "Seed SPAK Innovation Hub with super-admin users and the approved official content: "
        "branding, contact & hours, About page, homepage sections, the seven official services and "
        "the four official facilities. Idempotent — safe to re-run."
    )

    def add_arguments(self, parser):
        parser.add_argument("--no-input-reset", action="store_true", help="Do not reset demo passwords if users already exist.")

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding SPAK Innovation Hub official content…")

        from core.models import WebsiteSettings, ContactSettings, HomepageSection, CmsPage
        from facilities.models import FacilityCategory, Facility, Service
        from programmes.models import ProgrammeCategory  # noqa: F401  (ensures app installed)

        admin_password = os.environ.get("SPAK_ADMIN_PASSWORD", "admin12345")
        lead_password = os.environ.get("SPAK_LEAD_PASSWORD", "lead12345!")
        writer_password = os.environ.get("SPAK_WRITER_PASSWORD", "writer12345!")

        admin = User.objects.filter(username="admin").first()
        if not admin:
            admin = User.objects.create_superuser(
                username="admin", email="admin@example.com", password=admin_password,
                first_name="SPAK", last_name="Administrator", role="super_admin",
            )
            self.stdout.write(self.style.SUCCESS("Created super admin 'admin'"))
        else:
            self.stdout.write(f"Super admin 'admin' already exists: {admin}")

        lead = User.objects.filter(username="lead").first()
        if not lead:
            lead = User.objects.create_user(
                username="lead", email="lead@example.com", password=lead_password,
                first_name="Programme", last_name="Lead", role="programme_lead",
            )
            self.stdout.write(self.style.SUCCESS("Created Programme Lead 'lead'"))
        else:
            self.stdout.write(f"Programme Lead 'lead' already exists: {lead}")

        writer = User.objects.filter(username="writer").first()
        if not writer:
            writer = User.objects.create_user(
                username="writer", email="writer@example.com", password=writer_password,
                first_name="Content", last_name="Staff", role="content_staff",
            )
            self.stdout.write(self.style.SUCCESS("Created Content Staff 'writer'"))
        else:
            self.stdout.write(f"Content Staff 'writer' already exists: {writer}")

        # ------------------------------------------------------------------ Branding
        ws = WebsiteSettings.get()
        ws.tagline = TAGLINE
        ws.programme_approval_required = True
        ws.content_staff_enabled = True
        ws.ai_enabled = True
        ws.seo_description = ABOUT_PARA_1
        ws.save(update_fields=["tagline", "seo_description", "programme_approval_required", "content_staff_enabled", "ai_enabled"])

        # ------------------------------------------------------------------ Contact & hours
        contact = ContactSettings.get()
        contact.phone_1 = "09160103097"
        contact.phone_2 = "07060670647"
        contact.phone_3 = "09021077966"
        contact.email_1 = "spakhub@gmail.com"
        contact.working_hours = "Monday – Saturday: 9:00 AM – 5:00 PM"
        contact.office_hours = "Monday – Saturday: 9:00 AM – 5:00 PM"
        contact.office_hours_closed = "Sunday: Closed · Public Holidays: Closed"
        contact.coworking_hours = "Monday – Saturday: 9:00 AM – 9:00 PM"
        contact.coworking_hours_closed = "Sunday & Public Holidays: 11:00 AM – 6:00 PM"
        contact.save()

        # ------------------------------------------------------------------ About CMS page
        CmsPage.objects.update_or_create(
            slug="about",
            defaults={
                "title": "About SPAK Innovation Hub",
                "summary": TAGLINE,
                "content": f"{ABOUT_PARA_1}\n\n{ABOUT_PARA_2}\n\n\n<strong>{MANTRA}</strong>",
                "is_published": True,
            },
        )

        # ------------------------------------------------------------------ Homepage sections (render order)
        site_sections = [
            ("hero", "Where ideas move forward", ABOUT_PARA_1, "Book a Space", "/facilities/", 10),
            ("about", "About SPAK Innovation Hub", f"{ABOUT_PARA_1}\n\n{MANTRA}", "Learn More About Us", "/about/", 15),
            ("services", "Our Services", "Flexible workspaces, virtual offices, meeting rooms, programmes and more — all in one place.", "All services", "/services/", 25),
            ("programmes", "Programmes & Training", "Learning, building and growing together.", "View programmes", "/programmes/", 30),
            ("facilities", "Spaces & Facilities", "Built for working, meeting and creating.", "Browse spaces", "/facilities/", 40),
            ("team", "Our Team", "The people behind SPAK Innovation Hub.", "Meet the team", "/team/", 50),
            ("news", "News & Updates", "Stories from the hub.", "Read the blog", "/blog/", 60),
            ("cta", "Ready to build what's next?", "Book a space, run a programme or talk to the SPAK team.", "Contact SPAK", "/contact/", 70),
        ]
        for key, title, subtitle, cta_text, cta_link, order in site_sections:
            HomepageSection.objects.update_or_create(
                key=key,
                defaults={"title": title, "subtitle": subtitle, "content": "", "cta_text": cta_text, "cta_link": cta_link, "sort_order": order, "is_active": True},
            )

        # ------------------------------------------------------------------ Privacy & terms CMS pages
        CmsPage.objects.update_or_create(
            slug="privacy-policy",
            defaults={"title": "Privacy Policy", "summary": "How SPAK Innovation Hub handles your data.", "content": "This policy will be published by SPAK management.", "is_published": True},
        )
        CmsPage.objects.update_or_create(
            slug="terms-of-use",
            defaults={"title": "Terms of Use", "summary": "Rules for using this website.", "content": "These terms will be published by SPAK management.", "is_published": True},
        )

        # ------------------------------------------------------------------ Facility categories
        cat_specs = [
            ("Co-working", "Shared workspaces for working, meeting and connecting."),
            ("Virtual Office", "A professional business address for remote teams and start-ups."),
            ("Conference & Events", "A hall for conferences, events and workshops."),
            ("Meeting Rooms", "Private rooms for small meetings and calls."),
        ]
        cats = {}
        for name, desc in cat_specs:
            c, _ = FacilityCategory.objects.get_or_create(name=name, defaults={"description": desc, "is_active": True, "sort_order": cats.__len__()})
            cats[name] = c

        # ------------------------------------------------------------------ Facilities (approved info only — no invented prices)
        facility_specs = [
            (
                "Co-working Space", cats["Co-working"],
                "A shared workspace with round-table seating for up to 50 people, electricity/solar power available 24/7 and refreshments on request.",
                FACILITY_FEATURES, 50,
                "Monday – Saturday: 9:00 AM – 9:00 PM · Sunday & Public Holidays: 11:00 AM – 6:00 PM", 10,
            ),
            (
                "Virtual Office Services", cats["Virtual Office"],
                "A professional business address for remote teams and start-ups.",
                [], None,
                "Available 24/7", 20,
            ),
            (
                "Conference / Event Hall", cats["Conference & Events"],
                "A hall for conferences, events and workshops, seating up to 50 people.",
                FACILITY_FEATURES, 50,
                "Bookable — confirm dates and current rates with SPAK management.", 30,
            ),
            (
                "Meeting Room", cats["Meeting Rooms"],
                "A private meeting room for small teams of up to 10 people.",
                FACILITY_FEATURES, 10,
                "Monday – Saturday: 9:00 AM – 5:00 PM · confirm at booking.", 40,
            ),
        ]
        for name, category, overview, features, capacity, availability, order in facility_specs:
            Facility.objects.update_or_create(
                name=name,
                defaults={
                    "category": category, "overview": overview, "features": features,
                    "capacity": capacity, "availability_text": availability,
                    "status": "published", "is_featured": True, "sort_order": order,
                    "created_by": admin,
                },
            )

        # Hide any leftover placeholder/demo facilities from the public site.
        Facility.objects.filter(name__icontains="[DEMO]").update(status="archived", is_featured=False)

        # ------------------------------------------------------------------ Services (the seven official services)
        service_specs = [
            ("Co-working Space Booking", "bi-person-workspace", "Book a seat or a day in SPAK's co-working space — round-table seating, 24/7 electricity/solar and refreshments on request.", "Book Now", "/facilities/", 10),
            ("Virtual Office Services", "bi-briefcase", "A professional business address that works around the clock for remote teams and start-ups.", "Make Enquiry", "/contact/", 20),
            ("Conference / Event Hall Booking", "bi-calendar-event", "A 50-capacity hall for conferences, events and workshops, with refreshments on request.", "Book Now", "/facilities/", 30),
            ("Hub Programmes, Events and Activities", "bi-people", "Programmes, events and activities run by the hub to develop skills and encourage innovation.", "Explore Programmes", "/programmes/", 40),
            ("Other Available Hub Services and Facilities", "bi-grid", "Other services and facilities available at the hub — ask us what we can support.", "Make Enquiry", "/contact/", 50),
            ("Training / Workshop Facilities", "bi-mortarboard", "Spaces and support for training and workshops.", "Explore Programmes", "/programmes/", 60),
            ("Meeting Room Booking", "bi-door-open", "A private meeting room for small teams of up to 10 people.", "Book Now", "/facilities/", 70),
        ]
        for name, icon, short, cta_label, cta_link, order in service_specs:
            Service.objects.update_or_create(
                name=name,
                defaults={
                    "icon": icon, "short_description": short,
                    "full_description": short,
                    "cta_label": cta_label, "cta_link": cta_link,
                    "is_published": True, "is_featured": name in {
                        "Co-working Space Booking", "Virtual Office Services",
                        "Conference / Event Hall Booking", "Meeting Room Booking",
                    },
                    "sort_order": order,
                },
            )

        # Unpublish any leftover placeholder/demo services.
        Service.objects.filter(name__icontains="[DEMO]").update(is_published=False)

        self.stdout.write(self.style.SUCCESS("\nOfficial content ready. Logins:"))
        self.stdout.write(f"  Super Admin   ->  user 'admin'  password '{admin_password}'")
        self.stdout.write(f"  Programme Lead->  user 'lead'   password '{lead_password}'")
        self.stdout.write(f"  Content Staff ->  user 'writer' password '{writer_password}'")
        self.stdout.write("Content is Admin-editable under /admin/. Run:  .venv/bin/python manage.py runserver")