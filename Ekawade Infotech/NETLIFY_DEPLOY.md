Netlify deployment guide — Ekawade Infotech booking UI

Goal: host the static frontend (`infotech.html` and `admin.html`) on Netlify and proxy API calls to your Flask backend (hosted elsewhere, e.g., Render).

Prerequisites
- Netlify account
- Project repo with static files (this repo)
- A running backend URL (e.g., https://ekawade.onrender.com)

Steps
1. Add `_redirects` and `netlify.toml` (already present in repo). Edit them to replace `<BACKEND_HOST>` with your backend host (e.g., ekawade.onrender.com).
2. Push the repo to GitHub.
3. In Netlify dashboard: New site from Git -> choose your repo -> Deploy site.
4. After deploy, configure a custom domain (e.g., `www.ekawadeinfotech.in`) in Netlify Domain settings and follow DNS instructions.
5. Netlify provides automatic Let's Encrypt certificates for TLS.

Proxy behavior
- Netlify will rewrite `/book`, `/bookings/*`, `/export`, and `/images/*` to your backend host so the frontend can call relative API paths.

Smoke tests
- Visit https://<your-netlify-site>/infotech.html — the site should load.
- Perform a booking via the UI and ensure the backend receives it.
- Visit https://<your-netlify-site>/admin and verify admin functions (login, list, delete, export) work through the proxy.

Notes
- This pattern keeps static assets on Netlify while your Flask app runs on a server with a persistent DB.
- If you host backend on Render, use the Render URL (no trailing slash) in `_redirects`/`netlify.toml`.
- If you prefer the backend to be on the same domain for cookie-based sessions, configure your provider accordingly (CORS and cookies require proper domain and TLS settings).
