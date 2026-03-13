import json
import os
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import Issue, IssueCreate, IssueListResponse, IssueUpdate


class IssueStore:
	"""Thread-safe JSON file store for issues."""

	def __init__(self, data_dir: str = "data", filename: str = "issues.json") -> None:
		self._lock = threading.RLock()
		self._data_dir = os.path.join(os.path.dirname(__file__), data_dir)
		self._file_path = os.path.join(self._data_dir, filename)
		self._issues: List[Dict[str, Any]] = []
		self._next_id: int = 1
		self._ensure_storage()
		self._load()

	def _ensure_storage(self) -> None:
		os.makedirs(self._data_dir, exist_ok=True)
		if not os.path.exists(self._file_path):
			with open(self._file_path, "w", encoding="utf-8") as f:
				json.dump({"nextId": 1, "issues": []}, f)

	def _load(self) -> None:
		with self._lock:
			with open(self._file_path, "r", encoding="utf-8") as f:
				data = json.load(f)
			self._issues = data.get("issues", [])
			self._next_id = int(data.get("nextId", 1))

	def _save(self) -> None:
		with self._lock:
			with open(self._file_path, "w", encoding="utf-8") as f:
				json.dump({"nextId": self._next_id, "issues": self._issues}, f, ensure_ascii=False, indent=2, default=str)

	def list_issues(
		self,
		search: Optional[str] = None,
		status: Optional[str] = None,
		priority: Optional[str] = None,
		assignee: Optional[str] = None,
		sort_by: Optional[str] = "updatedAt",
		sort_dir: Optional[str] = "desc",
		page: int = 1,
		page_size: int = 10,
	) -> IssueListResponse:
		with self._lock:
			items = list(self._issues)

		# Search by title
		if search:
			needle = search.lower()
			items = [i for i in items if needle in i.get("title", "").lower()]

		# Filters
		if status:
			items = [i for i in items if i.get("status") == status]
		if priority:
			items = [i for i in items if i.get("priority") == priority]
		if assignee:
			items = [i for i in items if (i.get("assignee") or "") == assignee]

		# Sorting
		key = sort_by or "updatedAt"
		reverse = (sort_dir or "desc").lower() == "desc"

		def sort_key(i: Dict[str, Any]):
			value = i.get(key)
			# Parse datetimes for createdAt/updatedAt if necessary
			if key in ("createdAt", "updatedAt") and isinstance(value, str):
				try:
					return datetime.fromisoformat(value.replace("Z", "+00:00"))
				except Exception:
					return datetime.min
			return value

		try:
			items.sort(key=sort_key, reverse=reverse)
		except Exception:
			# If invalid sort key, fall back to updatedAt
			items.sort(key=lambda i: i.get("updatedAt", ""), reverse=True)

		total = len(items)
		start = (page - 1) * page_size
		end = start + page_size
		page_items = items[start:end]

		# Convert to Issue models
		issue_models = [Issue(**i) for i in page_items]
		return IssueListResponse(items=issue_models, total=total, page=page, pageSize=page_size)

	def get_issue(self, issue_id: int) -> Optional[Issue]:
		with self._lock:
			for i in self._issues:
				if i.get("id") == issue_id:
					return Issue(**i)
		return None

	def create_issue(self, payload: IssueCreate) -> Issue:
		now = datetime.utcnow().isoformat() + "Z"
		with self._lock:
			issue_dict = payload.model_dump(exclude_unset=True)
			issue_dict.setdefault("status", "open")
			issue_dict.setdefault("priority", "medium")
			issue = {
				"id": self._next_id,
				"title": issue_dict.get("title"),
				"description": issue_dict.get("description"),
				"status": issue_dict.get("status"),
				"priority": issue_dict.get("priority"),
				"assignee": issue_dict.get("assignee"),
				"createdAt": now,
				"updatedAt": now,
			}
			self._issues.append(issue)
			self._next_id += 1
			self._save()
			return Issue(**issue)

	def update_issue(self, issue_id: int, payload: IssueUpdate) -> Optional[Issue]:
		now = datetime.utcnow().isoformat() + "Z"
		with self._lock:
			for idx, i in enumerate(self._issues):
				if i.get("id") == issue_id:
					updates = payload.model_dump(exclude_unset=True)
					updated = {**i, **updates, "updatedAt": now}
					self._issues[idx] = updated
					self._save()
					return Issue(**updated)
		return None

	def delete_issue(self, issue_id: int) -> bool:
		with self._lock:
			for idx, i in enumerate(self._issues):
				if i.get("id") == issue_id:
					del self._issues[idx]
					self._save()
					return True
		return False
