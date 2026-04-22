#!/bin/sh
set -e

mkdir -p /app/persist /app/staticfiles

export DJANGO_DEBUG="${DJANGO_DEBUG:-true}"
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-127.0.0.1,localhost}"

if [ ! -n "${SQLITE_PATH:-}" ]; then
    export SQLITE_PATH="/app/persist/db.sqlite3"
fi

if [ ! -n "${MEDIA_ROOT:-}" ]; then
    export MEDIA_ROOT="/app/persist/media"
fi

python - <<'PY'
import os
from pathlib import Path

db_path = Path(os.environ.get("SQLITE_PATH", "/app/persist/db.sqlite3"))
db_path.parent.mkdir(parents=True, exist_ok=True)
media_root = Path(os.environ.get("MEDIA_ROOT", "/app/persist/media"))
media_root.mkdir(parents=True, exist_ok=True)
print(f"Using SQLite database: {db_path}")
print(f"Using media root: {media_root}")
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn market_board.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2
