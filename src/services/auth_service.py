"""Authentication service for user login and JWT token management"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.models.user import User, UserRole


class AuthService:
    """Service for authentication and JWT token management"""
    
    # Password hashing configuration
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # JWT configuration
    SECRET_KEY = "your-secret-key-change-in-production"  # Should be from config
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    def __init__(self, secret_key: Optional[str] = None, token_expire_minutes: int = 30, user_repository=None):
        """Initialize auth service with optional custom configuration"""
        if secret_key:
            self.SECRET_KEY = secret_key
        self.ACCESS_TOKEN_EXPIRE_MINUTES = token_expire_minutes
        self.user_repository = user_repository
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password using bcrypt"""
        # Truncate password to bcrypt's 72-byte limit
        if len(password.encode('utf-8')) > 72:
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return self.pwd_context.hash(password)
    
    def create_access_token(
        self,
        username: str,
        role: UserRole,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            username: Username to encode in token
            role: User role to encode in token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = {
            "sub": username,
            "role": role.value
        }
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[dict]:
        """
        Decode and validate a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def authenticate_user(
        self,
        username: str,
        password: str,
        user_db: dict[str, User]
    ) -> Optional[User]:
        """
        Authenticate a user with username and password
        
        Args:
            username: Username to authenticate
            password: Plain text password
            user_db: Dictionary of users (username -> User)
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = user_db.get(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if user.disabled:
            return None
        return user
