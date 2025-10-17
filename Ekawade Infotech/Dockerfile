# Use an official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# copy requirements first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copy application
COPY . /app

# ensure writable dir for sqlite
RUN mkdir -p /app/data && chown -R root:root /app/data

EXPOSE ${PORT}

# Use gunicorn to serve the app; wsgi.py exposes `application`
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:application", "--workers", "2"]
