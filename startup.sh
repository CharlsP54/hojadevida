#!/bin/bash
set -e

echo "📁 Contenido de wwwroot:"
ls -la

# Si manage.py está en una subcarpeta, AJUSTA este cd
# Ejemplo: cd backend
# Ejemplo: cd hojadevida
cd .

echo "🚀 Iniciando Gunicorn..."

gunicorn NOMBRE_REAL_DEL_PROYECTO.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --timeout 120
