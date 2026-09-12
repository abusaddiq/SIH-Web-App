import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "Seed SPAK Innovation Hub with super admin users and clearly labelled [DEMO] placeholder content."

    def add_arguments(self, parser):
        parser.add_argument("--no-input-reset", action="store_true", help="Do not reset demo passwords if users already exist.")

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding SPAK Innovation Hub demo data…")

        from core.models import (
            WebsiteSettings, ContactSettings, HomepageSection, CmsPage,
        )
        from facilities.models import FacilityCategory, Facility, FacilityPrice, Service, Enquiry, Booking
        from programmes.models import ProgrammeCategory, Person, Programme
        from blog.models import Category, Tag, Post

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

        ws = WebsiteSettings.get()
        ws.programme_approval_required = True
        ws.content_staff_enabled = True
        ws.ai_enabled = True
        ws.save(update_fields=["programme_approval_required", "content_staff_enabled", "ai_enabled"])

        contact = ContactSettings.get()
        contact.address = "[DEMO] Example Avenue, Nairobi"
        contact.phone_1 = "+254 700 000000"
        contact.email_1 = "hello@example.com"
        contact.working_hours = "Mon–Fri 8:00 AM – 6:00 PM"
        contact.save()

        site_sections = [
            ("hero", "SPAK Innovation Hub", "Where ideas become innovations. [DEMO]", "Explore our facilities", "/facilities/", 10),
            ("features", "Why join us?", "Open, flexible space designed for creators, startups and learners. [DEMO]", "Learn more", "/about/", 20),
            ("programmes", "Programmes & Training", "Hands-on skills to grow your career. [DEMO]", "View programmes", "/programmes/", 30),
            ("facilities", "Facilities", "Book meetings, studios and labs. [DEMO]", "Browse facilities", "/facilities/", 40),
            ("news", "News & Updates", "What's happening at the hub. [DEMO]", "Read the blog", "/blog/", 50),
            ("cta", "Get in touch", "We would love to host your next event. [DEMO]", "Contact us", "/contact/", 60),
        ]
        for key, title, subtitle, cta_text, cta_link, order in site_sections:
            HomepageSection.objects.get_or_create(
                key=key,
                defaults={"title": title, "subtitle": subtitle, "cta_text": cta_text, "cta_link": cta_link, "sort_order": order, "is_active": True},
            )

        CmsPage.objects.get_or_create(
            slug="privacy-policy",
            defaults={"title": "Privacy Policy", "summary": "[DEMO] How we handle your data.", "content": "[DEMO] This is placeholder privacy policy text. Replace it before launch.", "is_published": True},
        )
        CmsPage.objects.get_or_create(
            slug="terms-of-use",
            defaults={"title": "Terms of Use", "summary": "[DEMO] Rules for using the website.", "content": "[DEMO] This is placeholder terms of use text. Replace it before launch.", "is_published": True},
        )
        CmsPage.objects.get_or_create(
            slug="about",
            defaults={"title": "About SPAK", "summary": "[DEMO] About the hub.", "content": "[DEMO] This is placeholder about-page text. Replace it before launch.", "is_published": True},
        )

        court_cat, _ = FacilityCategory.objects.get_or_create(name="Workshop Studios [DEMO]", defaults={"description": "Makerspace and fabrication studios."})
        meet_cat, _ = FacilityCategory.objects.get_or_create(name="Meeting & Event Rooms [DEMO]", defaults={"description": "Conference and collaborative rooms."})
        other_cat, _ = FacilityCategory.objects.get_or_create(name="Other Spaces [DEMO]", defaults={"description": "Flexible open spaces."})

        facility_specs = [
            (court_cat, "Makerspace Studio [DEMO]", "A fully equipped craft studio.", ["3D printers", "Laser cutter", "Hand tools"], 20, "Mon–Sat, bookable hourly"),
            (court_cat, "Design & Print Studio [DEMO]", "Graphics and print prototyping space.", ["Printing press", "Cutting mats", "Large format printer"], 12, "Bookable daily"),
            (meet_cat, "Meeting Room A [DEMO]", "Seats 10, with display screen.", ["4K display", "Whiteboard", "Video conferencing"], 10, "8 AM – 8 PM"),
            (meet_cat, "Boardroom [DEMO]", "Premium boardroom for workshops.", ["Round table", "Projector", "Refreshments on request"], 24, "By arrangement"),
            (other_cat, "Open Innovation Area [DEMO]", "Open co-working style space.", ["Hot desks", "Lounge", "Free Wi-Fi"], 60, "During working hours"),
        ]
        for cat, name, overview, features, capacity, availability in facility_specs:
            fac, created = Facility.objects.get_or_create(name=name, defaults={
                "category": cat, "overview": overview, "features": features,
                "capacity": capacity, "availability_text": availability,
                "status": "published", "created_by": admin, "is_featured": cat is court_cat,
            })
            if not created:
                continue
            default_amount = 15_000 if fac is not None and cat is court_cat else 8_000
            price_amount = {"Meeting Room A [DEMO]": 8_000, "Boardroom [DEMO]": 20_000, "Open Innovation Area [DEMO]": 12_000}.get(name, 15_000)
            FacilityPrice.objects.get_or_create(facility=fac, price_type="daily", defaults={"amount": price_amount, "currency": "KES", "billing_period": "per day", "is_active": True})

        service_specs = [
            ("Product Design Support [DEMO]", "bi-pencil-square", "Guidance to take your product from idea to prototype.", "Contact SPAK for pricing"),
            ("Prototyping & Fabrication [DEMO]", "bi-tools", "Bring your concept to life with our equipment.", "From KES 2,000/week"),
            ("Business Advisory [DEMO]", "bi-briefcase", "One-on-one sessions for startups and freelancers.", "Contact SPAK for pricing"),
            ("Events Hosting [DEMO]", "bi-calendar-event", "Host your workshop, bootcamp or meetup with us.", "From KES 20,000/day"),
        ]
        for name, icon, short, price_text in service_specs:
            Service.objects.get_or_create(name=name, defaults={"icon": icon, "short_description": short, "price_text": price_text, "is_published": True})

        prog_cats = [
            ("Innovation & Skills [DEMO]", "Learn practical innovation skills."),
            ("Entrepreneurship [DEMO]", "Build and grow a business."),
            ("Creative & Digital [DEMO]", "Digital media and creative tools."),
        ]
        for name, desc in prog_cats:
            ProgrammeCategory.objects.get_or_create(name=name, defaults={"description": desc, "is_active": True})

        person_specs = [
            ("Jane Demo Trainer [DEMO]", "Trainer", "trainer", "Design thinking, facilitation."),
            ("Bob Demo Facilitator [DEMO]", "Facilitator", "facilitator", "Workshop facilitation."),
            ("Ana Demo Speaker [DEMO]", "Speaker", "speaker", "Innovation talks and panels."),
        ]
        for name, title, kind, bio in person_specs:
            Person.objects.get_or_create(name=name, defaults={"title": title, "kind": kind, "bio": bio})

        cat_accel = ProgrammeCategory.objects.get(name="Innovation & Skills [DEMO]")
        trainer = Person.objects.get(name="Jane Demo Trainer [DEMO]")

        pub_prog, created = Programme.objects.get_or_create(
            title="Design Thinking Bootcamp [DEMO]", defaults={
                "category": cat_accel, "short_description": "A 2-day hands-on introduction to design thinking. [DEMO]",
                "full_description": "[DEMO] This event is placeholder content. Replace details before launch.",
                "programme_type": "physical", "venue": "[DEMO] Boardroom, SPAK Innovation Hub",
                "start_date": (timezone.localdate() + timezone.timedelta(days=14)),
                "end_date": (timezone.localdate() + timezone.timedelta(days=15)),
                "start_time": timezone.now().time(), "end_time": (timezone.now() + timezone.timedelta(hours=2)).time(),
                "target_audience": "Students, startups and professionals",
                "max_participants": 24, "registration_deadline": (timezone.localdate() + timezone.timedelta(days=12)),
                "status": "published", "created_by": lead, "approved_by": admin, "published_at": timezone.now(),
            },
        )
        if created:
            pub_prog.trainers.add(trainer)

        sub_prog, created = Programme.objects.get_or_create(
            title="Intro to Digital Fabrication [DEMO]", defaults={
                "category": cat_accel, "short_description": "Learn the basics of 3D printing and laser cutting. [DEMO]",
                "full_description": "[DEMO] Placeholder programme content.",
                "programme_type": "physical", "venue": "[DEMO] Makerspace Studio",
                "start_date": (timezone.localdate() + timezone.timedelta(days=30)),
                "end_date": (timezone.localdate() + timezone.timedelta(days=30)),
                "status": "submitted", "created_by": lead,
            },
        )

        Programme.objects.get_or_create(
            title="Freelance Foundations Draft [DEMO]", defaults={
                "category": cat_accel, "short_description": "A draft programme not yet submitted. [DEMO]",
                "programme_type": "online",
                "start_date": (timezone.localdate() + timezone.timedelta(days=60)),
                "status": "draft", "created_by": lead,
            },
        )

        from programmes.models import ProgrammeRegistration, ProgrammeEnquiry
        ProgrammeRegistration.objects.get_or_create(
            programme=sub_prog, full_name="Dennis Applicant [DEMO]", email="a@example.com", phone="0700000000",
        )
        ProgrammeEnquiry.objects.get_or_create(
            programme=sub_prog, name="Mary Inquirer [DEMO]", email="m@example.com",
            message="Please let me know the full dates and fees. [DEMO]",
        )

        news_cat, _ = Category.objects.get_or_create(name="News [DEMO]")
        tag_launch, _ = Tag.objects.get_or_create(name="launch")
        tag_events, _ = Tag.objects.get_or_create(name="events")

        demo_post, created = Post.objects.get_or_create(
            title="Welcome to the SPAK Innovation Hub website [DEMO]",
            defaults={
                "excerpt": "Placeholder welcome post for the demo. [DEMO]",
                "content": "[DEMO] This is placeholder content for the demo. Replace with real news before launch.",
                "category": news_cat, "author": writer, "status": "published", "published_at": timezone.now(),
            },
        )
        if created:
            demo_post.tags.add(tag_launch, tag_events)

        Post.objects.get_or_create(
            title="Upcoming workshops at the hub [DEMO]",
            defaults={
                "excerpt": "Placeholder news about upcoming workshops. [DEMO]",
                "content": "[DEMO] Placeholder content.",
                "category": news_cat, "author": writer, "status": "published", "published_at": timezone.now(),
            },
        )
        Post.objects.get_or_create(
            title="Draft announcement [DEMO]",
            defaults={
                "excerpt": "Draft post to demonstrate the workflow. [DEMO]",
                "content": "[DEMO] Draft content.",
                "category": news_cat, "author": writer, "status": "draft",
            },
        )

        Booking.objects.get_or_create(
            full_name="Faith Booker [DEMO]", email="f@example.com", phone="0700000000",
            facility=Facility.objects.get(name="Meeting Room A [DEMO]"),
            preferred_date=timezone.localdate() + timezone.timedelta(days=7),
            participants=6, purpose="Project team sync", status="pending",
        )
        Enquiry.objects.get_or_create(
            name="Paul Enquirer [DEMO]", email="p@example.com",
            subject="Do you host public hackathons?", message="Please share details. [DEMO]", status="new",
        )

        self.stdout.write(self.style.SUCCESS("\nSeed data ready. Logins:"))
        self.stdout.write(f"  Super Admin   ->  user 'admin'  password '{admin_password}'")
        self.stdout.write(f"  Programme Lead->  user 'lead'   password '{lead_password}'")
        self.stdout.write(f"  Content Staff ->  user 'writer' password '{writer_password}'")
        self.stdout.write("All placeholder content is labelled [DEMO]. Run:  .venv/bin/python manage.py runserver")