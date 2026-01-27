#!/bin/bash

# --- 1. INSTALAR LIBRERÍAS DE SISTEMA (Vital para WeasyPrint) ---
# Azure usa una imagen basada en Debian, así que usamos apt-get
echo "==> Instalando dependencias gráficas para PDF..."
apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libcairo2

# --- 2. CONFIGURACIÓN DE DJANGO ---
echo "==> Aplicando migraciones de base de datos..."
python manage.py migrate

echo "==> Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# --- 3. INICIAR SERVIDOR ---
echo "==> Iniciando Gunicorn..."
# Aumentamos el timeout a 600s para dar tiempo a la instalación y generación de PDFs grandes
exec gunicorn hojadevida.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 600