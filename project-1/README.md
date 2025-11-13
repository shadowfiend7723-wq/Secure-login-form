# FastAPI Auth Boilerplate

A small FastAPI authentication example with MongoDB (Motor), Jinja2 HTML forms, JWT tokens and a minimal middleware for request logging and rate-limiting.

**Project structure**

- `main.py` — FastAPI application, routes for HTML forms and app configuration.
- `auth.py` — Authentication endpoints (signup, token), password hashing, JWT creation and user dependency helpers.
- `database.py` — Async Motor client and `db` reference.
- `middleware.py` — `AdvancedMiddleware` for logging, simple per-IP rate-limiting and response timing.
- `models.py` — Pydantic models for users.
- `templates/` — Jinja2 templates: `index.html`, `login.html`, `login_result.html` (and planned `signup.html`).
- `static/` — Static assets served at `/static` (e.g. `styles.css`).
- `requirements.txt` — Recommended runtime dependencies.

**Features**

- User signup with password hashing (passlib / bcrypt).
- User login via OAuth2 password flow and via an HTML form; returns a JWT access token.
- JWT tokens signed with `python-jose`.
- Basic middleware: logging, X-Process-Time header and per-IP 1-second rate limit (skips localhost and dev paths).
- Templates + static CSS for a minimal UI.

**Quick Start (local development)**

Prerequisites:
- Python 3.10+
- MongoDB running locally (default: `mongodb://localhost:27017/`)

Install dependencies:

```powershell
python -m pip install -r "c:\Users\adhik\OneDrive\Public\Tutorial tasks\project-1\requirements.txt"
```

Run the app:

```powershell
cd "c:\Users\adhik\OneDrive\Public\Tutorial tasks\project-1"
uvicorn main:app --reload --port 8000
```

Open in a browser:
- App home: `http://127.0.0.1:8000/`
- Login page: `http://127.0.0.1:8000/login`
- API docs: `http://127.0.0.1:8000/docs`

**API Endpoints (summary)**

- `POST /auth/` — Create a new user. JSON body: `{ "username": "...", "password": "..." }`.
- `POST /auth/token` — Obtain a JWT access token (OAuth2 password grant). Send as form data: `username` and `password`.
- `GET /login` — HTML login form.
- `POST /login` — Form login endpoint that renders `login_result.html` with a token on success.
- `GET /` — `index.html` with links to login/signup.

**Templates & Styling**
- Templates located in `templates/`.
- Styles are in `static/styles.css` and served at `/static/styles.css`.

**Configuration & Notes**
- Database name used in `database.py` is `new_db` (lowercase) to avoid case-differing DB name errors on some systems.
- `auth.py` contains `SECRET_KEY` and `ALGORITHM` for JWTs — replace `SECRET_KEY` with a securely stored environment variable in production.
- The middleware will skip rate-limiting for `localhost` and for dev paths such as `/login`, `/static`, `/auth`, `/docs`.

**Security Considerations**
- Do not use the hard-coded `SECRET_KEY` in production — use environment variables and a secure secret store.
- Use HTTPS in production and consider additional protections: CSRF (for form-based login flows), email verification, token revocation, and stronger password policies.

**Testing**
- A simple `test_auth.py` uses FastAPI `TestClient` for quick checks. For UI testing, run the server and use a browser.

**Development suggestions**
- Add a `signup.html` form and a POST `/signup` handler (if you want form-based user creation outside of the API).
- Add a `.env` or config module to centralize settings (database url, jwt secret, debug flags).
- Add unit tests and CI workflow to validate endpoints.

---

If you’d like, I can also:
- Add a `signup.html` template and the server-side signup handler (form + route).
- Expand the README with curl examples, sample `.env` and instructions for deploying behind a production server.
- Add a short CONTRIBUTING.md and LICENSE file.
