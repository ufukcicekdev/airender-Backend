#!/bin/sh
set -eu

PORT="${PORT:-8000}"
echo "[railway] PORT=${PORT}"

echo "[railway] migrate..."
python manage.py migrate --noinput

echo "[railway] collectstatic..."
python manage.py collectstatic --noinput --clear 2>/dev/null || python manage.py collectstatic --noinput

echo "[railway] starting daphne on 0.0.0.0:${PORT}..."
exec daphne -b 0.0.0.0 -p "${PORT}" config.asgi:application
