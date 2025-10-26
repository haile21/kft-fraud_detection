from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import HTTPException


from database import SessionLocal
from schemas import TransactionRequest, FraudResponse
from services.fraud_orchestrator import assess_fraud_risk

# Create router
router = APIRouter(prefix="/transaction", tags=["Transaction"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=FraudResponse)
def check_transaction(
    request: TransactionRequest,
    national_id: str,
    db: Session = Depends(get_db)
):
    """
    Check Transaction for Fraud
    
    Analyzes a transaction using **dynamic fraud detection rules** that can be configured by admins through the UI.
    
    **Dynamic Rule System:**
    - ✅ **Admin Configurable** - Rules can be added/modified via `/rules/` endpoints
    - ✅ **Real-time Updates** - Rule changes take effect immediately
    - ✅ **Rule Management** - Enable/disable rules without code changes
    - ✅ **Custom Rules** - Admins can create new fraud detection rules
    
    **Default Rules (Configurable):**
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
        "amount": 50000.0,
        "ip_address": "192.168.1.100"
    }
    ```
    
    **Example Response (Approved):**
    ```json
    {
        "is_fraud": false,
        "reason": "Approved",
        "risk_score": 0.0
    }
    ```
    
    **Example Response (Fraud Detected):**
    ```json
    {
        "is_fraud": true,
        "reason": "NID expired; Active loan check",
        "risk_score": 1.0
    }
    ```
    """
    is_fraud, reason, risk_score = assess_fraud_risk(
        db, request.user_id, request.amount, request.ip_address, national_id
    )
    
    if is_fraud:
        raise HTTPException(
            status_code=403, 
            detail=f"Fraud detected: {reason}"
        )
    
    return {
        "is_fraud": False, 
        "reason": reason, 
        "risk_score": risk_score
    }

@router.get("/history/{user_id}")
def get_transaction_history(user_id: int, db: Session = Depends(get_db)):
    """Get transaction history for a user"""
    from models import FraudLog
    
    transactions = db.query(FraudLog).filter(
        FraudLog.user_id == user_id
    ).order_by(FraudLog.created_at.desc()).limit(50).all()
    
    return {
        "user_id": user_id,
        "transactions": [
            {
                "id": t.id,
                "event_type": t.event_type,
                "amount": t.amount,
                "ip_address": t.ip_address,
                "is_fraud": t.is_fraud,
                "reason": t.reason,
                "created_at": t.created_at
            }
            for t in transactions
        ]
    }
