from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


Status = Literal["open", "in_progress", "closed"]
Priority = Literal["low", "medium", "high"]


class Issue(BaseModel):
	id: int
	title: str
	description: Optional[str] = None
	status: Status = "open"
	priority: Priority = "medium"
	assignee: Optional[str] = None
	createdAt: datetime
	updatedAt: datetime


class IssueCreate(BaseModel):
	title: str = Field(min_length=1)
	description: Optional[str] = None
	status: Optional[Status] = None
	priority: Optional[Priority] = None
	assignee: Optional[str] = None


class IssueUpdate(BaseModel):
	title: Optional[str] = None
	description: Optional[str] = None
	status: Optional[Status] = None
	priority: Optional[Priority] = None
	assignee: Optional[str] = None


class IssueListResponse(BaseModel):
	items: List[Issue]
	total: int
	page: int
	pageSize: int
