Render deployment guide — Ekawade Infotech booking API

This file contains step-by-step instructions to deploy the project to Render using the repo's Dockerfile or render.yaml.

Prerequisites
- A Render account (https://render.com)
- GitHub repository with this project

Option A — Deploy using render.yaml (recommended)
1. Push your changes to GitHub (main branch). Ensure the repo contains `render.yaml` at the root.
2. In Render dashboard, click "New" → "Web Service" → "Connect a repository" and select your repo.
3. Render will detect `render.yaml` and show the service configuration. Choose the service `ekawade-infotech` and confirm.
4. In the service settings, review environment variables and replace the sample values:
   - `ADMIN_PASS` — set a strong password
   - `SECRET_KEY` — set a long random string
   - Optionally change `ADMIN_USER` and `BOOKING_DB` (default uses `/tmp/bookings.db` inside the container)
5. Deploy. Render will build the Docker image using the repository's Dockerfile (or the image specified).
6. After deployment, go to the service's URL. You can add a custom domain in the Render UI and follow prompts to enable HTTPS (automatic with Let's Encrypt).

Option B — Create a Docker Web Service manually (if not using render.yaml)
1. In Render, "New" → "Web Service" → select your GitHub repo.
2. Choose "Docker" as the environment.
3. Set the start command blank (Render uses Dockerfile's CMD). Set the build command to blank.
4. Configure environment variables (see step 4 above).
5. Deploy and attach a custom domain if desired.

Environment variables to set (minimum)
- ADMIN_AUTH=1
- ADMIN_USER=admin
- ADMIN_PASS=<strong-password>
- SECRET_KEY=<long-random-secret>
- BOOKING_DB=/tmp/bookings.db

DNS / Domain
- Add `www.ekawadeinfotech.in` as a custom domain in Render. Follow Render's DNS instructions to add CNAME/A records.
- Enable HTTPS in Render — Render obtains a Let's Encrypt cert automatically.

Smoke-tests to run after deploy
1. Health endpoint
   - Visit: https://<your-service>.onrender.com/bookings
   - Expect: 200 JSON (may be empty array)
2. Submit booking (from local or using curl):
   ```bash
   curl -X POST https://<your-service>.onrender.com/book \
     -H "Content-Type: application/json" \
     -d '{"name":"Test","email":"t@example.com","date":"2025-10-20","phone":"900"}'
   ```
   - Expect: JSON {"status":"success"}
3. Verify in admin UI
   - Visit: https://<your-service>.onrender.com/admin
   - Login with `ADMIN_USER`/`ADMIN_PASS` and verify the booking appears.
4. Export CSV
   - Visit https://<your-service>.onrender.com/export (requires admin login) or click the Admin "Export" link.
   - Expect: CSV download of bookings.
5. Delete booking (Admin)
   - Use the Admin UI to delete a booking and verify it's removed via GET /bookings.

Notes and recommendations
- For production, store secrets (ADMIN_PASS, SECRET_KEY) in Render's Environment variables UI — do not hardcode in `render.yaml`.
- Consider using persistent storage for the SQLite DB or switch to a hosted DB if the volume of bookings grows or you need persistence across restarts.
- Render's ephemeral containers store files in `/tmp` only while the container is running; if you need persistent storage, use an external DB.

Render secrets and recommended setup
----------------------------------
Use Render's Secrets feature (recommended) for sensitive values instead of putting them into `render.yaml`. To add secrets:

1. Open your Render service page → "Environment" → "Secrets" → "Add Secret".
2. Add the following secrets:
   - `ADMIN_USER` — admin username
   - `ADMIN_PASS` — admin password
   - `SECRET_KEY` — a long random secret
3. The provided `render.yaml` references these secrets by key. Do NOT commit actual secret values to the repo.

If you prefer, you can also set non-secret environment variables from the Render UI under the Environment panel.


If you'd like I can also produce a `render.yaml` variant that does not include secret values (safer) and add specific `healthCheckPath` changes. Would you like me to remove credentials from the current `render.yaml` and add guidance to set them in the Render UI instead?