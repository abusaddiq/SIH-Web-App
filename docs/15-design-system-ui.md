# Design System & UI/UX (Redesign)

Date: 2026-09-12 · Applies to commit `6628f3a` (design-system overhaul)

## Purpose

A complete visual overhaul of the **public-facing front end** of SPAK Innovation Hub:
from a generic Bootstrap dashboard look into a premium, editorial, mobile-first
coworking/innovation-hub experience inspired by the UX philosophy of sites such as
betahaus.com — while keeping **SPAK's own blue-and-white identity**, a fully
CMS-driven UI, and the existing Django backend untouched.

Admin/lead/content dashboards keep their dense, functional styling. This document
describes the design system and the (small) additive backend changes.

## Design principles

1. **No invented SPAK content** — every fact (prices, capacities, dates, contact
   details, counts, people) comes from the database/CMS. Demo seed content is the
   only exception and is labelled `[DEMO]`.
2. **Original identity** — inspired by editorial coworking sites in structure and
   typography, not cloned (no betahaus text, images, logos, or branding).
3. **Mobile-first** — all layout built for 320 px phones up through 1920 px desktops;
   no horizontal overflow, no clipped content, large tap targets.
4. **Accessibility** — skip link, visible focus, ARIA labels on interactive elements,
   semantic landmarks, `prefers-reduced-motion` respected, no color-only meaning.
5. **SEO-friendly** — per-page titles/descriptions, canonical URLs, Open Graph +
   JSON-LD Organization markup, semantic headings.
6. **Self-hosted resources** — Inter variable font and Bootstrap 5 are vendored in
   `static/vendor/` (no CDN/CSP dependency).

## Design tokens (CSS custom properties)

Defined in `static/css/spak.css` `:root`:

| Token | Value | Use |
|---|---|---|
| `--ink` / `--navy-900` | `#0b1f3f` | Primary text & deep navy |
| `--blue-100…900` | ramp of `#1f6ef2` | Brand blue scale |
| `--blue-600` | `#1f6ef2` | Primary brand accent |
| `--accent` | `#3eb8ff` | Bright UI accent |
| `--surface` | `#ffffff` | Cards/panels |
| `--surface-2` | `#f5f7fb` | Tinted sections |
| `--line` | `#e3e9f2` | Borders/dividers |
| `--muted` | `#63708a` | Secondary text |
| `--radius` / `--radius-sm/pill` | 16 / 10 / 999px | Radii |
| `--font-sans` | Inter variable + fallbacks | Type |
| `--shadow` / `--shadow-lg` | soft navy shadows | Elevation |
| `--t-fast/med` | 0.15s / 0.3s | Motion |
| Breakpoints | 480 / 600 / 800 / 992 / 1200 | Responsive |

## Typography

- **Inter Variable** (`static/vendor/fonts/inter-var.woff2`, weights 100–900) with
  `font-display: swap`. Preloaded in `<head>`.
- Scales: extra display titles `clamp(2.2rem…4.5rem)`, section titles
  `clamp(1.5rem…2.2rem)`, base 1rem/1.75 line-height, fine print 0.875rem.
- Editorial details: tight letter-spacing headlines, a brand-blue accent marker
  (`<span class="hl">.</span>`), kickers (uppercase micro-labels), hairline rules.

## Layout language

- **Editorial hero** — dark navy field with grid/gradient texture, large headline +
  highlighted period, CMS-driven sub-line, primary/secondary CTAs, and a site-search
  strip. A floating stat card shows the count of published spaces (derived, animated
  on large screens only).
- **`.spak-container`** — centered, 16 px gutters (24 px from 600 px), max ~1200 px.
- **Section rhythm** — alternating white / `--surface-2` tints, generous vertical
  padding; kicker + title + lead per section.
- **Split panels** — text-left/visual-right blocks (`layout--sided`, `split`).
- **Index lists** — numbered editorial rows for services (big 02d numerals, hover
  arrow) and event lists for programmes (date block + meta + arrow).
- **Media cards** — image-first cards with tag + price pills, arrow glyph, used for
  facilities, programmes, blog (a lead/story grid with first-story emphasis).
- **Stats band** — dark `section--ink` band with pure derived counts
  (`facilities`, upcoming programmes, trainers/facilitators, published stories).
- **CTA band** — navy/blue panel with headline + actions.
- **Filters** — pill chips (`category`, search) reused on Facilities, Programmes,
  Blog, Search.
- **AI widget** — floating launcher (bottom-right) opening a chat panel that POSTs
  to the JSON endpoint with the CSRF header; suggestion chips; thinking state;
  reduced-motion friendly. Also provided as a full page at `/ai-chat/`.
- **Footer** — 4-column editorial footer (brand/socials, explore links, programme
  links, contact details) drawn from `ContactSettings`.

## Pages converted

Home, About, Services, CMS pages, Facilities (list/detail/book/enquiry/success/
meeting-rooms), Programmes (list/detail/training/cards), Blog (list/detail),
Contact, Search, AI Assistant, Staff Login, 403/404/500.

## Compatibility with admin dashboards

Admin shells (`admin_shell/_base.html`, `programmes_dash/_base.html`) also load
`spak.css`. The redesign keeps the shared classes they rely on:
`--spak-primary`, `--spak-accent`, `.btn-spak`, `.text-accent`,
`.placeholder-banner`. Admin-specific styling stays in `static/css/admin.css`
(now with responsive table/form/`overflow-x` rules). Dashboards remain dense and
functional — the editorial language applies to the public site only.

## Backend changes (additive & documented)

1. `public/views.py` — `home()` now also supplies derived counts:
   `programmes_count`, `posts_count`, `people_count` (used only by the honest stats
   band).
2. `public/views.py` — new `ai_chat_ask()` (POST only, rate-limited `30/m`/IP)
   returns JSON `{"answer": ...}` for the floating widget.
3. `public/urls.py` — `path("ai/ask/", ..., name="public-ai-ask")`.
4. No migrations, no model changes, no RBAC changes.

## Search engine & social

- Canonical URL block (overridable per page through `{% block canonical %}`).
- `og:type/site_name/title/description/url/image` blocks (+ `og_image_meta` per-article).
- JSON-LD `Organization` with name/url/description/address/email/telephone from settings.

## Accessibility & motion

- Skip link before the header.
- All interactive elements focus-visible styled; `:focus-visible` ring on brand blue.
- Mobile nav closes on Escape, link tap, or overlay; `aria-expanded`/`aria-label` on
  the burger.
- Reveal-on-scroll uses `IntersectionObserver` and is disabled under
  `prefers-reduced-motion`.

## Verification

- All public pages render 200 on dev (`127.0.0.1:8000`) and deployed Gunicorn
  (`127.0.0.1:8077`) instances, including one expected 404.
- `manage.py test --settings config.settings_test` → 9/9 OK.
- `manage.py check --deploy` (with `DJANGO_SECURE_SSL=true`) → 0 issues; strong
  random `DJANGO_SECRET_KEY` in `.env`.
- AI JSON endpoint verified end-to-end (CSRF cookie + header) returning a real
  answer from the rules provider.
- Blog detail page required a template fix: a `{% block %}` nested inside `{% if %}`
  rendered unconditionally and dereferenced a missing image file — blocks are now
  outside conditionals everywhere.

## Files

| Path | Change |
|---|---|
| `static/css/spak.css` | Complete redesign (design tokens + editorial components + responsive) |
| `static/css/admin.css` | Added responsive rules for dashboards |
| `static/js/spak.js` | Nav toggle, reveal-on-scroll, AI widget fetch, alert auto-dismiss |
| `templates/base.html` | SEO head, sticky header, mobile nav, editorial footer, AI widget |
| `templates/public/*` | All public pages redesigned |
| `templates/auth/login.html`, `templates/403/404/500.html` | Redesigned |
| `public/views.py`, `public/urls.py` | Derived stats + JSON AI endpoint (additive) |
| `static/vendor/fonts/inter-var.woff2` | Self-hosted Inter variable font |