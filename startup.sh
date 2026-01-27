#!/bin/bash

echo "--- INICIANDO INSTALACIÓN DE DEPENDENCIAS ---"

# 1. Instalar librerías gráficas (WeasyPrint lo necesita OBLIGATORIAMENTE)
# Usamos -qq para que no llene el log de texto basura
apt-get update -qq
apt-get install -y -qq libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info libcairo2

echo "--- DEPENDENCIAS INSTALADAS ---"

# 2. Migraciones
echo "==> Migrando base de datos..."
python manage.py migrate

# 3. Estáticos
echo "==> Recolectando estáticos..."
python manage.py collectstatic --noinput

# 4. Iniciar Gunicorn
echo "==> Arrancando servidor..."
gunicorn --bind=0.0.0.0 --timeout 600 hojadevida.wsgi