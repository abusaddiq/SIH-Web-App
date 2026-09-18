# DEVELOPMENT_CONTEXT.md — SPAK Innovation Hub

## Project summary

Django 5 content-managed website + staff dashboards for SPAK Innovation Hub
(Nigeria). Public pages + three server-rendered admin roles. No React/Node —
the frontend is Django templates + Bootstrap 5 (vendored, no CDN).

## Running locally

| Port | Server | Purpose |
|------|--------|---------|
| 8077 | Gunicorn | Production-like server (`DJANGO_DEBUG=false`) |
| 8000 | `manage.py runserver` | Dev server (auto-reload OFF in the deployed test scripts; set `DJANGO_DEBUG=true` if you want reload) |

Static/media served in production via explicit URL routes in `config/urls.py`
(no WhiteNoise installed).

## Infrastructure (postgres)

- Container: `spak_postgres` (podman/docker, image `postgres:15-alpine`)
- Port: **5432** (host)
- DB/user/pass: `spak_hub` / `engr` / (empty — trust auth)
- Volume: `spak_postgres_data`
- `.env` values: `DB_NAME=spak_hub`, `DB_USER=engr`, `DB_PORT=5432`,
  `DB_PASSWORD=` (empty), `DJANGO_DEBUG=false`
- **IMPORTANT:** The old user-owned cluster (port 5433) and its data are gone
  and cannot be recovered (sudo needed). This DB was rebuilt; `seed_demo`
  regenerates official content.

## Test run

```bash
.venv/bin/python manage.py test --settings config.settings_test
```

Currently 15 tests covering RBAC, public pages, booking, programme workflow,
content publishing, staff CRUD, facility images, and public gallery.

## App structure (key modules)

| App | Purpose |
|-----|---------|
| `accounts` | Custom User model, roles (`ROLE_SUPER_ADMIN`, `ROLE_PROGRAMME_LEAD`, `ROLE_CONTENT_STAFF`), login/password |
| `core` | WebsiteSettings/ContactSettings singletons, CmsPage, MediaItem, audit_log, notifications, RBAC helpers |
| `facilities` | Facility + FacilityCategory + FacilityPrice + FacilityImage, Service (CTA fields), Booking, Enquiry |
| `programmes` | Programme, ProgrammeRegistration, lead dashboard, approval workflow |
| `blog` | Post, Tag, admin + content-staff authoring |
| `public` | Public views (home, about, team, services, facilities, contact, search, AI chat) |
| `staff` | StaffMember (CMS-driven team page + homepage section) |

## Key URLs

| Path | Who |
|------|-----|
| `/` | Homepage (team preview, services, facilities, testimonials) |
| `/about/`, `/team/`, `/services/`, `/facilities/<slug>/`, `/programmes/`, `/contact/`, `/search/` | Public |
| `/admin/` | Super Admin dashboard |
| `/admin/facilities/`, `/admin/facilities/<pk>/images/`, `/admin/facilities/<pk>/prices/` | Super Admin only |
| `/admin/staff/`, `/admin/staff/new/`, `/admin/staff/<pk>/` | Super Admin only |
| `/admin/settings/site/`, `/admin/settings/contact/` | Super Admin only |
| `/programmes-dashboard/` | Programme Lead + Super Admin |
| `/content-dashboard/` | Content Staff + Programme Lead (posts) + Super Admin |

## Theme / dark mode

- Toggle button in header (`#themeToggle`)
- localStorage key: `spak-theme` (`"dark"` / `"light"`)
- A pre-paint inline script in `base.html` reads the preference to prevent flash
- Dark overrides: end of `static/css/spak.css` (section 26)

## Approved official content

Loaded by `manage.py seed_demo`. Key facts (official profile, source of truth):

- Slogan: *"Innovating for People and Planet"*; brand expression: *"Connect • Collaborate • Create"*
- Legal name: **SPAK Innovation Hub Ltd/GTE** (CAC-registered 2024)
- Email: `spakhub@gmail.com`
- Address: `CVL02, Dr Sanda Street, 2nd Gate, Janbulo Kabuga Housing Estate, Kano, Nigeria`
- Phones: `09160103097`, `07060670647`, `09021077966` (maintained from earlier approved content)
- Office hours: Mon–Sat 9:00 AM–5:00 PM; Sun & PH Closed
- Co-working hours: Mon–Sat 9:00 AM–9:00 PM; Sun & PH 11:00 AM–6:00 PM
- About copy: official organisational profile (paragraphs from the SPAK profile PDF) + *"Connect • Collaborate • Create"*
- Vision, Mission, 8 Objectives and 6 Core Values from the official profile
- 7 official services, 4 official facilities (no prices invented), 4 features (round table, refreshment on request, electricity/solar 24/7, functional toilet)
- 6 Key Activities and 3 Flagship Projects (SpakCare, SpakRecycle, Talynq) — see `/projects/`

## Conventions / gotchas

- Staff admin views all use the `@super_admin_required` decorator
- FacilityImage.is_primary has a partial unique constraint per facility
- `Facility.primary_image` is an **ImageField** (file), not an FK — when syncing
  with FacilityImage.is_primary, assign `facility.primary_image = facilityimage.image`
- Bare `<path>` in a Django URL route defaults to the `str` converter (`[^/]+`);
  write `<path:path>` explicitly to capture slashes
- `templates/500.html` must not reference template context variables
- Unused `from django.contrib import messages` and `from django.urls import reverse`
  in `core/tests.py` are legacy and harmless
