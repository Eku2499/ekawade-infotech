"""
WSGI entry point for production servers (gunicorn / waitress).

Usage examples:
  gunicorn -w 4 booking_api:app
  waitress-serve --listen=*:8000 booking_api:app
"""
from booking_api import app

# Expose the WSGI callable as 'application' for some servers
application = app
