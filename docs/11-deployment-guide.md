# SPAK Innovation Hub — Deployment Guide

The project runs on Gunicorn (WSGI) and can be served behind Nginx. PostgreSQL is the only external
service required. The default `.env` is development-oriented: set `DJANGO_DEBUG=false` and real secrets
before going live.

## 1. Production environment variables

Edit `.env` (see `docs/12-environment-variables.md`):

```bash
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<long random string>
DJANGO_ALLOWED_HOSTS=spak.example.com,www.spak.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://spak.example.com
DJANGO_SECURE_SSL=true
DJANGO_HSTS_SECONDS=31536000
NOTIFICATION_EMAIL_ENABLED=true
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=no-reply@spak.example.com
EMAIL_HOST_PASSWORD=<secret>
EMAIL_USE_TLS=true
```

## 2. Static & media files

```bash
.venv/bin/python manage.py collectstatic --noinput
```

- `STATIC_ROOT` → serves the app's CSS/JS/vendored Bootstrap.
- `MEDIA_ROOT` (`media/`) → uploaded images. Keep it on a persistent, backed-up volume.

## 3. Run with Gunicorn

```bash
.venv/bin/gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
```

For ASGI (WebSockets / long-lived connections) use Uvicorn:

```bash
.venv/bin/python -m uvicorn config.asgi:application --host 127.0.0.1 --port 8000
```

## 4. Nginx reverse proxy

```nginx
server {
    listen 80;
    server_name spak.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name spak.example.com;

    ssl_certificate     /etc/ssl/spak.example.com.crt;
    ssl_certificate_key /etc/ssl/spak.example.com.key;

    client_max_body_size 12m;              # MUST exceed MAX_UPLOAD_SIZE_MB (default 8)

    location /static/ {
        alias /home/engr/Desktop/SIH\ Web\ App/staticfiles/;
    }
    location /media/ {
        alias /home/engr/Desktop/SIH\ Web\ App/media/;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 5. Process manager (systemd)

```ini
# /etc/systemd/system/spak.service
[Unit]
Description=SPAK Innovation Hub (Gunicorn)
After=network.target

[Service]
User=engr
WorkingDirectory=/home/engr/Desktop/SIH Web App
ExecStart=/home/engr/Desktop/SIH Web App/.venv/bin/gunicorn config.wsgi:application -b 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now spak
```

## 6. Post-deploy tasks

```bash
sudo systemctl restart spak
.venv/bin/python manage.py check --deploy
.venv/bin/python manage.py seed_demo   # only if no real data exists yet
```

## 7. Backups

Back up the PostgreSQL `spak_hub` database and the `media/` folder together:

```bash
/usr/lib/postgresql/15/bin/pg_dump -p 5433 -h 127.0.0.1 spak_hub > spak_hub_$(date +%F).sql
rsync -a "/home/engr/Desktop/SIH Web App/media/" ./backups/media/
```

## 8. Rolling back

Code is deployed from a git tag/branch; rollback = deploy the previous tag and restart. Database
migrations should be reverted deliberately (restore the backup) rather than auto-reversed.