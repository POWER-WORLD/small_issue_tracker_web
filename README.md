# Small Issue Tracker Web

Small Issue Tracker Web is a lightweight full-stack issue tracker with a FastAPI backend and a static HTML/CSS/JavaScript frontend.

## What this site does

- Create issues
- View all issues in a sortable table
- Filter by status, priority, assignee, and title search
- Paginate results
- Edit existing issues
- Delete issues
- View issue details in a side drawer

## Tech stack

- Backend: FastAPI, Pydantic
- Frontend: Vanilla HTML, CSS, JavaScript
- Storage: JSON file on disk (`backend/data/issues.json`)

## Project structure

```text
README.md
backend/
	app.py
	models.py
	storage.py
	requirements.txt
	data/
		issues.json
frontend/
	index.html
	app.js
	styles.css
```

## Prerequisites

- Python 3.10+
- Modern browser (Chrome, Edge, Firefox)

## Backend setup and run

clone site and navigate to project root:

```bash

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Run API server:

```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

API will be available at:

- `http://127.0.0.1:8000`

Health check:

- `GET /health`

## Frontend setup and run

Open the frontend file in your browser:

- `frontend/index.html`

By default, frontend calls:

- `http://127.0.0.1:8000`

If your API is running on a different host/port, set this in browser console before using the app:

```js
window.API_BASE = 'http://localhost:8000';
```

## API reference

Base URL: `http://127.0.0.1:8000`

### 1) Health

- Method: `GET`
- Path: `/health`
- Response:

```json
{ "status": "ok" }
```

### 2) List issues

- Method: `GET`
- Path: `/issues`
- Query parameters:
	- `search` (optional): title contains text
	- `status` (optional): `open`, `in_progress`, `closed`
	- `priority` (optional): `low`, `medium`, `high`
	- `assignee` (optional): exact assignee name
	- `sortBy` (optional): `id`, `title`, `status`, `priority`, `assignee`, `createdAt`, `updatedAt`
	- `sortDir` (optional): `asc`, `desc`
	- `page` (optional, default `1`)
	- `pageSize` (optional, default `10`, max `100`)

Response shape:

```json
{
	"items": [
		{
			"id": 1,
			"title": "Login form bug",
			"description": "...",
			"status": "open",
			"priority": "high",
			"assignee": "Alex",
			"createdAt": "2026-03-13T10:00:00Z",
			"updatedAt": "2026-03-13T10:00:00Z"
		}
	],
	"total": 1,
	"page": 1,
	"pageSize": 10
}
```

### 3) Get single issue

- Method: `GET`
- Path: `/issues/{id}`
- Success: `200`
- Not found: `404`

### 4) Create issue

- Method: `POST`
- Path: `/issues`
- Body:

```json
{
	"title": "Issue title",
	"description": "Optional details",
	"status": "open",
	"priority": "medium",
	"assignee": "Optional name"
}
```

- Success: `201`

### 5) Update issue

- Method: `PUT`
- Path: `/issues/{id}`
- Body: same fields as create (all optional except your own app-level rules)
- Success: `200`
- Not found: `404`

### 6) Delete issue

- Method: `DELETE`
- Path: `/issues/{id}`
- Success: `204`
- Not found: `404`

## Data model

Issue fields:

- `id`: integer
- `title`: string
- `description`: string or null
- `status`: `open` | `in_progress` | `closed`
- `priority`: `low` | `medium` | `high`
- `assignee`: string or null
- `createdAt`: ISO datetime string
- `updatedAt`: ISO datetime string

## Security and behavior notes

- CORS currently allows all origins (`*`) without credentials for local development convenience.
- Security headers are added in middleware:
	- `X-Content-Type-Options`
	- `X-Frame-Options`
	- `Referrer-Policy`
	- `Permissions-Policy`
	- `Content-Security-Policy`
- Frontend escapes user text before inserting in HTML.
- Sorting input is validated through an allowlist on the backend.

For production, replace wildcard CORS with your frontend domain.

## Development notes

- Data persists in `backend/data/issues.json`.
- `IssueStore` uses a thread lock for safe concurrent file access.
- Default sorting in the app is `updatedAt desc`.

## Quick manual test flow

1. Start backend.
2. Open frontend in browser.
3. Create 2-3 issues.
4. Search and filter issues.
5. Edit one issue.
6. Delete one issue and verify it disappears from the table.
