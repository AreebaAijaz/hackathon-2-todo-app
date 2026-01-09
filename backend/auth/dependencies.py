"""Authentication dependencies for FastAPI routes."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select, text

from database import get_session

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> str:
    """Get the current authenticated user ID from the session token.

    Args:
        credentials: The HTTP Authorization header credentials.
        session: Database session.

    Returns:
        The user ID of the authenticated user.

    Raises:
        HTTPException: If authentication fails.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Query Better Auth session table to validate token
    # Better Auth stores sessions with the token as the ID
    query = text("""
        SELECT "userId" FROM "session"
        WHERE "token" = :token
        AND "expiresAt" > NOW()
    """).bindparams(token=token)

    result = session.exec(query).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return result[0]  # Return the userId


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: Session = Depends(get_session),
) -> Optional[str]:
    """Get the current user ID if authenticated, otherwise None.

    Args:
        credentials: The HTTP Authorization header credentials.
        session: Database session.

    Returns:
        The user ID if authenticated, None otherwise.
    """
    if not credentials:
        return None

    token = credentials.credentials

    query = text("""
        SELECT "userId" FROM "session"
        WHERE "token" = :token
        AND "expiresAt" > NOW()
    """).bindparams(token=token)

    result = session.exec(query).first()

    if not result:
        return None

    return result[0]
