"""SQLModel models for the Todo application."""

from datetime import datetime
from typing import Optional, List
import json

from sqlmodel import Field, SQLModel, Relationship


# ============== Phase II Models ==============

class Task(SQLModel, table=True):
    """Task model for todo items.

    Attributes:
        id: Auto-incrementing primary key.
        user_id: Foreign key to Better Auth user table.
        title: Task title (required).
        description: Task description (optional).
        completed: Whether task is complete.
        created_at: Task creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # References Better Auth "user" table
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=500)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Phase III Models ==============

class Conversation(SQLModel, table=True):
    """Conversation model for chat sessions.

    Attributes:
        id: Auto-incrementing primary key.
        user_id: Foreign key to Better Auth user table.
        title: Optional conversation title.
        created_at: Conversation creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # References Better Auth "user" table
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """Message model for chat messages.

    Attributes:
        id: Auto-incrementing primary key.
        conversation_id: Foreign key to conversations table.
        user_id: Foreign key to Better Auth user table.
        role: Message role (user/assistant/system).
        content: Message content.
        tool_calls: JSON string of tool calls made (optional).
        created_at: Message creation timestamp.
    """

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True)
    role: str = Field(max_length=20)  # user, assistant, system
    content: str = Field(default="")
    tool_calls: Optional[str] = Field(default=None)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    def get_tool_calls_list(self) -> List[dict]:
        """Parse tool_calls JSON string to list."""
        if self.tool_calls:
            return json.loads(self.tool_calls)
        return []

    def set_tool_calls_list(self, calls: List[dict]) -> None:
        """Set tool_calls from list to JSON string."""
        self.tool_calls = json.dumps(calls) if calls else None
