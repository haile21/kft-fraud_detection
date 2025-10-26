from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import SessionLocal
from schemas import AlertResponse, AlertUpdate
from services.alert_service import alert_service
from services.user_service import user_service

# Create router
router = APIRouter(prefix="/alerts", tags=["Alerts"])

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

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    status: Optional[str] = None,
    assigned_to: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get all alerts with optional filtering
    
    **Super Admin**: Can see all alerts
    **Fraud Analyst**: Can only see alerts assigned to them
    """
    # Check user permissions
    if not user_service.is_super_admin(db, current_user_id):
        if not user_service.is_fraud_analyst(db, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        # Fraud analysts can only see their assigned alerts
        assigned_to = current_user_id
    
    alerts = alert_service.get_alerts(db, status=status, assigned_to=assigned_to)
    return alerts

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get a specific alert by ID"""
    alert = alert_service.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Check permissions
    if not user_service.is_super_admin(db, current_user_id):
        if not user_service.is_fraud_analyst(db, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        # Fraud analysts can only see their assigned alerts
        if alert.assigned_to != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return alert

@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Update an alert"""
    # Check permissions
    if not user_service.is_super_admin(db, current_user_id):
        if not user_service.is_fraud_analyst(db, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    alert = alert_service.update_alert(db, alert_id, alert_update)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return alert

@router.post("/{alert_id}/assign/{analyst_id}")
def assign_alert(
    alert_id: int,
    analyst_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Assign an alert to a fraud analyst (Super Admin only)"""
    if not user_service.is_super_admin(db, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can assign alerts"
        )
    
    # Check if analyst exists and has fraud_analyst role
    if not user_service.is_fraud_analyst(db, analyst_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a fraud analyst"
        )
    
    alert = alert_service.assign_alert(db, alert_id, analyst_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return {"message": "Alert assigned successfully", "alert": alert}

@router.post("/{alert_id}/close")
def close_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Close an alert"""
    # Check permissions
    if not user_service.is_super_admin(db, current_user_id):
        if not user_service.is_fraud_analyst(db, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    alert = alert_service.close_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return {"message": "Alert closed successfully", "alert": alert}

@router.get("/dashboard/statistics")
def get_alert_statistics(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get alert statistics for dashboard (Super Admin only)"""
    if not user_service.is_super_admin(db, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can view statistics"
        )
    
    stats = alert_service.get_alert_statistics(db)
    return stats
