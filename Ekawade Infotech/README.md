# Ekawade Infotech - Booking API

This project is a small Flask-based booking API that stores bookings in SQLite and exposes a simple admin UI.

## Production deployment

Two options are provided below: Linux (Gunicorn + systemd) and Windows (Waitress + PowerShell).

Prerequisites
- Python 3.11
- Install dependencies: `pip install -r requirements.txt`

Run with Gunicorn (Linux)

1. Copy the project to `/var/www/ekawade-infotech`.
2. Create a virtualenv and install requirements.
3. Ensure `BOOKING_DB` environment var is set or default path is used.
4. Use the provided systemd unit `booking.service` (copy to `/etc/systemd/system/booking.service`).
5. Start and enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now booking.service
```

Run with Waitress (Windows)

```powershell
# In project dir
python -m pip install -r requirements.txt
pwsh .\run_waitress.ps1
```

Serving admin UI
- Visit `http://<host>:8000/admin` to access the admin panel.

Security
- For production, protect the admin route with authentication and run behind TLS (e.g., use a reverse proxy with Let's Encrypt).

Domain setup
- Point `www.ekawadeinfotech.in` A record to the server IP and configure TLS at the reverse proxy (nginx) or use the hosting provider's TLS feature.

Docker
------

Build the Docker image locally:

```powershell
docker build -t ekawade-infotech:latest .
```

Run the container (exposes port 8000):

```powershell
docker run -p 8000:8000 -e ADMIN_AUTH=1 -e ADMIN_USER=admin -e ADMIN_PASS=s3cr3t ekawade-infotech:latest
```

CI/CD
------

A GitHub Actions workflow is included at `.github/workflows/ci.yml`. It runs tests and builds/pushes a Docker image to GitHub Container Registry (GHCR) using the default `GITHUB_TOKEN`.

Enabling admin auth in production
---------------------------------

Set these env vars on the host or in your container orchestration platform:

- `SECRET_KEY` - a long random value
- `ADMIN_USER` - admin username
- `ADMIN_PASS` - admin password
- `ADMIN_AUTH=1` - enables admin auth enforcement

GitHub Actions -> Docker Hub
----------------------------

To allow GitHub Actions to push the built image to Docker Hub, add the following repository secrets in your GitHub repo (Settings → Secrets → Actions):

- `DOCKERHUB_USERNAME` — your Docker Hub username or organization
- `DOCKERHUB_TOKEN` — Docker Hub access token or password (recommended: use an access token)

The CI workflow will tag the image as `<DOCKERHUB_USERNAME>/ekawade-infotech:latest` and also with the commit SHA.
[![Netlify Status](https://api.netlify.com/api/v1/badges/6b6c731a-a54d-4780-93ea-5c9fa801c5ef/deploy-status)](https://app.netlify.com/projects/ekawadeinfotech/deploys)


