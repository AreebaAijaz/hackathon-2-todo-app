"""Authentication routes for the Todo API."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, text

from database import get_session
from auth.dependencies import get_current_user
from schemas import UserResponse, MessageResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/verify", response_model=MessageResponse)
async def verify_token(user_id: str = Depends(get_current_user)):
    """Verify the current session token is valid.

    Returns:
        Message confirming the token is valid.
    """
    return MessageResponse(message="Token is valid")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get the current authenticated user's information.

    Returns:
        The current user's profile.
    """
    # Query Better Auth user table
    query = text("""
        SELECT "id", "email", "name" FROM "user"
        WHERE "id" = :user_id
    """)

    result = session.exec(query, {"user_id": user_id}).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=result[0],
        email=result[1],
        name=result[2] or "",
    )
