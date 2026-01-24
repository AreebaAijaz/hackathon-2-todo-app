"""ChatKit API routes - Custom Backend for ChatKit UI.

Implements the ChatKit protocol to work with OpenAI's ChatKit UI component
while using our own backend logic, tools, and database.

Flow: ChatKit UI → This Backend → Your Logic/Tools → SSE Response → ChatKit UI
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator

from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from auth.dependencies import get_current_user
from chatkit_server import get_chatkit_server
from database import get_session
from models import Conversation, Message

router = APIRouter(prefix="/api", tags=["chatkit"])


class ChatKitMessage(BaseModel):
    """Message format in ChatKit requests."""
    role: str
    content: str


class ChatKitRequest(BaseModel):
    """ChatKit request body format."""
    messages: Optional[List[ChatKitMessage]] = None
    message: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None
    conversation_id: Optional[int] = None


def _generate_title(message: str) -> str:
    """Generate a conversation title from the first message."""
    title = message.strip()[:50]
    if len(message) > 50:
        title += "..."
    return title


async def stream_and_save(
    server,
    user_message: str,
    user_id: str,
    conversation_history: list,
    conversation_id: Optional[int],
    db_session: Session,
) -> AsyncGenerator[str, None]:
    """Stream response and save to database after completion."""

    # Get or create conversation
    conversation = None
    if conversation_id:
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = db_session.exec(statement).first()

    if not conversation:
        conversation = Conversation(
            user_id=user_id,
            title=_generate_title(user_message),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=user_message,
        created_at=datetime.utcnow(),
    )
    db_session.add(user_msg)
    db_session.commit()

    # Stream and collect response
    full_response = ""

    async for chunk in server.process_stream(
        user_message=user_message,
        user_id=user_id,
        conversation_history=conversation_history
    ):
        yield chunk

        # Extract content from SSE data
        if "data: " in chunk:
            try:
                data_str = chunk.split("data: ")[1].split("\n")[0]
                data = json.loads(data_str)
                if data.get("type") == "response.output_text.delta" and data.get("delta"):
                    full_response += data["delta"]
                elif data.get("type") == "response.output_text.done" and data.get("text"):
                    full_response = data["text"]
            except (json.JSONDecodeError, IndexError):
                pass

    # Save assistant message after streaming completes
    if full_response:
        assistant_msg = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=full_response,
            created_at=datetime.utcnow(),
        )
        db_session.add(assistant_msg)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        db_session.add(conversation)
        db_session.commit()


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    user_id: str = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Process ChatKit requests and return streaming responses.

    Saves conversations and messages to the database for history.
    """
    # Parse request body
    try:
        body = await request.json()
    except json.JSONDecodeError:
        body = {}

    user_message = ""
    conversation_history = []
    conversation_id = body.get("conversation_id")

    # Format 1: ChatKit messages array
    if "messages" in body and body["messages"]:
        messages = body["messages"]
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        for msg in messages[:-1] if messages else []:
            conversation_history.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

    # Format 2: OpenAI Responses API format
    elif "input" in body:
        input_data = body["input"]
        if isinstance(input_data, str):
            user_message = input_data
        elif isinstance(input_data, list):
            for item in reversed(input_data):
                if isinstance(item, dict) and item.get("role") == "user":
                    content = item.get("content", [])
                    if isinstance(content, str):
                        user_message = content
                    elif isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict) and c.get("type") == "input_text":
                                user_message = c.get("text", "")
                                break
                    break
            for item in input_data[:-1] if input_data else []:
                if isinstance(item, dict):
                    conversation_history.append({
                        "role": item.get("role", "user"),
                        "content": str(item.get("content", ""))
                    })

    # Format 3: Simple message format
    elif "message" in body:
        user_message = body.get("message", "")
        conversation_history = body.get("conversation_history", [])

    if not user_message:
        async def error_stream():
            error_event = {
                "type": "error",
                "error": {"message": "No message provided", "type": "invalid_request"}
            }
            yield f"event: error\ndata: {json.dumps(error_event)}\n\n"

        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    # Get the ChatKit server
    server = get_chatkit_server()

    # Stream and save to database
    return StreamingResponse(
        stream_and_save(
            server=server,
            user_message=user_message,
            user_id=user_id,
            conversation_history=conversation_history,
            conversation_id=conversation_id,
            db_session=db_session,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/chatkit/health")
async def chatkit_health():
    """Health check for ChatKit endpoint."""
    return {"status": "ok", "service": "chatkit"}
