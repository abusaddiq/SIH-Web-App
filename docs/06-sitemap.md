# SPAK Innovation Hub — Sitemap & URL Structure

## Public (anonymous)
| URL | Page |
|---|---|
| `/` | Home |
| `/about` | About SPAK |
| `/services` | Services |
| `/facilities` | All facilities |
| `/facilities/{slug}` | Facility detail (co-working, virtual office, meeting rooms, conference hall, …) |
| `/facilities/{slug}/book` | Facility booking form |
| `/programmes` | Programmes (upcoming/ongoing/past, filter by category) |
| `/programmes/{slug}` | Programme detail (Register/Enquire) |
| `/training` | Training activities |
| `/blog` | Blog list (search, category filter) |
| `/blog/{slug}` | Blog post |
| `/contact` | Contact page + form |
| `/search?q=` | Site-wide search |
| `/ai-chat` | AI assistant chat |
| `/legal/privacy-policy`, `/legal/terms-of-use` | Policy pages (CMS editable) |
| `/sitemap.xml`, `/robots.txt` | SEO |

## Admin — Super Admin (`/admin/...`, 403 for others)
`/admin/` (dashboard) · `/admin/facilities/` · `/admin/facilities/{id}/` · `/admin/facilities/{id}/prices/` ·
`/admin/services/` · `/admin/bookings/` · `/admin/bookings/{id}/` · `/admin/enquiries/` · `/admin/enquiries/{id}/` ·
`/admin/programmes/` · `/admin/trainings/` · `/admin/blog/` · `/admin/blog/new/` · `/admin/users/` ·
`/admin/media/` · `/admin/settings/` · `/admin/settings/site/` · `/admin/settings/contact/` ·
`/admin/settings/homepage/` · `/admin/audit-logs/` · `/admin/notifications/`

## Programme & Training Lead (`/programmes-dashboard/...`, 403 for others)
`/programmes-dashboard/` (dashboard) · `/programmes-dashboard/programmes/` · `/programmes-dashboard/programmes/new/` ·
`/programmes-dashboard/programmes/{id}/` · `/programmes-dashboard/trainings/` · `/programmes-dashboard/trainers/` ·
`/programmes-dashboard/registrations/` · `/programmes-dashboard/enquiries/`

## Content Staff (`/content-dashboard/...`, if enabled)
`/content-dashboard/blog/` · `/content-dashboard/blog/new/`

## Auth
`/login` · `/logout` · `/password-change` · `/password-reset` (future: email)