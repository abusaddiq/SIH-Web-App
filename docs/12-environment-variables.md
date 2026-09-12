# SPAK Innovation Hub — Environment Variables Reference

All settings are read from `.env` (dotenv). Copy `.env.example` → `.env` and adjust.

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | `insecure-dev-key-change-me` | Django secret. **Set a long random value in production.** |
| `DJANGO_DEBUG` | `true` | Debug mode. Must be `false` in production. |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated allowed hosts. Use `*` only in dev. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | *(empty)* | Comma-separated origins, e.g. `https://spak.example.com`. |
| `DJANGO_TIME_ZONE` | `Africa/Lagos` | Application time zone. |
| `DB_NAME` | `spak_hub` | PostgreSQL database name. |
| `DB_USER` | `engr` | PostgreSQL user. |
| `DB_PASSWORD` | *(empty)* | PostgreSQL password (leave empty when using `trust` auth). |
| `DB_HOST` | `127.0.0.1` | PostgreSQL host. |
| `DB_PORT` | `5433` | PostgreSQL port. The demo cluster runs on 5433. |
| `AI_PROVIDER` | `rules` | AI assistant provider. `rules` = offline, CMS-data answers, no API. Future: `openai` / `anthropic` / `gemini`. |
| `AI_API_KEY` | *(empty)* | Key for cloud AI providers when enabled. |
| `AI_MODEL` | *(empty)* | Model name for cloud AI providers when enabled. |
| `NOTIFICATION_EMAIL_ENABLED` | `false` | Send real emails for bookings/enquiries/approvals. |
| `DEFAULT_FROM_EMAIL` | `no-reply@spak.local` | From-address for outgoing email. |
| `EMAIL_BACKEND` | `console.EmailBackend` | `console` prints to logs (dev); use `smtp.EmailBackend` in production. |
| `EMAIL_HOST` | *(empty)* | SMTP host. |
| `EMAIL_PORT` | `587` | SMTP port. |
| `EMAIL_HOST_USER` | *(empty)* | SMTP username. |
| `EMAIL_HOST_PASSWORD` | *(empty)* | SMTP password. |
| `EMAIL_USE_TLS` | `false` | Enable STARTTLS. |
| `MAX_UPLOAD_SIZE_MB` | `8` | Max upload size for images; keep Nginx `client_max_body_size` higher. |
| `SPAK_ADMIN_PASSWORD` | `admin12345` | Initial password for the seeded `admin` user (used only by `seed_demo`). |
| `SPAK_LEAD_PASSWORD` | `lead12345!` | Initial password for the seeded `lead` user. |
| `SPAK_WRITER_PASSWORD` | `writer12345!` | Initial password for the seeded `writer` user. |

## Security notes

- Never commit `.env`. It is git-ignored.
- Rotate `DJANGO_SECRET_KEY` and all passwords before going live.
- When `DJANGO_DEBUG=false`, `SECURE_SSL_REDIRECT`, `SECURE_HSTS_*`, secure cookies and
  `X-Content-Type-Options: nosniff` become active automatically.