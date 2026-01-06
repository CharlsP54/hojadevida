#!/usr/bin/env bash
set -e

echo "==> Collect static"
python manage.py collectstatic --noinput

echo "==> Start gunicorn"
exec gunicorn hojadevida.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --timeout 120
