#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PORT="${SPAK_PORT:-8000}"
HOST="${SPAK_HOST:-}"
SEED="${SPAK_SEED:-auto}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR=".venv"

echo "==> SPAK deploy (port ${PORT}, seed=${SEED})"

# ---- PostgreSQL (podman/docker container on port 5432) ----
SOCK="$HOME/.local/share"
start_db() {
  if docker info >/dev/null 2>&1 || podman info >/dev/null 2>&1; then
    if docker exec spak_postgres pg_isready -U engr -h 127.0.0.1 -p 5432 >/dev/null 2>&1; then
      echo "    DB already running on 5432 (spak_postgres)"
      return
    fi
    echo "    Starting PostgreSQL container (spak_postgres)..."
    docker start spak_postgres >/dev/null 2>&1 || podman start spak_postgres >/dev/null 2>&1
    for i in $(seq 1 30); do
      docker exec spak_postgres pg_isready -U engr -h 127.0.0.1 -p 5432 >/dev/null 2>&1 && return
      sleep 1
    done
    echo "    DB did not come up in time."; exit 1
  fi
  echo "    No container runtime found. Create/start the spak_postgres container and retry."; exit 1
}
start_db

# ---- .env provisioning ----
if [ ! -f .env ]; then
  echo "==> Creating .env from .env.production.example"
  if [ ! -f .env.production.example ]; then
    echo "    .env.production.example missing — create .env manually (see docs/12)"; exit 1
  fi
  "$PYTHON_BIN" - "$HOST" <<'PYEOF'
import os, re, secrets, sys
host = sys.argv[1]
content = open(".env.production.example").read()
key = secrets.token_urlsafe(50)
content = re.sub(r"^DJANGO_SECRET_KEY=.*$", f"DJANGO_SECRET_KEY={key}", content, flags=re.M)
content = re.sub(r"^DJANGO_ALLOWED_HOSTS=.*$", f"DJANGO_ALLOWED_HOSTS={host or '127.0.0.1'}", content, flags=re.M)
if host:
    content = re.sub(r"^DJANGO_CSRF_TRUSTED_ORIGINS=.*$", f"DJANGO_CSRF_TRUSTED_ORIGINS=https://{host}", content, flags=re.M)
open(".env", "w").write(content)
print("    wrote .env with fresh secret key")
PYEOF
fi

# ---- Python venv + deps ----
if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating virtualenv ($VENV_DIR)"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi
echo "==> Installing/verifying requirements"
"$VENV_DIR/bin/pip" install --quiet --disable-pip-version-check -r requirements.txt

DJ="env DJANGO_DEBUG=false DJANGO_SECURE_SSL=${DJANGO_SECURE_SSL:-false}"

# ---- DB schema ----
echo "==> Applying migrations"
$DJ "$VENV_DIR/bin/python" manage.py migrate --noinput

# ---- Seed (only when the DB is empty) ----
if [ "$SEED" = "auto" ]; then
  HAS_USERS=$($DJ "$VENV_DIR/bin/python" manage.py shell -c \
    "from accounts.models import User; print(User.objects.exists())")
  if [ "$HAS_USERS" = "False" ]; then SEED=1; else SEED=0; fi
fi
if [ "$SEED" = "1" ]; then
  echo "==> Seeding demo data"
  $DJ "$VENV_DIR/bin/python" manage.py seed_demo
elif [ "$SEED" = "auto" ] || [ "$SEED" = "0" ]; then
  echo "    Seed skipped (users already exist / SPAK_SEED=0)"
else
  echo "    Unknown SPAK_SEED='$SEED'"; exit 1
fi

# ---- Static files ----
echo "==> Collecting static files"
$DJ "$VENV_DIR/bin/python" manage.py collectstatic --noinput --clear -v 0

# ---- Gunicorn ----
PIDFILE="run/spak-gunicorn.pid"
mkdir -p run
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "==> Gunicorn already running (pid $(cat "$PIDFILE")) — restarting"
  "$VENV_DIR/bin/gunicorn" config.wsgi:application --bind "127.0.0.1:${PORT}" \
    --workers 3 --timeout 60 --pid "$PIDFILE" --reload 2>/dev/null || true
  sleep 2
elif command -v ss >/dev/null 2>&1 && ss -ltn | grep -q ":${PORT} "; then
  echo "    Port ${PORT} is occupied by another process — set SPAK_PORT=PORT"; exit 1
else
  echo "==> Starting Gunicorn on 127.0.0.1:${PORT}"
  setsid nohup "$VENV_DIR/bin/gunicorn" config.wsgi:application \
    --bind "127.0.0.1:${PORT}" --workers 3 --timeout 60 \
    --pid "$PIDFILE" --access-logfile - --error-logfile - \
    </dev/null >> "logs/spak-gunicorn.log" 2>&1 &
  sleep 2
fi

# ---- Health check ----
echo "==> Health check"
ok=0
for i in $(seq 1 15); do
  if curl -fsS -m 5 -o /dev/null "http://127.0.0.1:${PORT}/" 2>/dev/null; then ok=1; break; fi
  sleep 1
done
if [ "$ok" = "1" ]; then
  echo ""
  echo "DEPLOY OK  ->  http://127.0.0.1:${PORT}/"
  echo "             Super Admin:  /admin/  (create via seed_demo)"
  echo "             Nginx/systemd in front? see docs/11-deployment-guide.md"
else
  echo "DEPLOY FAILED — last gunicorn log lines:"
  tail -20 "logs/spak-gunicorn.log" || true
  exit 1
fi