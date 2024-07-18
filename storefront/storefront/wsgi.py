"""
WSGI config for storefront project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""
import os
import logging
from django.core.wsgi import get_wsgi_application

print("Loading WSGI application")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storefront.settings')
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug('Loading WSGI application')
application = get_wsgi_application()
logger.debug('WSGI application loaded')
