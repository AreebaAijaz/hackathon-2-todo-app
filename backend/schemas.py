"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Task schemas
class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    user_id: str
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
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
