# 16 — Sprint 2 handover: content, staff, facility images, dark mode

Covers the content-update + feature-extension sprint delivered against the SPAK
Innovation Hub Django app. Owners: the SPAK hub team (approved content) and
the development team (implementation).

## Deliverables

1. **Official content (CMS-managed, no code edits needed to change)**
   - Brand: tagline *"A place where ideas move forward."*, About copy + mantra
     *"Connect. Create. Collaborate. Grow."* set via `seed_demo` and editable in
     the admin shell (Settings → Website / Contact) and CMS pages.
   - Contacts: 3 phones (`09160103097`, `07060670647`, `09021077966`), email
     `spakhub@gmail.com`, office hours *Mon–Sat 9:00 AM–5:00 PM, Sun & PH
     Closed*, co-working space hours *Mon–Sat 9:00 AM–9:00 PM, Sun & PH 11 AM–6 PM*.
   - Services: 7 official services with icons, short descriptions and per-service
     CTA label/link (`Service.cta_label`, `Service.cta_link`).
   - Facilities: 4 official spaces (Co-working Space, Virtual Office Services,
     Conference / Event Hall, Meeting Room). No prices were invented — pricing is
     unset on the public pages until management publishes prices.

2. **Staff / Our Team module**
   - New `staff` Django app: `StaffMember` (role, profession, department,
     phone, email, bio, profile image, LinkedIn, social links, display order,
     active flag) with admin CRUD, reorder, activate/deactivate, delete.
   - Backend: all staff admin actions are Super-Admin only (`@super_admin_required`),
     audit-logged, and visible on `/admin/staff/`.
   - Public: homepage "Our Team" section (active members, ordered) and `/team/`
     page with person cards (photo or initials avatar, contact links).

3. **Facility image management (admin + public)**
   - `FacilityImage` model (facility FK, image file, alt text, caption, sort
     order, active, primary flag — one primary per facility).
   - Admin: `/admin/facilities/<pk>/images/` upload (multiple files, optional
     caption, "make first image main"), reorder up/down, edit, delete, "Set main"
     (syncs the facility's `primary_image` file field used as the featured photo).
   - Public: facility detail page now shows a photo gallery under the featured image.

4. **Dark / Light mode**
   - Theme toggle in the header (moon/sun). Preference persisted in
     `localStorage` (`spak-theme`); default honours the OS `prefers-color-scheme`.
     A pre-paint script in `base.html` prevents a flash of the wrong theme.
     Dark tokens + component overrides live at the end of `static/css/spak.css`.

5. **Reliability / ops fixes**
   - `templates/500.html` rewritten standalone (no context vars) so Django's
     `server_error` handler stops recursing.
   - Static and media files are now served in production (`DEBUG=false`) via
     explicit URL routes in `config/urls.py` (`static/<path:path>` and
     `media/<path:path>`), since WhiteNoise is not installed.
   - `deploy.sh` PostgreSQL bootstrap updated from the unusable 5433 user-cluster
     to the `spak_postgres` container on port 5432.

## Database / infrastructure note (IMPORTANT)

- PostgreSQL runs in a podman/docker container `spak_postgres`
  (`-p 5432:5432`, DB `spak_hub`, user `engr`, trust auth, volume
  `spak_postgres_data`). `.env` sets `DB_PORT=5432`.
- The previous system cluster (port 5433) cannot be started without root and its
  data was **not** recoverable; the database was rebuilt and official content
  regenerated with `manage.py seed_demo`. Any data entered into the old cluster
  (users except admin/lead/writer, blog posts, bookings, etc.) was lost.
- To restart the stack after a reboot:
  ```bash
  docker start spak_postgres          # waits for postgres readiness
  cd "/home/engr/Desktop/SIH Web App"
  setsid nohup .venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8077 \
    --workers 3 --timeout 60 --pid run/spak-gunicorn.pid \
    --access-logfile - --error-logfile - </dev/null >> logs/spak-gunicorn.log 2>&1 &
  env DJANGO_DEBUG=false .venv/bin/python manage.py runserver 0.0.0.0:8000 --noreload \
    </dev/null >> logs/spak-dev.log 2>&1 &
  ```

## Verification

- Tests: `.venv/bin/python manage.py test --settings config.settings_test`
  (15 tests — auth/RBAC, public pages incl. `/team/`, booking, content
  publishing, staff CRUD+toggle+move+delete, facility-image RBAC/upload/
  reorder/primary-sync, public gallery).
- Spot-checked on the running site: public pages 200; admin staff / facility
  images / contact settings 200 for Super Admin and 403 for the Programme Lead;
  static CSS/JS served on the 8077 gunicorn port.

## Re-run seed (only when needed)

```bash
env DJANGO_DEBUG=false .venv/bin/python manage.py seed_demo
```
Seeding requires confirmation when users already exist; it only enforces
official content on first empty seed. Current seeded demo staff members carry a
`[DEMO]` marker — replace them with the real team via `/admin/staff/` when the roster is available.