"""
Authentication service with secure password handling
"""
import bcrypt
from sqlalchemy.orm import Session
from typing import Optional
import logging
from analytics_llm.backend.auth.models import User
from analytics_llm.backend.core.security import input_validator

logger = logging.getLogger(__name__)


def hash_password(pwd: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify(pwd: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(pwd.encode('utf-8'), hashed.encode('utf-8'))


class AuthService:
    """Authentication service"""
    
    async def authenticate(
        self, 
        db: Session, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Args:
            db: Database session
            email: User email
            password: Plain password
            
        Returns:
            User object if authenticated, None otherwise
        """
        try:
            # Validate email format
            if not input_validator.validate_email(email):
                logger.warning(f"Invalid email format: {email}")
                return None
            
            # Find user
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                logger.warning(f"User not found: {email}")
                return None
            
            # Verify password
            if not hasattr(user, 'hashed_password'):
                logger.error(f"User {email} has no password set")
                return None
            
            if not verify(password, str(user.hashed_password)):
                logger.warning(f"Invalid password for user: {email}")
                return None
            
            logger.info(f"User authenticated: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def create_user(
        self,
        db: Session,
        email: str,
        password: str,
        role: str,
        tenant_id: str
    ) -> User:
        """
        Create new user
        
        Args:
            db: Database session
            email: User email
            password: Plain password
            role: User role
            tenant_id: Tenant ID
            
        Returns:
            Created user
        """
        try:
            # Validate email
            if not input_validator.validate_email(email):
                raise ValueError("Invalid email format")
            
            # Validate password strength
            password_check = input_validator.validate_password_strength(password)
            if not password_check["valid"]:
                raise ValueError(f"Weak password: {', '.join(password_check['errors'])}")
            
            # Check if user exists
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                raise ValueError("User already exists")
            
            # Create user
            user = User(
                email=email,
                hashed_password=hash_password(password),
                role=role,
                tenant_id=tenant_id
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"User created: {email}")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"User creation error: {e}")
            raise
    
    async def change_password(
        self,
        db: Session,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Verify old password
            if not verify(old_password, str(user.hashed_password)):
                logger.warning(f"Invalid old password for user: {user.email}")
                return False
            
            # Validate new password
            password_check = input_validator.validate_password_strength(new_password)
            if not password_check["valid"]:
                raise ValueError(f"Weak password: {', '.join(password_check['errors'])}")
            
            # Update password
            user.hashed_password = str(hash_password(new_password))  # type: ignore[assignment]
            db.commit()
            
            logger.info(f"Password changed for user: {user.email}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Password change error: {e}")
            return False
