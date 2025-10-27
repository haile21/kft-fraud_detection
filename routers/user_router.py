
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from database import SessionLocal
from schemas import UserCreate, UserResponse, UserLogin, Token, UserRoleCreate, UserRoleResponse
from services.user_service import user_service, SECRET_KEY, ALGORITHM

# Create router
router = APIRouter(prefix="/users", tags=["Users"])

# Security scheme
security = HTTPBearer()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication dependency - extracts user ID from JWT token
def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> int:
    """Extract user ID from JWT token"""
    from jose import jwt
    from jose.exceptions import JWTError
    
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify user exists
        user = user_service.get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_id
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Authentication dependency - extracts user ID and roles from JWT token
def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Extract user ID and roles from JWT token"""
    from jose import jwt
    from jose.exceptions import JWTError
    
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        roles: list = payload.get("roles", [])
        username: str = payload.get("username")
        email: str = payload.get("email")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify user exists
        user = user_service.get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": user_id,
            "roles": roles,
            "username": username,
            "email": email
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Role-based authentication dependencies
def require_role(required_role: str):
    """Create a dependency that requires a specific role"""
    def role_checker(user_info: dict = Depends(get_current_user_info)):
        if required_role not in user_info["roles"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return user_info
    return role_checker

def require_super_admin(user_info: dict = Depends(get_current_user_info)):
    """Require super admin role"""
    if "super_admin" not in user_info["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Super admin role required"
        )
    return user_info

def require_fraud_analyst(user_info: dict = Depends(get_current_user_info)):
    """Require fraud analyst role"""
    if "fraud_analyst" not in user_info["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Fraud analyst role required"
        )
    return user_info

@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        user = user_service.create_user(db, user_data)
        return user
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        print(f"Error in register_user: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user and return JWT token with role information"""
    user = user_service.authenticate_user(
        db, user_credentials.username, user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user roles
    user_roles = user_service.get_user_role_names(db, user.id)
    
    access_token_expires = timedelta(minutes=30)
    access_token = user_service.create_access_token(
        data={
            "sub": user.username, 
            "user_id": user.id,
            "roles": user_roles,
            "username": user.username,
            "email": user.email
        }, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's information",
    responses={401: {"description": "Not authenticated"}}
)
def get_current_user(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get current user information"""
    user = user_service.get_user_by_id(db, current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get(
    "/me/info",
    summary="Get current user info with roles",
    description="Get the currently authenticated user's information including roles",
    responses={401: {"description": "Not authenticated"}}
)
def get_current_user_with_roles(
    user_info: dict = Depends(get_current_user_info)
):
    """Get current user information including roles"""
    return {
        "user_id": user_info["user_id"],
        "username": user_info["username"],
        "email": user_info["email"],
        "roles": user_info["roles"]
    }

@router.get("", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    user_info: dict = Depends(require_super_admin)
):
    """Get all users (Super Admin only)"""
    users = user_service.get_all_users(db)
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get user by ID"""
    # Users can only view their own profile unless they're super admin
    if not user_service.is_super_admin(db, current_user_id) and current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/{user_id}/roles", response_model=UserRoleResponse)
def assign_role(
    user_id: int,
    role_data: UserRoleCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Assign a role to a user (Super Admin only)"""
    if not user_service.is_super_admin(db, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can assign roles"
        )
    
    try:
        user_role = user_service.assign_role(db, user_id, role_data.role)
        return user_role
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{user_id}/roles", response_model=List[UserRoleResponse])
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get all roles for a user"""
    # Users can only view their own roles unless they're super admin
    if not user_service.is_super_admin(db, current_user_id) and current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    roles = user_service.get_user_roles(db, user_id)
    return roles

@router.get("/analysts/list", response_model=List[UserResponse])
def get_fraud_analysts(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get all fraud analysts (Super Admin only)"""
    if not user_service.is_super_admin(db, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can view fraud analysts"
        )
    
    analysts = user_service.get_fraud_analysts(db)
    return analysts
