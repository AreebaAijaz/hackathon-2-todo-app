"""ChatKit Session API for OpenAI Hosted ChatKit.

This endpoint creates OpenAI sessions that the frontend ChatKit widget
can use to communicate directly with OpenAI while using our custom tools.
"""

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from openai import OpenAI

from auth.dependencies import get_current_user

router = APIRouter(prefix="/api/chatkit", tags=["chatkit-session"])


# Tool definitions for OpenAI session
CHATKIT_TOOLS = [
    {
        "type": "function",
        "name": "add_task",
        "description": "Add a new task to the user's task list",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the task"
                },
                "description": {
                    "type": "string",
                    "description": "Optional description of the task"
                }
            },
            "required": ["title"]
        }
    },
    {
        "type": "function",
        "name": "list_tasks",
        "description": "List tasks with optional filtering by status",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter by task status"
                }
            }
        }
    },
    {
        "type": "function",
        "name": "complete_task",
        "description": "Mark a task as completed",
        "parameters": {
            "type": "object",
            "properties": {
                "task_identifier": {
                    "type": "string",
                    "description": "Task ID or title to identify the task"
                }
            },
            "required": ["task_identifier"]
        }
    },
    {
        "type": "function",
        "name": "delete_task",
        "description": "Delete a task from the list",
        "parameters": {
            "type": "object",
            "properties": {
                "task_identifier": {
                    "type": "string",
                    "description": "Task ID or title to identify the task"
                }
            },
            "required": ["task_identifier"]
        }
    },
    {
        "type": "function",
        "name": "update_task",
        "description": "Update a task's title or description",
        "parameters": {
            "type": "object",
            "properties": {
                "task_identifier": {
                    "type": "string",
                    "description": "Task ID or title to identify the task"
                },
                "new_title": {
                    "type": "string",
                    "description": "New title for the task"
                },
                "new_description": {
                    "type": "string",
                    "description": "New description for the task"
                }
            },
            "required": ["task_identifier"]
        }
    }
]

SYSTEM_INSTRUCTIONS = """You are a helpful AI assistant for task management.
You help users create, view, complete, and manage their tasks.

When users ask about tasks, use the available tools:
- add_task: Create new tasks
- list_tasks: Show tasks (filter by all/pending/completed)
- complete_task: Mark tasks as done
- delete_task: Remove tasks
- update_task: Modify task title or description

Be conversational and friendly. Confirm actions clearly.
If a user's request is ambiguous, ask for clarification.
Format task lists nicely for readability."""


class SessionResponse(BaseModel):
    """Response containing the client secret for ChatKit."""
    client_secret: str
    session_id: str


class RefreshRequest(BaseModel):
    """Request to refresh an existing session."""
    token: str


@router.post("/session", response_model=SessionResponse)
async def create_session(
    user_id: str = Depends(get_current_user),
):
    """Create a new ChatKit session.

    This endpoint creates an OpenAI session configured with our task
    management tools. The returned client_secret is used by the frontend
    ChatKit widget to communicate directly with OpenAI.

    Returns:
        SessionResponse with client_secret for ChatKit initialization
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        client = OpenAI(api_key=api_key)

        # Create a new session with our tools
        # Note: This uses OpenAI's Realtime API session endpoint
        session = client.beta.realtime.sessions.create(
            model="gpt-4o-realtime-preview",
            instructions=SYSTEM_INSTRUCTIONS,
            tools=CHATKIT_TOOLS,
            tool_choice="auto",
        )

        return SessionResponse(
            client_secret=session.client_secret.value,
            session_id=session.id
        )

    except Exception as e:
        # If Realtime API is not available, try responses API
        try:
            # Use the responses API for ChatKit
            response = client.responses.create(
                model="gpt-4o",
                instructions=SYSTEM_INSTRUCTIONS,
                tools=CHATKIT_TOOLS,
            )

            return SessionResponse(
                client_secret=response.client_secret,
                session_id=response.id
            )
        except Exception as inner_e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create session: {str(e)} / {str(inner_e)}"
            )


@router.post("/refresh", response_model=SessionResponse)
async def refresh_session(
    request: RefreshRequest,
    user_id: str = Depends(get_current_user),
):
    """Refresh an existing ChatKit session.

    Called when the current session token is about to expire.

    Args:
        request: Contains the current token to refresh

    Returns:
        SessionResponse with new client_secret
    """
    # For now, just create a new session
    # In production, you might want to preserve conversation state
    return await create_session(user_id=user_id)
