#!/bin/sh
# Simple script to run the app with gunicorn
# Usage: ./run_gunicorn.sh

exec gunicorn -w 4 -b 0.0.0.0:8000 booking_api:app
