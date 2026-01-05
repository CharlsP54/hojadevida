#!/bin/bash
set -e

echo "==> Entrando a /home/site/wwwroot"
cd /home/site/wwwroot

echo "==> Mostrando archivos"
ls -la

# Si tu manage.py NO está en /home/site/wwwroot, descomenta y ajusta:
# cd hojadevida

echo "==> Instalando dependencias"
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "==> Migraciones"
python manage.py migrate --noinput

echo "==> Collectstatic"
python manage.py collectstatic --noinput

echo "==> Arrancando Gunicorn"
gunicorn hojadevida.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120
