#!/usr/bin/env bash
# Salir inmediatamente si un comando falla
set -e

echo "==> Aplicando migraciones de base de datos..."
python manage.py migrate

echo "==> Recolectando archivos estáticos..."
# --noinput evita que pregunte si quieres sobrescribir
python manage.py collectstatic --noinput

echo "==> Iniciando Gunicorn..."
# Ajusta 'hojadevida' si tu carpeta principal se llama diferente
exec gunicorn hojadevida.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --timeout 120