#!/bin/bash
set -e

echo "== Instalando dependencias =="
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "== Migraciones =="
python manage.py migrate --noinput

echo "== Static =="
python manage.py collectstatic --noinput

echo "== Arrancando Gunicorn =="
gunicorn hojadevida.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120
