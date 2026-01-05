#!/bin/bash
set -e

cd /home/site/wwwroot

echo "==> Python:"
python --version
echo "==> Pip:"
python -m pip --version

echo "==> Upgrade pip"
python -m pip install --upgrade pip

echo "==> Install requirements"
python -m pip install -r requirements.txt

echo "==> Check Django"
python -c "import django; print('Django OK:', django.get_version())"

echo "==> Migrate"
python manage.py migrate --noinput

echo "==> Collectstatic"
python manage.py collectstatic --noinput

echo "==> Start gunicorn"
exec gunicorn hojadevida.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --timeout 120
