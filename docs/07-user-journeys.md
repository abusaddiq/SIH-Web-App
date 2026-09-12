# SPAK Innovation Hub — User Journeys

## J1 Visitor Books a Facility
1. Lands on Home → sees featured facilities.
2. Clicks "Facilities" → filtered list showing name/category/capacity/current price from DB.
3. Clicks "Co-working Space" → detail: description, features, prices (DB), terms, availability.
4. Clicks **Book Now** → booking form (pre-filled facility).
5. Submits → validation → success screen with booking reference (e.g. `SPAK-BK-2026-0001`).
6. Status `Pending`. Admin notified via in-app notification.
7. Admin approves → status `Approved`. (MVP: status visible to visitor only via reference/contact.)

## J2 Visitor Enquires About a Facility
Detail page → **Make an Enquiry** → form → stored in `Enquiry` (source=facility) → `new` status → Admin notified.

## J3 Admin Updates Price
Dashboard → Facilities → pick facility → Price list → edit/add current price → `AuditLog` (old→new) →
public website reflects new price immediately.

## J4 Programme Lead Creates a Programme
`/programmes-dashboard` → **+ Create New Programme** → form (title, dates, venue, trainers, audience,
deadline, image, registration settings) → Save as Draft → Submit for Review (if approval required) →
Admin notified → Admin approves → status `Published` → appears on public `/programmes`.

## J5 Admin Manages Bookings
Dashboard → Bookings → search/filter → open → review → Approve/Reject/More Info/Cancel/Complete +
admin notes → status updated + audit logged.

## J6 Admin Personalises Branding
Settings → Site Settings → upload logo/favicon, change site name/tagline → saved → appears in navbar,
footer, login page, favicon instantly.

## J7 Admin Manages Blog
Dashboard → Blog → create/edit post → draft → publish/schedule → featured image from media library →
public `/blog` + `/blog/{slug}`.

## J8 Visitor Asks the AI Assistant
Home/AI chat → type "What facilities does SPAK have?" → rule-based engine answers from published CMS data;
if data missing → "please contact SPAK or submit an enquiry". No invented prices/confirmations.

## J9 Content Staff Writes an Article (if enabled)
`/content-dashboard/blog` → create post → publish or submit → never sees facilities/prices/settings.