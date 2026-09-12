# SPAK Innovation Hub — Testing Report (MVP)

## 1. Static checks

```
.venv/bin/python manage.py check               -> "System check identified no issues (0 silenced)"
.venv/bin/python manage.py migrate             -> "No migrations to apply" (all applied)
.venv/bin/python manage.py test --settings config.settings_test   -> 9 tests, all OK
```

> `config.settings_test` disables the IP rate-limiter (`RATELIMIT_ENABLE=False`) so the suite is
> hermetic. The rate-limiter stays active in normal/development runs.

## 2. Public site — live smoke test (via HTTP)

All returned HTTP 200 after acceptance build:

`/`, `/about/`, `/services/`, `/facilities/`, `/programmes/`, `/blog/`, `/contact/`,
`/search/?q=innov`, `/ai-chat/`, `/pages/privacy-policy/`, programme detail,
`/sitemap.xml`, `/robots.txt`.

## 3. RBAC matrix verification (HTTP status)

| Request | Anonymous | Programme Lead | Content Staff | Super Admin |
|---|---|---|---|---|
| `/admin/` and all `/admin/…` | 302 → login | 403 | 403 | 200 |
| `/programmes-dashboard/` | 302 → login | 200 | 403 | 200 |
| `/content-dashboard/` | 302 → login | 403 | 200 | 200 |
| `/my-account/` | 302 → login | 200 | 200 | 200 |

Verified with a full matrix script against the running dev server — every case matched.

## 4. Render-all URL test

Every named URL (51 patterns incl. detail/delete/create pages) was GET-rendered with the
correct role and produced no 5xx after the fixes below.

## 5. Workflow POST tests

- [x] Public booking submission (saved with ref, shows success page)
- [x] Public contact form (saved as Enquiry, source `contact`)
- [x] Admin booking status update (with audit + notification)
- [x] Admin reply to facility enquiry
- [x] Admin CMS page create
- [x] Admin programme approval → becomes public
- [x] Admin blog publish
- [x] Programme Lead create draft + submit for approval
- [x] Content Staff publish blog post → visible on `/blog/<slug>/`
- [x] Media library upload → saved to `media/` with size + mime
- [x] AI chat (`AI_PROVIDER=rules`, offline) returns CMS-data answer
- [x] My-account update + password change apply

## 6. Automated test suite

`manage.py test --settings config.settings_test` runs the suite in `core/tests.py`
(auth/RBAC, public pages, booking flow, programme approval flow, content publish flow)
— 9/9 passing.

## 7. Defects found & fixed during acceptance

| # | Defect | Fix |
|---|---|---|
| 1 | `core.middleware` module missing (WSGI would not boot) | Created `core/middleware.py` |
| 2 | `Facility.current_prices` filtered `status` but field is `is_active` | Filtered on `is_active=True` |
| 3 | Login URL inconsistency `/login/login/` in `LOGIN_URL` and views | Corrected to `/login/` |
| 4 | Anonymous `/admin/` raised 500 (`can_access_admin` on AnonymousUser) | Guarded with `is_authenticated` |
| 5 | Content-staff views lacked role decorators | Added `content_staff_required` |
| 6 | `admin_post_detail` lacked `super_admin_required` | Added decorator |
| 7 | `user_create` referenced missing `UserForm` import | Imported it |
| 8 | `programme_edit` called `save_m2m()` after `save()` → AttributeError | Removed double call |
| 9 | `PostForm.save(commit=False)` set M2M tags without pk → ValueError | Refactored to `save_extra_fields()` |
| 10 | `admin_dashboard_view` redirected to non-existent `admin_login` | Redirect to `login` |
| 11 | Meeting-rooms page filtered a slug the seed doesn't produce | Filter on category name (robust) |

## 8. Known limitations / not covered

- Email delivery not tested end-to-end (console backend in dev).
- No load/penetration testing (rate limits and middleware reduce the main risks).
- Cloud AI providers (OpenAI/Anthropic/Gemini) stubbed — only `rules` (offline) tested.