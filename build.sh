#!/usr/bin/env bash
# Salir si ocurre cualquier error
set -o errexit

# 1. Instalar librerías
pip install -r requirements.txt

# 2. Recolectar archivos estáticos (CSS, Imágenes, JS)
python manage.py collectstatic --no-input

# 3. Crear las tablas en la Base de Datos (¡ESTO ES LO QUE TE FALTA!)
python manage.py migrate