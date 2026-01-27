#!/usr/bin/env python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess # <--- IMPORTANTE: Necesario para ejecutar comandos de Linux

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hojadevida.settings')

    # =========================================================================
    # PARCHE PARA AZURE: Instalar dependencias de WeasyPrint antes de iniciar
    # =========================================================================
    # Verificamos si estamos en Azure (Azure siempre crea la variable WEBSITE_HOSTNAME)
    if os.environ.get('WEBSITE_HOSTNAME') or os.environ.get('WEBSITE_SITE_NAME'):
        print("--- [PYTHON] DETECTADO AZURE: Verificando librerías gráficas... ---")
        try:
            # Lista de comandos para instalar lo que le falta a Azure Linux
            commands = [
                "apt-get update -qq",
                "apt-get install -y -qq libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info"
            ]
            
            for cmd in commands:
                # Ejecutamos el comando y esperamos a que termine
                subprocess.run(cmd, shell=True, check=True)
                
            print("--- [PYTHON] LIBRERÍAS INSTALADAS CON ÉXITO ---")
            
        except Exception as e:
            # Si falla, imprimimos el error pero dejamos que intente seguir
            print(f"--- [PYTHON] ERROR AL INSTALAR LIBRERÍAS: {e} ---")
    # =========================================================================

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()