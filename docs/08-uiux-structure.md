# SPAK Innovation Hub — UI/UX Design Structure

## Visual Language
- **Theme**: clean, modern innovation-hub. Primary deep navy/purple-blue, accent vibrant cyan; white/grey surfaces.
- **Typography**: strong sans-serif headings (e.g. system/inter stack), readable body.
- **Spacing**: consistent scale; generous whitespace; minimal clutter.
- **Animations**: subtle only (hover states, card lifts, page transitions); no heavy motion.
- **Accessibility**: colour-contrast safe, focus states, semantic HTML, aria labels, keyboard-friendly nav.
- **Mobile-first**: hamburger nav on small screens; sticky CTA where relevant.

## Layout System (shared)
- **Base**: navbar (logo + nav + Book a Facility CTA), content block, footer (editable).
- **Components**: hero, section cards, feature chips, price cards, timeline, testimonial cards,
  CTA band, stats strip, breadcrumb, pagination, forms, modals, toast/alerts, empty states, badges.

## Public Pages
1. **Home** — Hero (editable), intro, About preview, Services, Featured facilities w/ price chips,
   Upcoming programmes, Why choose SPAK, Statistics, Featured blog, Testimonials, CTA, Contact strip. Every section DB-driven via `HomepageSection`.
2. **About** — story, mission, vision, values (CMS).
3. **Services** — card grid.
4. **Facilities** — filterable grid; each card: image, category, capacity, current price, Book button.
5. **Facility detail** — gallery, description, features list, pricing tabs (daily/weekly/monthly/membership),
   availability, terms, Book Now + Make an Enquiry.
6. **Programmes** — category filter chips, upcoming/ongoing/past groups, Register/Enquire buttons.
7. **Programme detail** — image, meta grid (dates/times/venue/type/audience), trainers/speakers,
   requirements, registration deadline, Register/Enquire.
8. **Blog** — featured/latest grid, category sidebar, search.
9. **Blog post** — article, share links, related posts.
10. **Contact** — info cards, map embed, form.
11. **Search** — results grouped by type.
12. **AI Chat** — persistent chat window with clear disclaimer.

## Admin Dashboard (`/admin`)
- Sidebar nav grouped: Overview · Facilities · Services · Bookings · Enquiries · Programmes · Blog · Media ·
  Users · Settings · Audit Logs.
- Top bar: search, notifications bell, user menu.
- Content: KPI stat cards, charts (recent bookings/programmes), tables with search/filter, action buttons.
- Consistent CRUD layout: list page, form page, detail page.

## Programme Lead Dashboard (`/programmes-dashboard`)
- KPI cards (my programmes, drafts, upcoming, registrations), + Create New Programme;
- list tables with status badges; edit forms reusing programme fields; approval workflow banner.

## Forms
- Consistent labelled inputs, required markers, inline validation, character counters, date/time pickers,
  file upload preview, success/error messaging. Server-side validation mirrors client-side.