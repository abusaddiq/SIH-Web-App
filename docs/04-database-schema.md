# SPAK Innovation Hub — Database Schema / ERD (MVP)

## App: accounts
- **User** (Django `AbstractUser` extension)
  - `id`, `username`, `email`, `password` (hashed), `first_name`, `last_name`, `phone`, `profile_image`,
    `is_active`, `date_joined`, `last_login`, `role` → FK **Role**, `permissions` M2M (Django), `force_password_change`
- **Role** (`super_admin` | `programme_lead` | `content_staff`)
  - `id`, `code`, `name`, `is_active`
- **Permission** (Django built-in) — M2M to Role via custom table `RolePermission`

## App: core
- **WebsiteSettings** (singleton)
  - `site_name`, `tagline`, `logo`, `logo_alt`, `favicon`, `default_social_image`,
    `seo_title`, `seo_description`, `footer_text`, `copyright`, `analytics_enabled`,
    `programme_approval_required` (bool), `ai_enabled`, `ai_provider`, `content_staff_enabled`
- **ContactSettings** (singleton)
  - `address`, `address_map_link`, `phone_1`, `phone_2`, `email_1`, `email_2`, `whatsapp`,
    `working_hours`, `facebook`, `twitter`, `instagram`, `linkedin`, `youtube`,
    `contact_page_text`, `emergency_contact`, `map_embed_html`
- **HomepageSection**
  - `id`, `key` (unique), `title`, `subtitle`/`content` (RichText), `image`, `cta_text`, `cta_link`,
    `is_active`, `sort_order`
- **MediaItem**
  - `id`, `file`, `alt_text`, `caption`, `uploaded_by` FK, `created_at`, `size`, `mime`
- **AuditLog**
  - `id`, `user` FK, `action`, `entity_type`, `entity_id`, `previous_value` (JSON), `new_value` (JSON),
    `ip_address`, `created_at`
- **Notification**
  - `id`, `recipient` FK, `title`, `body`, `entity_type`, `read`, `created_at`

## App: facilities
- **FacilityCategory**: `id`, `name`, `slug`, `description`, `is_active`, `sort_order`
- **Facility**
  - `id`, `name`, `slug`, `category` FK, `description`, `overview`, `features` (JSON array),
    `capacity`, `availability_text`, `status` (draft/published/archived), `terms` (text),
    `primary_image`, `gallery` (M2M MediaItem), `is_featured`, `sort_order`, `created_by`, `updated_at`
  - slug templates: `co-working-space`, `virtual-office`, `meeting-rooms`, `conference-hall`, `event-hall`, `training-rooms`
- **FacilityPrice**
  - `id`, `facility` FK, `price_type` (daily/weekly/monthly/membership/special), `amount` (Decimal),
    `currency` (default `KES`), `billing_period`, `effective_date`, `is_current` (bool), `status`
  - rule: only one `is_current` per `(facility, price_type)`
- **Service**: `id`, `name`, `slug`, `icon`, `short_description`, `full_description`, `image`,
  `price_text`, `category`, `is_published`, `is_featured`, `sort_order`
- **Booking**
  - `id`, `ref_no` (unique, e.g. `SPAK-BK-2026-0001`), `full_name`, `organization`, `email`, `phone`,
    `facility` FK, `preferred_date`, `start_time`, `end_time`, `participants`, `purpose`,
    `requirements`, `message`, `status` (pending/under_review/approved/rejected/cancelled/completed),
    `admin_notes`, `submitted_at`, `reviewed_by`, `reviewed_at`
- **Enquiry**
  - `id`, `ref_no`, `name`, `email`, `phone`, `subject`, `message`, `source` (contact/facility/programme/booking),
    `status` (new/read/replied/archived), `admin_reply`, `replied_by`, `created_at`, `replied_at`

## App: programmes
- **ProgrammeCategory**: `id`, `name`, `slug` (training/workshop/seminar/webinar/bootcamp/clinic/mentorship/…), `is_active`
- **Person** (Trainer/Facilitator/Speaker): `id`, `name`, `title`, `bio`, `image`, `email`, `kind`
- **Programme**
  - `id`, `title`, `slug`, `category` FK, `programme_type` (online/physical/hybrid), `short_description`,
    `full_description`, `start_date`, `end_date`, `start_time`, `end_time`, `venue`, `trainers` M2M Person,
    `facilitators` M2M Person, `speakers` M2M Person, `target_audience`, `max_participants`,
    `registration_deadline`, `requires_registration` (bool), `uses_external_registration` (bool),
    `registration_link`, `registration_button_label`, `contact_info`, `image`, `requirements`,
    `status` (draft/submitted/published/cancelled/archived), `created_by` FK, `published_at`, `campaign` (text)
- **ProgrammeRegistration**: `id`, `ref_no`, `programme` FK, `full_name`, `email`, `phone`, `organization`,
  `message`, `status`, `created_at`
- **ProgrammeEnquiry**: `id`, `ref_no`, `programme` FK, `name`, `email`, `phone`, `message`, `status`, `created_at`

## App: blog
- **Category**: `id`, `name`, `slug`
- **Tag**: `id`, `name`, `slug`
- **Post**
  - `id`, `title`, `slug`, `excerpt`, `content` (RichText), `featured_image`, `category` FK, `tags` M2M,
    `author` FK User, `status` (draft/published/scheduled/unpublished/archived), `published_at`,
    `scheduled_for`, `seo_title`, `seo_description`, `views`, `created_at`, `updated_at`

## Relationships summary
`Role <- User` ; `FacilityCategory -> Facility -> FacilityPrice` ; `Facility -> Booking` ;
`ProgrammeCategory -> Programme <- Person` ; `Programme -> ProgrammeRegistration/Enquiry` ;
`Category/Tag <- Post` ; `User -> MediaItem/AuditLog/Notification`