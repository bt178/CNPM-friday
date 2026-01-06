"""
API Dependencies for FastAPI endpoints.
Provides database sessions, authentication, and authorization.
"""
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.all_models import User

# OAuth2 scheme for JWT token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency.
    Yields an async database session and ensures proper cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Raises:
        HTTPException: If token is invalid or user not found.
    
    Returns:
        User: The authenticated user object with role preloaded.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    
    return user


def require_role(*allowed_roles: str):
    """
    Role-based access control decorator.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            current_user: User = Depends(require_role("ADMIN"))
        ):
            ...
    
    Args:
        *allowed_roles: Role names that are allowed to access the endpoint.
    
    Returns:
        Dependency function that checks user role.
    """
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role = current_user.role.role_name.upper()
        if user_role not in [role.upper() for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )
        return current_user
    
    return role_checker


def require_lecturer(current_user: User = Depends(get_current_user)) -> User:
    """Shortcut dependency for lecturer-only endpoints."""
    if current_user.role.role_name.upper() != "LECTURER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can access this endpoint",
        )
    return current_user


def require_student(current_user: User = Depends(get_current_user)) -> User:
    """Shortcut dependency for student-only endpoints."""
    if current_user.role.role_name.upper() != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint",
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Shortcut dependency for admin-only endpoints."""
    if current_user.role.role_name.upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this endpoint",
        )
    return current_user