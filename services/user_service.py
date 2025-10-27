# services/user_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from models import User, UserRole
from schemas import UserCreate, UserLogin

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "test-secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class UserService:
    def __init__(self):
        pass
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        if not isinstance(password, str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must be a string"
            )
        # Truncate to 72 bytes if needed (bcrypt limit)
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password = password_bytes[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(password)
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if username or email already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Hash password
        hashed_password = self.get_password_hash(user_data.password)
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            gender=user_data.gender,
            phone_number=user_data.phone_number,
            tin_number=None,
            national_id=None
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    def get_all_users(self, db: Session) -> List[User]:
        """Get all users"""
        return db.query(User).all()
    
    def assign_role(self, db: Session, user_id: int, role: str) -> UserRole:
        """Assign a role to a user"""
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if role is valid
        valid_roles = ["super_admin", "fraud_analyst"]
        if role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {valid_roles}"
            )
        
        # Check if user already has this role
        existing_role = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role == role
        ).first()
        
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has this role"
            )
        
        # Create role assignment
        user_role = UserRole(user_id=user_id, role=role)
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        return user_role
    
    def get_user_roles(self, db: Session, user_id: int) -> List[UserRole]:
        """Get all roles for a user"""
        return db.query(UserRole).filter(UserRole.user_id == user_id).all()
    
    def get_user_role_names(self, db: Session, user_id: int) -> List[str]:
        """Get user role names as a list of strings"""
        roles = self.get_user_roles(db, user_id)
        return [role.role for role in roles]
    
    def has_role(self, db: Session, user_id: int, role: str) -> bool:
        """Check if user has a specific role"""
        user_role = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role == role
        ).first()
        return user_role is not None
    
    def is_super_admin(self, db: Session, user_id: int) -> bool:
        """Check if user is super admin"""
        return self.has_role(db, user_id, "super_admin")
    
    def is_fraud_analyst(self, db: Session, user_id: int) -> bool:
        """Check if user is fraud analyst"""
        return self.has_role(db, user_id, "fraud_analyst")
    
    def get_fraud_analysts(self, db: Session) -> List[User]:
        """Get all fraud analysts"""
        analyst_user_ids = db.query(UserRole.user_id).filter(
            UserRole.role == "fraud_analyst"
        ).all()
        
        analyst_ids = [user_id[0] for user_id in analyst_user_ids]
        return db.query(User).filter(User.id.in_(analyst_ids)).all()

# Create service instance
user_service = UserService()
