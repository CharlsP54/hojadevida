#!/bin/bash
set -e

python -m pip install --upgrade pip

# Migra (opcional hacerlo automático; yo lo dejo porque te evita sustos)
python manage.py migrate --noinput

# Static (WhiteNoise necesita esto)
python manage.py collectstatic --noinput

# Arranque
gunicorn hojadevida.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
