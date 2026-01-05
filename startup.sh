#!/bin/bash
set -e

echo "==> Ir a wwwroot"
cd /home/site/wwwroot

echo "==> Python & pip"
python --version
python -m pip --version

echo "==> Upgrade pip"
python -m pip install --upgrade pip

echo "==> Instalar dependencias"
python -m pip install -r requirements.txt

echo "==> Migraciones"
python manage.py migrate --noinput

echo "==> Collectstatic"
python manage.py collectstatic --noinput

echo "==> Arrancar Gunicorn"
exec gunicorn hojadevida.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --timeout 120
