## Issue Tracker

### Backend (FastAPI)

Prereqs: Python 3.10+

Install deps:

```bash
pip install -r backend/requirements.txt
```

Run:

```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

API endpoints:
- GET `/health`
- GET `/issues` query params: `search`, `status`, `priority`, `assignee`, `sortBy`, `sortDir` (asc|desc), `page`, `pageSize`
- GET `/issues/{id}`
- POST `/issues`
- PUT `/issues/{id}`

Data is stored in `backend/data/issues.json`.

Security hardening included:
- CORS set to wildcard origins without credentials. For production, restrict `allow_origins`.
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, and a basic `Content-Security-Policy`.
- `sortBy`/`sortDir` validated against an allowlist.

To restrict CORS to your domain, adjust in `backend/app.py`:

```python
app.add_middleware(
	CORSMiddleware,
	allow_origins=["https://your-frontend.example"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)
```

### Frontend (Static)
Open `frontend/index.html` in a browser. By default it calls `http://127.0.0.1:8000`.

To point to a different API, set `window.API_BASE` in DevTools console before using the app:

```js
window.API_BASE = 'http://localhost:8000';
```

Security notes:
- User-supplied fields are escaped before inserting into the DOM.
- Avoid enabling remote scripts or inline event handlers that bypass CSP.
