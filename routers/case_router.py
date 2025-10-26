# routers/case_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import SessionLocal
from schemas import CaseResponse, CaseCreate, CaseUpdate, CaseFollowUpCreate, CaseFollowUpResponse
from services.case_service import case_service
from services.user_service import user_service

# Create router
router = APIRouter(prefix="/cases", tags=["Cases"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication dependency (simplified for now)
def get_current_user_id() -> int:
    # In a real implementation, this would extract user ID from JWT token
    # For now, return a default user ID
    return 1

@router.get("", response_model=List[CaseResponse])
def get_cases(
    status: Optional[str] = None,
    assigned_to: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get all cases with optional filtering
    
    **Super Admin**: Can see all cases
    **Fraud Analyst**: Can only see cases assigned to them
    """
    # Check user permissions
    if not user_service.is_super_admin(db, current_user_id):
        if not user_service.is_fraud_analyst(db, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        # Fraud analysts can only see their assigned cases
        assigned_to = current_user_id
    
    cases = case_service.get_cases(db, status=status, assigned_to=assigned_to)
    return cases

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get a specific case by ID"""
    case = case_service.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check permissions
    if not user_service.is_super_admin(db, current_user_id):
        if not user_service.is_fraud_analyst(db, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        # Fraud analysts can only see their assigned cases
        if case.assigned_to != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return case

@router.get("/number/{case_number}", response_model=CaseResponse)
def get_case_by_number(
    case_number: str,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get a specific case by case number"""
    case = case_service.get_case_by_number(db, case_number)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check permissions
    if not user_service.is_super_admin(db, current_user_id):
        if not user_service.is_fraud_analyst(db, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        # Fraud analysts can only see their assigned cases
        if case.assigned_to != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return case

@router.post("", response_model=CaseResponse)
def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Create a new case from an alert (Super Admin only)"""
    if not user_service.is_super_admin(db, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can create cases"
        )
    
    try:
        case = case_service.create_case_from_alert(
            db, case_data.alert_id, current_user_id, case_data
        )
        return case
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: int,
    case_update: CaseUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Update a case"""
    # Check permissions
    if not user_service.is_super_admin(db, current_user_id):
        if not user_service.is_fraud_analyst(db, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    case = case_service.update_case(db, case_id, case_update)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    return case

@router.post("/{case_id}/assign/{analyst_id}")
def assign_case(
    case_id: int,
    analyst_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Assign a case to a fraud analyst (Super Admin only)"""
    if not user_service.is_super_admin(db, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can assign cases"
        )
    
    # Check if analyst exists and has fraud_analyst role
    if not user_service.is_fraud_analyst(db, analyst_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a fraud analyst"
        )
    
    case = case_service.assign_case(db, case_id, analyst_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    return {"message": "Case assigned successfully", "case": case}

@router.post("/{case_id}/close")
def close_case(
    case_id: int,
    resolution_notes: str,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Close a case"""
    # Check permissions
    if not user_service.is_super_admin(db, current_user_id):
        if not user_service.is_fraud_analyst(db, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    case = case_service.close_case(db, case_id, resolution_notes)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    return {"message": "Case closed successfully", "case": case}

@router.post("/{case_id}/follow-ups", response_model=CaseFollowUpResponse)
def add_follow_up(
    case_id: int,
    follow_up_data: CaseFollowUpCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Add a follow-up to a case"""
    # Check permissions
    if not user_service.is_super_admin(db, current_user_id):
        if not user_service.is_fraud_analyst(db, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    try:
        follow_up = case_service.add_follow_up(
            db, case_id, current_user_id, follow_up_data
        )
        return follow_up
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{case_id}/follow-ups", response_model=List[CaseFollowUpResponse])
def get_case_follow_ups(
    case_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get all follow-ups for a case"""
    # Check permissions
    if not user_service.is_super_admin(db, current_user_id):
        if not user_service.is_fraud_analyst(db, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    follow_ups = case_service.get_case_follow_ups(db, case_id)
    return follow_ups

@router.get("/dashboard/statistics")
def get_case_statistics(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get case statistics for dashboard (Super Admin only)"""
    if not user_service.is_super_admin(db, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can view statistics"
        )
    
    stats = case_service.get_case_statistics(db)
    return stats
