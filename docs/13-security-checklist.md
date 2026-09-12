# SPAK Innovation Hub — Security Checklist

Status refers to the current MVP implementation. Items marked **[verify at deploy]** are environment
tasks for whoever deploys the live site.

## Authentication & sessions
- [x] Passwords stored with Django's hashed backend (PBKDF2SHA256 default), never plaintext.
- [x] Login rate-limited at `10/minute` per IP (`django-ratelimit`, blocks on exceed).
- [x] Booking, facility-enquiry and contact forms rate-limited (20/h and 30/h per IP).
- [x] Login/logout events written to the audit log.
- [x] Session cookie: `HttpOnly`, `SameSite=Lax`.
- [x] CSRF cookies: `SameSite=Lax`; CSRF enforced on every POST.
- [x] `must_change_password` flag forces first-login password change for non-super users.

## Authorization (role-based access control)
- [x] Server-side decorators on every admin/dashboard view:
      `super_admin_required`, `programme_lead_required`, `content_staff_required`.
- [x] Anonymous access to restricted areas → redirect to login (302), never 500.
- [x] Authenticated users without the right role → HTTP 403 (custom `templates/403.html`).
- [x] Programme editing restricted to the owning Lead (super admin override).
- [x] Content staff may only edit their own posts.
- [x] Programme Lead **cannot** reach facilities/prices/settings/users (verified by tests).
- [x] Object-level checks in addition to role checks (e.g. enquiry/registration ownership).

## Input validation & injection
- [x] Django forms with field validation on all inputs (public + admin + dashboards).
- [x] Dates/times validated (no past dates, end after start).
- [x] File uploads limited (`MAX_UPLOAD_SIZE_MB`, default 8 MB).
- [x] User content rendered with Django auto-escaping; no `|safe` on free-text user input.

## Transport & headers
- [x] `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`,
      `Permissions-Policy: camera=(), microphone=(), geolocation=()` applied by middleware.
- [x] Content-Type nosniff applied when `DEBUG=false`.
- [x] HSTS enabled when `DEBUG=false` (`DJANGO_HSTS_SECONDS`).
- [x] **[verify at deploy]** `SECURE_SSL_REDIRECT=true` behind a TLS-terminating proxy.

## Data protection
- [x] Secret key stored in `.env` (git-ignored).
- [x] No secrets logged; the audit-log anonymises IP to 45 chars.
- [x] Audit trail for create/update/approve/delete on all major entities.
- [x] Booking/enquiry ref numbers are unguessable UUID fragments.
- [x] **[verify at deploy]** Backups (DB dump + `media/`) and restricted file ownership.

## Rate limiting & abuse
- [x] Login: `10/m`. Bookings: `20/h`. Enquiries + contact: `30/h` (per IP).
- [x] **[verify at deploy]** Optionally front with Nginx `limit_req`.

## Housekeeping
- [x] `manage.py check` and `manage.py check --deploy` run during deployment.
- [x] Seed passwords are demo-only; swap to real ones before launch.
- [x] Before launch: remove/replace all `[DEMO]` and `[PLACEHOLDER]` content via the admin UI,
      media library and CMS pages.