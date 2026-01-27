#!/usr/bin/env bash
set -o errexit

# Dependencias del sistema (WeasyPrint)
apt-get update
apt-get install -y \
  libcairo2 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  shared-mime-info

# Python deps
pip install -r requirements.txt

# Static + DB
python manage.py collectstatic --noinput
python manage.py migrate --noinput
