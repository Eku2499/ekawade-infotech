# Run this on Windows PowerShell to serve with Waitress
# Usage: .\run_waitress.ps1
python -m pip install waitress -q
python -c "from waitress import serve; import booking_api; serve(booking_api.app, host='0.0.0.0', port=8000)"
