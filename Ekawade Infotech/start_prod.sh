#!/bin/sh
# Production start: ensure DB initialized and start gunicorn
export FLASK_ENV=production
export BOOKING_DB=${BOOKING_DB:-"$(pwd)/bookings.db"}
python -c "from booking_api import init_db; init_db(migrate_from_excel=False)"
exec gunicorn -w 4 -b 0.0.0.0:8000 booking_api:app
