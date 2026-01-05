#!/bin/bash
set -e

cd /home/site/wwwroot

echo "==> Python:"
python3 --version

echo "==> Upgrade pip"
python3 -m pip install --upgrade pip

echo "==> Install requirements"
python3 -m pip install -r requirements.txt

echo "==> Check Django"
python3 -c "import django; print('Django OK:', django.get_version())"

echo "==> Migrate"
python3 manage.py migrate --noinput

echo "==> Collectstatic"
python3 manage.py collectstatic --noinput

echo "==> Start gunicorn"
exec gunicorn hojadevida.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --timeout 120
