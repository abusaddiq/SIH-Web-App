# SPAK Innovation Hub — System Architecture

## 1. Stack Decision
| Layer | Choice | Rationale |
|---|---|---|
| Backend / Framework | Django 5 (Python) | Built-in secure auth, admin customsable, ORM, migrations, forms validation, CSRF/XSS/SQLi protection, mature CMS ecosystem |
| Database | PostgreSQL 15 | Relational, FK constraints, robust migrations, production-ready |
| Frontend | Server-rendered Django templates + Bootstrap 5 (custom theme) | Fast, SEO-friendly, accessible, no heavy JS build step; mobile-first |
| Routing | Django URL conf + slugs | SEO-friendly URLs |
| Files/Media | Django `MEDIA_ROOT` uploads | Logo, favicon, images; future S3/ObjectStorage swap via Django storage backend |
| AI Assistant | Provider abstraction (`AIProvider` interface) | Default: rule-based over CMS data; swappable to OpenAI/Anthropic/etc. later (env config) |
| Notifications | `NotificationService` + model `InAppNotification` | Email/WhatsApp/SMS provider stubs; configurable later |
| Auth/RBAC | Django auth + custom permission checks | Server-side enforcement on every protected view |

## 2. Environment
- Local dev: `runserver`, dev DB creds via `.env`, SQLite not used — PostgreSQL from the start (parity with prod).
- Production: gunicorn + nginx (HTTPS) + PostgreSQL; env-based secrets; no secrets in source (`.env` in `.gitignore`, `.env.example` committed).

## 3. Components (Django apps)
```
config/          project settings, urls, wsgi/asgi
accounts/        User model, roles, authentication views, permission helpers
core/            WebsiteSettings, ContactSettings, HomepageSection, Media, AuditLog, Notification, dashboard mixins
facilities/      Facility, FacilityCategory, FacilityPrice, FacilityImage, Service, Booking, Enquiry
programmes/      Programme, ProgrammeCategory, Trainer (Person), ProgrammeRegistration, ProgrammeEnquiry
blog/            Post, Category, Tag
public/          public-facing views (home, about, facilities detail, contact, search, AI chat)
```

## 4. Request Flow
```
Browser → nginx (HTTPS, static/media) → gunicorn (Django)
  → URLconf → View
      → Permission check (decorator/mixin) → Perform action via ORM (PostgreSQL)
      → Render template (server-side)  OR  Redirect/JSON
```
- Public views: permission = anonymous allowed.
- `/admin/...` views: require `is_authenticated` + role check.
- `/programmes-dashboard/...`: require Programme & Training Lead role (or superadmin).

## 5. Security Architecture
- Brute-force protection: rate limiting on login/contact/booking/enquiry (django-ratelimit or custom middleware).
- Sessions: `SESSION_COOKIE_HTTPONLY`, `SECURE` in prod, `SameSite=Lax`.
- File uploads: extension + content sniffing + size validation; stored outside web root with path checks.
- Audit log middleware for admin actions (actor, action, entity, timestamp, IP).
- Template autoescaping (XSS), ORM parameterization (SQLi), Django CSRF on all POST forms.

## 6. Data Flow: Booking & Programme Approval described in `01-requirements-analysis.md`.

## 7. Future Evolution
- Switch AI provider via env (`AI_PROVIDER`).
- Add EMAIL_/WHATSAPP_SMS_PROVIDER adapters behind existing `NotificationService` interface.
- Availability calendar: extend `FacilityPrice`/add `FacilitySlot` with conflict detection.
- Payments: add `Provider`/`Payment` models; gate by setting `PAYMENTS_ENABLED`.
- Static/S3: swap `STORAGES` backend.