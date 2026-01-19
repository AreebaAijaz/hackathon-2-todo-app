"""Chat API routes for AI-powered task management."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database import get_session
from models import Conversation, Message
from auth.dependencies import get_current_user
from agents import Orchestrator, process_message
from skills import MessageContext

router = APIRouter(prefix="/api", tags=["chat"])


# ============== Request/Response Schemas ==============

class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[int] = Field(default=None, description="Existing conversation ID")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    response: str
    conversation_id: int
    message_id: int
    agent_used: Optional[str] = None


class ConversationResponse(BaseModel):
    """Response schema for conversation listing."""
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int


class MessageResponse(BaseModel):
    """Response schema for message in conversation."""
    id: int
    role: str
    content: str
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    """Response schema for conversation with messages."""
    id: int
    title: Optional[str]
    created_at: datetime
    messages: List[MessageResponse]


# ============== Chat Endpoint ==============

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Process a chat message and return AI response.

    This endpoint:
    1. Creates or retrieves a conversation
    2. Saves the user message
    3. Processes through the AI orchestrator
    4. Saves and returns the assistant response

    Args:
        request: ChatRequest with message and optional conversation_id

    Returns:
        ChatResponse with AI response and conversation info
    """
    # Get or create conversation
    conversation = None
    if request.conversation_id:
        statement = select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(statement).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

    if not conversation:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            title=_generate_title(request.message),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow(),
    )
    session.add(user_message)
    session.commit()
    session.refresh(user_message)

    # Load conversation history for context
    history = _load_conversation_history(session, conversation.id)

    # Process through orchestrator
    orchestrator = Orchestrator(user_id=user_id)
    result = orchestrator.process(
        user_message=request.message,
        conversation_history=history
    )

    # Save assistant response
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=result.response,
        created_at=datetime.utcnow(),
    )
    session.add(assistant_message)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()
    session.refresh(assistant_message)

    return ChatResponse(
        response=result.response,
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        agent_used=result.agent_used,
    )


# ============== Conversation Endpoints ==============

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all conversations for the authenticated user.

    Returns:
        List of conversations with message counts, newest first.
    """
    statement = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc())

    conversations = session.exec(statement).all()

    # Get message counts
    result = []
    for conv in conversations:
        count_stmt = select(Message).where(Message.conversation_id == conv.id)
        messages = session.exec(count_stmt).all()
        result.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(messages),
        ))

    return result


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific conversation with all messages.

    Args:
        conversation_id: The conversation ID.

    Returns:
        Conversation with all messages.

    Raises:
        404: If conversation not found or not owned by user.
    """
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    conversation = session.exec(statement).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get messages
    msg_statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc())
    messages = session.exec(msg_statement).all()

    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a conversation and all its messages.

    Args:
        conversation_id: The conversation ID.

    Returns:
        Confirmation message.

    Raises:
        404: If conversation not found or not owned by user.
    """
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    conversation = session.exec(statement).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Delete all messages first
    msg_statement = select(Message).where(Message.conversation_id == conversation_id)
    messages = session.exec(msg_statement).all()
    for msg in messages:
        session.delete(msg)

    # Delete conversation
    session.delete(conversation)
    session.commit()

    return {"message": "Conversation deleted successfully"}


# ============== Helper Functions ==============

def _generate_title(message: str) -> str:
    """Generate a conversation title from the first message."""
    # Take first 50 chars, clean up
    title = message.strip()[:50]
    if len(message) > 50:
        title += "..."
    return title


def _load_conversation_history(session: Session, conversation_id: int) -> List[MessageContext]:
    """Load conversation history as MessageContext objects."""
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc())

    messages = session.exec(statement).all()

    return [
        MessageContext(role=m.role, content=m.content)
        for m in messages
        if m.role in ("user", "assistant")  # Exclude system messages
    ]
