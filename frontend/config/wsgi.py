"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Asegurar que 'frontend' y sus carpetas estén en sys.path para Vercel Serverless
file_dir = Path(__file__).resolve().parent
frontend_dir = str(file_dir.parent)
repo_dir = str(file_dir.parent.parent)

for d in [frontend_dir, str(file_dir), repo_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
app = application  # Alias para compatibilidad con Vercel
