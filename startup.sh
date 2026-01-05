#!/bin/bash
set -e

echo "==> Iniciando en: $(pwd)"
echo "==> Listando archivos en /home/site/wwwroot"
cd /home/site/wwwroot
ls -la

# (Opcional) si necesitas ver si existe manage.py:
test -f manage.py && echo "✅ manage.py encontrado" || (echo "❌ No encuentro manage.py" && exit 1)

echo "==> Arrancando Gunicorn (rápido)"
exec gunicorn hojadevida.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --timeout 120
