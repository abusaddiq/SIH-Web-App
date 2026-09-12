# SPAK Innovation Hub — Digital Platform

A content-managed website with role-based management dashboards for SPAK Innovation Hub.
Built with Django 5 and PostgreSQL.

## Highlights

- **Public site** — Home, About, Services, Facilities (with DB-driven prices), Meeting Rooms,
  Programmes & Training, Blog, Contact, Search, AI assistant, and CMS-editable pages
  (Privacy Policy, Terms, About…).
- **Three staff roles** with hardened, server-side access control:
  - **Super Admin** — everything in `/admin/` (facilities, prices, services, bookings,
    enquiries, programmes, blog, media, settings, users, audit logs, notifications).
  - **Programme & Training Lead** — own dashboard at `/programmes-dashboard/`: manages
    programmes, registrations, enquiries, trainers; submits programmes for Super Admin
    approval. **Cannot** touch prices, settings, or users.
  - **Content & Communication Staff** — `/content-dashboard/`: publish/unpublish blog posts
    (own posts only).
- **Workflows** — booking requests (never auto-confirmed), enquiry handling, programme
  approval, in-app notifications, and a full audit trail.
- **Security** — Django auth + role decorators (403 on violation), CSRF + rate limits on
  forms, security headers, required password change on first login, `.env` secrets.

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env            # adjust DB settings if needed

# PostgreSQL must be running (see docs/10-installation-guide.md)
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver
```

Demo logins (change immediately): `admin/admin12345` (Super Admin),
`lead/lead12345!` (Programme Lead), `writer/writer12345!` (Content Staff).
All placeholder content is labelled `[DEMO]` and should be replaced before launch.

## Tests

```bash
.venv/bin/python manage.py test --settings config.settings_test
```

## Documentation

Full documentation lives in [`docs/`](docs/):

| Doc | Topic |
|---|---|
| 01 | Requirements analysis |
| 02 | Requirements to confirm |
| 03 | System architecture |
| 04 | Database schema |
| 05 | Role–permission matrix |
| 06 | Sitemap |
| 07 | User journeys |
| 08 | UI/UX structure |
| 09 | Development roadmap |
| 10 | Installation guide |
| 11 | Deployment guide |
| 12 | Environment variables |
| 13 | Security checklist |
| 14 | Testing report |

## Structure

```
config/        project settings, URLs, WSGI/ASGI
accounts/      custom User/Role, auth views, admin user management
core/          settings singletons, CMS pages, media, audit log, notifications, RBAC
facilities/    facilities, prices, services, bookings, enquiries (admin + model)
programmes/    programmes, trainers, registrations, enquiries, lead dashboard, approval
blog/          categories/tags/posts, admin + content-staff management, public views
public/        public views, forms, AI assistant (rules provider), search
templates/     base + public + admin_shell + programmes_dash + auth templates
static/        CSS/JS + vendored Bootstrap 5 (no CDN dependency)
docs/          design & ops documentation (01–14)
```