"""Authentication API routes"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from src.api.models import LoginRequest, TokenResponse, UserResponse
from src.services.auth_service import AuthService
from src.repositories.user_repository import UserRepository
from src.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Initialize services (in production, use dependency injection)
auth_service = AuthService()
user_repository = UserRepository()


@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest):
    """
    Authenticate user and return JWT token
    
    Args:
        login_request: Login credentials (username and password)
        
    Returns:
        JWT access token with user information
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    # Get all users from repository
    users_db = user_repository.get_users_dict()
    
    # Authenticate user
    user = auth_service.authenticate_user(
        login_request.username,
        login_request.password,
        users_db
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = auth_service.create_access_token(
        username=user.username,
        role=user.role
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        username=user.username,
        role=user.role.value
    )


@router.get("/login")
async def login_status():
    """
    GET endpoint for login status - redirects to proper POST endpoint
    Some frontends might call GET /api/auth/login by mistake
    """
    return {
        "message": "Login requires POST method",
        "method": "POST", 
        "endpoint": "/api/auth/login",
        "body": {
            "username": "string",
            "password": "string"
        },
        "example": {
            "username": "admin",
            "password": "admin123"
        }
    }


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    OAuth2 compatible token endpoint
    
    This endpoint follows OAuth2 password flow specification
    and is compatible with FastAPI's OAuth2PasswordBearer
    
    Args:
        form_data: OAuth2 password form data
        
    Returns:
        JWT access token with user information
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    # Get all users from repository
    users_db = user_repository.get_users_dict()
    
    # Authenticate user
    user = auth_service.authenticate_user(
        form_data.username,
        form_data.password,
        users_db
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = auth_service.create_access_token(
        username=user.username,
        role=user.role
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        username=user.username,
        role=user.role.value
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Get current authenticated user information
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: 401 if token is invalid
    """
    # Decode token
    payload = auth_service.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from repository
    user = user_repository.get_user(username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserResponse(
        username=user.username,
        role=user.role.value,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled
    )


def get_current_active_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Dependency to get current authenticated and active user
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: 401 if token is invalid or user is disabled
    """
    # Decode token
    payload = auth_service.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from repository
    user = user_repository.get_user(username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/logout")
async def logout():
    """
    Logout endpoint
    
    Since JWT tokens are stateless, logout is handled client-side
    by removing the token from storage. This endpoint can be used
    for logging purposes or future token blacklisting.
    
    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}


def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> User:
    """
    Optional dependency to get current user (returns None if not authenticated)
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        Current user or None if not authenticated
    """
    try:
        return get_current_active_user(token)
    except HTTPException:
        return None
