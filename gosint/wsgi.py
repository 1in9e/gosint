"""
WSGI config for gosint project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'false':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gosint.setting-prod')
    print('production')
else:
    """
    调试模式
    """
    print('debuging')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gosint.settings')

application = get_wsgi_application()
