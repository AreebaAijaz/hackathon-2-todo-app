"""Authentication dependencies for FastAPI routes."""

import logging
import os
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select, text

from database import get_session

logger = logging.getLogger("auth")

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)

# Trusted internal Dapr app IDs for service-to-service calls
TRUSTED_DAPR_APP_IDS = {"recurring-service", "notification-service", "audit-service"}

# Internal service user ID used for service-to-service task creation
INTERNAL_SERVICE_USER_ID = os.getenv("INTERNAL_SERVICE_USER_ID", "")


async def get_current_user(
    request: Request,
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
    # Check for trusted Dapr service invocation (internal service-to-service calls)
    # Dapr may forward the caller app ID under different header names
    dapr_app_id = request.headers.get("dapr-app-id", "") or request.headers.get("dapr-caller-app-id", "")
    if dapr_app_id in TRUSTED_DAPR_APP_IDS and INTERNAL_SERVICE_USER_ID:
        return INTERNAL_SERVICE_USER_ID

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
