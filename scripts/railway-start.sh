#!/bin/sh
# Dispatched by APP_PROCESS (set per Railway service).
#   web    — migrate, collectstatic, Daphne (default)
#   celery — Celery worker
#   beat   — Celery beat (optional)
set -eu

PROCESS="${APP_PROCESS:-web}"
echo "[railway-start] APP_PROCESS=${PROCESS}"

case "$PROCESS" in
  web)
    exec sh scripts/railway-web.sh
    ;;
  celery)
    exec sh scripts/railway-celery.sh
    ;;
  beat)
    echo "[railway-beat] starting celery beat..."
    exec celery -A config beat -l info
    ;;
  *)
    echo "[railway-start] unknown APP_PROCESS='${PROCESS}' (use web, celery, or beat)" >&2
    exit 1
    ;;
esac
