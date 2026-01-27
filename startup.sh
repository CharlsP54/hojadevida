#!/bin/bash

# 1. Instalar dependencias del sistema para WeasyPrint (PDF)
# Esto es vital porque Azure Linux viene "pelado"
echo "==> Instalando librerías gráficas..."
apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

# 2. Migraciones de Django
echo "==> Ejecutando migraciones..."
python manage.py migrate

# 3. Archivos Estáticos
echo "==> Recolectando estáticos..."
python manage.py collectstatic --noinput

# 4. Iniciar Gunicorn
echo "==> Iniciando servidor..."
# Aumentamos el timeout a 600 porque la instalación inicial toma tiempo
exec gunicorn hojadevida.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 600