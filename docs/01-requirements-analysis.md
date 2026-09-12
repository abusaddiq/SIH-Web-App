# SPAK Innovation Hub Digital Platform — Requirements Analysis (MVP)

*Status: MVP design baseline. Companion: `02-requirements-to-confirm.md` (items requiring official SPAK confirmation).*

## 1. Purpose
A professional, responsive, database-driven digital platform for SPAK Innovation Hub that combines a
public-facing website with a secure, role-based management system. Non-technical SPAK staff must be
able to update website content, branding, facilities, prices, services, programmes, blog, and contact
information **from the dashboard — without touching source code**.

## 2. Business Rules (must never be violated)
1. Only Super Admin manages facilities and facility prices.
2. Programme & Training Lead manages programmes/training only; never facility prices, core website settings, or users.
3. All prices, contact info, branding, content come from the database — never hard-coded.
4. A booking submission is a *request*, not a confirmation. Confirmation only after Admin approval.
5. No invented official SPAK information; placeholder content is clearly marked.
6. RBAC is enforced server-side, not only in the UI.
7. No payment functionality in the MVP (architecture reserved for future).

## 3. Stakeholders & Users
| Role | Access |
|---|---|
| Public visitor / client | Public website only |
| Super Admin / Hub Administrator | `/admin` full control |
| Programme & Training Lead | `/programmes-dashboard` |
| Content & Communication Staff (optional) | Blog/news limited, if enabled |

## 4. Functional Requirements Summary
- **Public**: Home, About, Services, Facilities (list + detail), Co-working, Virtual Office, Meeting Rooms,
  Conference/Event Hall, Programmes, Training, Blog, Blog post, Contact, Search, Booking form, Enquiry forms, AI assistant.
- **Admin (Super Admin)**: dashboard with statistics; full CRUD for website/branding/settings, facilities &
  prices & availability, services, bookings (review/approve/reject/cancel/complete + notes), enquiries
  (read/reply/status/archive), users & roles, blog (posts/categories/tags/drafts/schedule), programmes
  (view/publish), media library, audit logs, SEO, notifications config.
- **Programme Lead**: separate dashboard; create/edit/cancel/archive programmes & training, manage trainers/
  facilitators/speakers, registration fields, submit-for-review workflow, programme enquiries/registrations.
  No access to facilities pricing or system settings.
- **Content Staff (optional flag)**: blog/news/announcements only.

## 5. Non-Functional Requirements
- Security: hashed passwords, RBAC middleware, CSRF, XSS-safe templates, ORM (SQLi safe), validated file
  uploads, rate-limited forms, audit logging, protected admin routes.
- Responsive: mobile-first (phone/tablet/laptop/desktop).
- UX: clean, modern innovation-hub aesthetic; minimal animation; strong typography; clear CTAs; accessibility.
- SEO: dynamic titles, meta descriptions, Open Graph, sitemap, robots, slugs, alt text.
- Maintainability: modular Django apps, migrations, env-based config, no secrets in source.
- Notifications: architecture supports email/WhatsApp/SMS later; internal in-app notifications now.

## 6. Data Modelling Notes
Relational models for: Users, Roles, Permissions, Facilities, Facility Categories, Facility Prices,
Services, Bookings, Enquiries, Programmes, Programme Categories, Trainers/Facilitators, Blog Posts,
Blog Categories/Tags, Media, Website Settings, Contact Settings, Homepage Sections, Notifications, Audit Logs.
Normalized, FK-based, no duplicated data.

## 7. Booking & Enquiry Workflow
`Facility → view → Book Now → form → submit (status Pending) → DB record → Admin review → Approved /
Rejected / More Info / Cancelled / Completed`. Contact form submissions stored and managed by Admin.

## 8. Programme Approval Workflow (configurable)
`Draft → Submit for Review → Admin approves (if approval required) → Publish`. Configurable toggle in settings.

## 9. MVP Scope / Out of Scope
- **In**: everything listed in §4.
- **Out (future)**: payments/invoices/receipts, real-time availability calendar & conflict detection,
  client accounts with login, LMS, certificates, membership subscriptions, mobile app, WhatsApp bot,
  email/SMS delivery (interface stubbed).

## 10. Deployment
Single Django app instance + PostgreSQL. Production via WSGI (gunicorn) behind HTTPS reverse proxy
(nginx/Caddy). Env-based secrets. Scheduled DB backups. See `11-deployment-guide.md`.