# routers/loan_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from schemas import (
    LoanApplicationCreate, 
    LoanApplicationResponse, 
    LoanCreate, 
    LoanResponse
)
from services.loan_service import loan_service

# Create router
router = APIRouter(prefix="/loans", tags=["Loans"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/applications", response_model=LoanApplicationResponse)
def create_loan_application(
    application: LoanApplicationCreate, 
    db: Session = Depends(get_db)
):
    """
     Create Loan Application with Comprehensive Fraud Detection
    
    Creates a new loan application with comprehensive fraud detection using the same rules as the Transaction API.
    
    **Process:**
    1.  **Fraud Check** - Automatically runs comprehensive fraud detection
    2.  **NID Verification** - Validates user identity
    3.  **TIN Verification** - Cross-checks TIN with eTrade API
    4.  **Rule Engine** - Applies 9 configurable fraud detection rules
    5.  **Application Creation** - Stores application in database (only if fraud check passes)
    
    **Fraud Detection Rules Applied:**
    1. ✅ **Active Loan Check** - Flag if user has active loan
    2. ✅ **Phone Variation** - Detect different phone with same name/gender
    3. ✅ **Rapid Reapply** - Flag reapplications within 24h
    4. ✅ **Fraud DB Match** - Check against known fraudsters
    5. ✅ **Excessive Reapply** - Flag >2 applications/day
    6. ✅ **TIN Mismatch** - Verify TIN matches registered name
    7. ✅ **NID KYC Mismatch** - Cross-verify NID with KYC data
    8. ✅ **NID Expired** - Flag expired NIDs
    9. ✅ **NID Suspended** - Flag suspended NIDs
    
    **Example Request:**
    ```json
    {
        "user_id": 1,
        "application_amount": 50000.0,
        "loan_purpose": "Business expansion",
        "employment_status": "employed",
        "monthly_income": 15000.0,
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "national_id": "123456789012"
    }
    ```
    
    **Example Response (Success):**
    ```json
    {
        "id": 1,
        "user_id": 1,
        "application_amount": 50000.0,
        "loan_purpose": "Business expansion",
        "employment_status": "employed",
        "monthly_income": 15000.0,
        "application_date": "2024-01-15T10:30:00Z",
        "status": "pending"
    }
    ```
    
    **Example Response (Fraud Detected):**
    ```json
    {
        "detail": "Loan application rejected due to fraud detection: NID expired; Active loan check"
    }
    ```
    """
    try:
        new_application = loan_service.create_loan_application(
            db=db,
            user_id=application.user_id,
            amount=application.application_amount,
            purpose=application.loan_purpose,
            employment_status=application.employment_status,
            monthly_income=application.monthly_income,
            ip_address=application.ip_address,
            user_agent=application.user_agent,
            national_id=application.national_id
        )
        return new_application
    except HTTPException as e:
        # Re-raise HTTP exceptions (fraud detection failures)
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/applications/user/{user_id}", response_model=List[LoanApplicationResponse])
def get_user_applications(user_id: int, db: Session = Depends(get_db)):
    """Get all loan applications for a user"""
    applications = db.query(loan_service.LoanApplication).filter(
        loan_service.LoanApplication.user_id == user_id
    ).all()
    return applications

@router.get("/applications/{application_id}", response_model=LoanApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    """Get a specific loan application"""
    from models import LoanApplication
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

@router.post("/applications/{application_id}/approve", response_model=LoanResponse)
def approve_application(
    application_id: int, 
    interest_rate: float, 
    loan_term_months: int,
    db: Session = Depends(get_db)
):
    """Approve a loan application"""
    try:
        loan = loan_service.approve_loan_application(
            db, application_id, interest_rate, loan_term_months
        )
        if not loan:
            raise HTTPException(status_code=404, detail="Application not found")
        return loan
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/applications/{application_id}/reject")
def reject_application(
    application_id: int, 
    reason: str,
    db: Session = Depends(get_db)
):
    """Reject a loan application"""
    try:
        loan_service.reject_loan_application(db, application_id, reason)
        return {"message": "Application rejected successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}", response_model=List[LoanResponse])
def get_user_loans(user_id: int, db: Session = Depends(get_db)):
    """Get all loans for a user"""
    from models import Loan
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    return loans

@router.get("/all", response_model=List[LoanResponse])
def get_all_loans(db: Session = Depends(get_db)):
    """Get all loans"""
    loans = loan_service.get_all_loans(db)
    return loans

@router.get("/user/{user_id}/active", response_model=List[LoanResponse])
def get_active_loans(user_id: int, db: Session = Depends(get_db)):
    """Get active loans for a user"""
    active_loans = loan_service.get_active_loans(db, user_id)
    return active_loans

@router.post("/{loan_id}/close")
def close_loan(loan_id: int, db: Session = Depends(get_db)):
    """Close a loan"""
    try:
        loan_service.close_loan(db, loan_id)
        return {"message": "Loan closed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}/applications/today")
def get_applications_today(user_id: int, db: Session = Depends(get_db)):
    """Get count of applications made today"""
    count = loan_service.get_applications_today(db, user_id)
    return {"user_id": user_id, "applications_today": count}

@router.get("/user/{user_id}/applications/recent")
def get_recent_applications(user_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Get recent applications for a user"""
    applications = loan_service.get_recent_applications(db, user_id, days)
    return {
        "user_id": user_id,
        "days": days,
        "applications": applications
    }
