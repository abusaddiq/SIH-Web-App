# SPAK Innovation Hub — User Roles & Permission Matrix

| Feature | Super Admin | Programme & Training Lead | Content Staff | Public |
|---|---|---|---|---|
| Website settings / branding / logo | **YES** | NO | NO | — |
| Homepage content | **YES** | NO | Limited/NO | — |
| Facilities (CRUD) | **YES** | NO (may reference) | NO | view |
| Facility prices | **YES** | NO | NO | view |
| Facility availability | **YES** | NO | NO | view |
| Services | **YES** | NO | Limited (view) | view |
| Bookings (all) | **YES** | NO (view own programme scope) | NO | submit request |
| Enquiries (all) | **YES** | programme enquiries only | NO | submit |
| Programmes CRUD | **YES** | **YES** (own) | View | view |
| Training activities | **YES** | **YES** | View | view |
| Programme approval | Approve/Reject | Submit/Edit | NO | — |
| Blog | **YES** | Optional view | **YES** | read |
| Contact information | **YES** | NO | NO | view |
| Users & roles | **YES** | NO | NO | — |
| System settings | **YES** | NO | NO | — |
| Audit logs | **YES** | NO (own actions visible if scoped) | NO | — |
| Media library | **YES** | upload programme images | upload blog images | — |
| Search (public) | — | — | — | **YES** |
| AI assistant | configure | — | — | **YES** |

## Enforcement
- **Server side only.** Every protected view uses `PermissionRequiredMixin`-style checks / decorators.
- `super_admin` may access `/admin/*` and `/programmes-dashboard/*`.
- `programme_lead` may access `/programmes-dashboard/*`; any navigation to `/admin/*` returns **403**.
- `content_staff` (enabled via setting) may access `/blog-admin/*` only.
- Anonymous users may access `/` and public routes only; dashboards return 403/redirect-to-login.

## Critical Rules
1. Only Super Admin can reach: facilities, prices, availability, users, system settings, services, all bookings.
2. Programme Lead can never modify prices/settings/users/facilities — enforced by URL-level guards AND in-view
   permission checks (defense in depth).
3. Content Staff can never touch facilities, prices, users, or settings.