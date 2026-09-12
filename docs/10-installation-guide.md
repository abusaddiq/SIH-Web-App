# SPAK Innovation Hub — Installation Guide

Requirements: Python 3.11+, PostgreSQL 15+, and network access to install PyPI packages and Bootstrap assets (already vendored in `static/vendor/`).

## 1. Prerequisites

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip postgresql postgresql-contrib
```

The PostgreSQL version on modern Debian/Ubuntu is usually 15+.

## 2. PostgreSQL (user-owned demo cluster — no root needed)

If you cannot manage the system PostgreSQL service, create a **user-owned cluster**:

```bash
export PGBIN=/usr/lib/postgresql/15/bin
DATA=$HOME/.local/share/spak_pgdata
$PGBIN/initdb -D "$DATA" -U $USER --auth=trust

# Start it on port 5433 with a writable socket directory
$PGBIN/pg_ctl -D "$DATA" -o "-p 5433 -c listen_addresses=127.0.0.1 -k $HOME/.local/share" \
  -l $HOME/.local/share/spak_pg.log start

$PGBIN/createdb -p 5433 -h 127.0.0.1 spak_hub
```

> Every time the machine restarts, re-run the `pg_ctl ... start` line above.

## 3. Clone & install the app

```bash
cd "/home/engr/Desktop/SIH Web App"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 4. Configure environment

```bash
cp .env.example .env
# Edit .env to match your DB host/port/user and to set a real DJANGO_SECRET_KEY.
```

## 5. Migrations, checks, seed

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py check
.venv/bin/python manage.py seed_demo     # demo users + [DEMO] placeholder content
```

The seed creates:

| Role            | Username | Password         |
|-----------------|----------|------------------|
| Super Admin     | `admin`  | `admin12345`     |
| Programme Lead  | `lead`   | `lead12345!`     |
| Content Staff   | `writer` | `writer12345!`   |

> Change these passwords immediately and override them via `SPAK_ADMIN_PASSWORD`, `SPAK_LEAD_PASSWORD`, `SPAK_WRITER_PASSWORD` when seeding.

## 6. Run for development

```bash
.venv/bin/python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

## 7. Useful entry points

| Page | URL |
|---|---|
| Public home | `/` |
| Admin shell (Super Admin) | `/admin/` |
| Django admin | `/django-admin/` |
| Programme Lead dashboard | `/programmes-dashboard/` |
| Content staff dashboard | `/content-dashboard/` |
| AI assistant | `/ai-chat/` |
| Sitemap / robots | `/sitemap.xml`, `/robots.txt` |

## 8. Verifying the install

```bash
.venv/bin/python manage.py check          # no issues
# Then browse the public site and log in as each demo role.
```