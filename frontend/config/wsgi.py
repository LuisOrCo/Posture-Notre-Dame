"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Asegurar que 'frontend' esté en sys.path para Vercel Serverless
frontend_dir = str(Path(__file__).resolve().parent.parent)
if frontend_dir not in sys.path:
    sys.path.insert(0, frontend_dir)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
app = application  # Alias para compatibilidad con Vercel
