"""Pydantic schemas for request/response validation."""

import re
from datetime import datetime, timezone
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator, computed_field


# ============== Tag Validation ==============

TAG_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def validate_tags(tags: List[str]) -> List[str]:
    """Validate tag list: max 10 tags, each max 30 chars, alphanumeric/hyphens/underscores."""
    if len(tags) > 10:
        raise ValueError("Maximum 10 tags per task")
    for tag in tags:
        tag = tag.strip()
        if len(tag) > 30:
            raise ValueError(f"Tag '{tag}' exceeds 30 characters")
        if not TAG_PATTERN.match(tag):
            raise ValueError(
                f"Tag '{tag}' contains invalid characters. "
                "Only alphanumeric, hyphens, and underscores allowed."
            )
    return [t.strip().lower() for t in tags]


# ============== Task Schemas ==============

class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)
    priority: str = Field(default="medium", pattern=r"^(low|medium|high|urgent)$")
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    recurring_pattern: str = Field(default="none", pattern=r"^(none|daily|weekly|monthly)$")

    @field_validator("tags")
    @classmethod
    def validate_tags_field(cls, v: List[str]) -> List[str]:
        return validate_tags(v)


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    priority: Optional[str] = Field(default=None, pattern=r"^(low|medium|high|urgent)$")
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    recurring_pattern: Optional[str] = Field(default=None, pattern=r"^(none|daily|weekly|monthly)$")

    @field_validator("tags")
    @classmethod
    def validate_tags_field(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            return validate_tags(v)
        return v


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    user_id: str
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    priority: str
    tags: List[str]
    due_date: Optional[datetime]
    recurring_pattern: str

    @computed_field
    @property
    def is_overdue(self) -> bool:
        """Task is overdue if due_date is in the past and task is not completed."""
        if self.due_date and not self.completed:
            return self.due_date < datetime.now(timezone.utc)
        return False

    class Config:
        from_attributes = True


# ============== Bulk Operation Schemas ==============

class BulkOperations(BaseModel):
    """Operations to apply in a bulk update."""

    priority: Optional[str] = Field(default=None, pattern=r"^(low|medium|high|urgent)$")
    add_tags: Optional[List[str]] = None
    remove_tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    recurring_pattern: Optional[str] = Field(default=None, pattern=r"^(none|daily|weekly|monthly)$")

    @field_validator("add_tags")
    @classmethod
    def validate_add_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            return validate_tags(v)
        return v


class BulkUpdateRequest(BaseModel):
    """Request body for bulk task update."""

    task_ids: List[int] = Field(..., min_length=1, max_length=50)
    operations: BulkOperations


class BulkUpdateResponse(BaseModel):
    """Response for bulk task update."""

    updated_count: int
    task_ids: List[int]


# ============== Tags Response ==============

class TagsResponse(BaseModel):
    """Response for user tags endpoint."""

    tags: List[str]
    count: int


# ============== Auth Schemas ==============

class UserResponse(BaseModel):
    """Schema for user response."""

    id: str
    email: str
    name: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for simple message response."""

    message: str


class ErrorResponse(BaseModel):
    """Schema for error response."""

    detail: str
