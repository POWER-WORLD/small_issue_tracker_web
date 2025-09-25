from typing import Optional

from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Query

from .models import Issue, IssueCreate, IssueListResponse, IssueUpdate
from .storage import IssueStore

app = FastAPI(title="Issue Tracker API")

# CORS: default allow all methods/headers, but disallow credentials when using wildcard origins
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)

store = IssueStore()


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
	response: Response = await call_next(request)
	# Basic hardening headers
	response.headers.setdefault("X-Content-Type-Options", "nosniff")
	response.headers.setdefault("X-Frame-Options", "DENY")
	response.headers.setdefault("Referrer-Policy", "no-referrer")
	response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
	# CSP: allow same-origin and inline styles for this simple app; tighten as needed
	response.headers.setdefault(
		"Content-Security-Policy",
		"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self' http://127.0.0.1:8000 http://localhost:8000; img-src 'self' data:;"
	)
	return response


_ALLOWED_SORT_FIELDS = {"id", "title", "status", "priority", "assignee", "createdAt", "updatedAt"}
_ALLOWED_SORT_DIRS = {"asc", "desc"}


@app.get("/health")
def health():
	return {"status": "ok"}


@app.get("/issues", response_model=IssueListResponse)
def list_issues(
	search: Optional[str] = Query(default=None),
	status: Optional[str] = Query(default=None),
	priority: Optional[str] = Query(default=None),
	assignee: Optional[str] = Query(default=None),
	sortBy: Optional[str] = Query(default="updatedAt"),
	sortDir: Optional[str] = Query(default="desc"),
	page: int = Query(default=1, ge=1),
	pageSize: int = Query(default=10, ge=1, le=100),
):
	# Validate sort inputs
	sort_by = sortBy if sortBy in _ALLOWED_SORT_FIELDS else "updatedAt"
	sort_dir = sortDir.lower() if sortDir and sortDir.lower() in _ALLOWED_SORT_DIRS else "desc"
	return store.list_issues(
		search=search,
		status=status,
		priority=priority,
		assignee=assignee,
		sort_by=sort_by,
		sort_dir=sort_dir,
		page=page,
		page_size=pageSize,
	)


@app.get("/issues/{issue_id}", response_model=Issue)
def get_issue(issue_id: int):
	issue = store.get_issue(issue_id)
	if not issue:
		raise HTTPException(status_code=404, detail="Issue not found")
	return issue


@app.post("/issues", response_model=Issue, status_code=201)
def create_issue(payload: IssueCreate):
	return store.create_issue(payload)


@app.put("/issues/{issue_id}", response_model=Issue)
def update_issue(issue_id: int, payload: IssueUpdate):
	updated = store.update_issue(issue_id, payload)
	if not updated:
		raise HTTPException(status_code=404, detail="Issue not found")
	return updated


# For `python -m backend.app` local run convenience
if __name__ == "__main__":
	import uvicorn

	uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
