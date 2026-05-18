#!/bin/sh
set -eu

echo "[railway-celery] starting worker (queues: default, rendering)..."
exec celery -A config worker -l info -Q default,rendering --concurrency=2
