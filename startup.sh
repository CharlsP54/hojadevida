#!/bin/bash

echo "--- 1. INSTALANDO LIBRERÍAS DE PYTHON (Django, Weasyprint...) ---"
# Esto soluciona el error "No module named django"
pip install -r requirements.txt

echo "--- 2. INSTALANDO LIBRERÍAS DE LINUX (Para PDF) ---"
# Esto soluciona el error de WeasyPrint/Gobject
apt-get update -qq
apt-get install -y -qq libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info libcairo2

echo "--- 3. MIGRANDO BASE DE DATOS ---"
python manage.py migrate

echo "--- 4. RECOLECTANDO ARCHIVOS ESTÁTICOS ---"
python manage.py collectstatic --noinput

echo "--- 5. ARRANCANDO SERVIDOR ---"
# Importante: Puerto 8000
gunicorn --bind=0.0.0.0:8000 --timeout 600 hojadevida.wsgi