#!/bin/bash
set -e

cd /home/site/wwwroot

# Arranque directo y rápido
exec gunicorn hojadevida.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --timeout 120
