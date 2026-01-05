#!/bin/bash
set -e

cd /home/site/wwwroot

# (Opcional) si manage.py NO está aquí, usa:
# cd /home/site/wwwroot/hojadevida

# Arranque directo (rápido)
exec gunicorn hojadevida.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --timeout 120
