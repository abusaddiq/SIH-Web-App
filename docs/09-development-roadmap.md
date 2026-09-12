# SPAK Innovation Hub — Development Roadmap (MVP)

Phase # phases build order, each with verification.

| Phase | Deliverable | Verification |
|---|---|---|
| 0 | Docs 01–09 (analysis/architecture/schema/roles/sitemap/journeys/UI) | review |
| 1 | Django project bootstrap + PostgreSQL DB + env config + static/media setup | server boots |
| 2 | Core models + migrations (accounts, core, facilities, programmes, blog) | migrate ok |
| 3 | Auth + RBAC + role seed + permission decorators/classes | login/logout, 403 cases |
| 4 | CMS: site settings, contact settings, homepage sections, media library, branding | settings pages persist |
| 5 | Public site: base template, home, about, services, facilities list/detail, co-working/virtual office/rooms/halls pages | browse all routes |
| 6 | Contact + booking + enquiry forms with validation + rate limiting | submit + stored |
| 7 | Blog public + management (Super Admin) | CRUD, publish/schedule |
| 8 | Programmes public + Programme Lead dashboard + approval workflow | programme lifecycle |
| 9 | Admin dashboard: KPI, facilities CRUD + prices + availability, services CRUD, booking/enquiry management, users, audit logs visibility | full admin CRUD |
| 10 | AI assistant abstraction + public chat (rule-based default) | chat over CMS data |
| 11 | Search (public + admin), notifications wiring, audit triggers | queries + logs |
| 12 | Seed demo data (labelled `[DEMO]`) + default super admin | app populated |
| 13 | Security pass (isolation, validation, headers, rate limits) | checklist `13-security-checklist.md` |
| 14 | Documentation 10–14 (install/deploy/env/guides) + testing report | docs present |
| 15 | End-to-end smoke test + serve on LAN/IP | acceptance walkthrough |

## MVP Acceptance (from spec §53)
Public site loads; nav works; logo shows; facilities + DB prices display; programmes + blog + contact work;
booking/enquiry forms work. Admin can log in, change logo/content/prices/facilities/bookings/enquiries/
blog/contact/users. Programme Lead has own dashboard, creates/trains/edits programmes, submits for approval,
and **cannot** touch prices/settings/users. Security: role guards return 403; passwords hashed; forms validated.

## Out of scope (future roadmap)
Payments, availability calendar/conflict detection, client accounts, LMS/certificates, memberships,
WhatsApp/email/SMS delivery, mobile app, analytics deep-dive.