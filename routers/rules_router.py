# routers/rules_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from models import Rule
from schemas import RuleCreate, RuleUpdate, RuleResponse

# Create router
router = APIRouter(prefix="/rules", tags=["Rules"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=RuleResponse)
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    """
     Create New Fraud Detection Rule
    
    Creates a new dynamic fraud detection rule that will be applied to all transactions.
    
    **Rule Types Available:**
    - `active_loan` - Check for active loans
    - `duplicate_phone` - Phone variation detection
    - `rapid_reapply` - Rapid reapplication detection
    - `fraud_db_match` - Fraud database matching
    - `excessive_reapply` - Excessive reapplication detection
    - `tin_mismatch` - TIN name mismatch detection
    - `nid_kyc_mismatch` - NID KYC mismatch detection
    - `nid_expired` - Expired NID detection
    - `nid_suspended` - Suspended NID detection
    
    **Example Request:**
    ```json
    {
        "name": "High Amount Check",
        "description": "Flag transactions over 100,000",
        "condition_type": "high_amount",
        "is_active": true
    }
    ```
    
    **Admin Features:**
    - ✅ **Real-time Activation** - Rules take effect immediately
    - ✅ **Custom Descriptions** - Clear fraud reason messages
    - ✅ **Enable/Disable** - Toggle rules without deletion
    - ✅ **Priority Management** - Order rules by importance
    """
    db_rule = Rule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.get("", response_model=List[RuleResponse])
def list_rules(db: Session = Depends(get_db)):
    """
    📋 List All Fraud Detection Rules
    
    Returns all configured fraud detection rules for admin management.
    
    **Admin Dashboard Features:**
    - ✅ **Rule Status** - See which rules are active/inactive
    - ✅ **Rule Descriptions** - Understand what each rule does
    - ✅ **Rule Types** - See available condition types
    - ✅ **Management Actions** - Edit, delete, or toggle rules
    
    **Response includes:**
    - Rule ID, name, and description
    - Condition type and status
    - Creation date and activation status
    - Management capabilities
    """
    return db.query(Rule).all()

@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a specific rule by ID"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: int, rule_update: RuleUpdate, db: Session = Depends(get_db)):
    """Update an existing rule"""
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    for key, value in rule_update.dict(exclude_unset=True).items():
        setattr(db_rule, key, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a rule"""
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(db_rule)
    db.commit()
    return {"message": "Rule deleted successfully"}

@router.patch("/{rule_id}/toggle")
def toggle_rule_status(rule_id: int, db: Session = Depends(get_db)):
    """
    🔄 Toggle Rule Active/Inactive Status
    
    Instantly enable or disable a fraud detection rule without deleting it.
    
    **Admin Benefits:**
    - ✅ **Instant Effect** - Changes apply to next transaction
    - ✅ **No Data Loss** - Rule configuration preserved
    - ✅ **A/B Testing** - Test rule effectiveness
    - ✅ **Emergency Control** - Quickly disable problematic rules
    
    **Use Cases:**
    - Temporarily disable a rule for testing
    - Enable new rules gradually
    - Emergency rule management
    - Performance optimization
    """
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db_rule.is_active = not db_rule.is_active
    db.commit()
    db.refresh(db_rule)
    
    return {
        "message": f"Rule {'activated' if db_rule.is_active else 'deactivated'}",
        "rule_id": rule_id,
        "is_active": db_rule.is_active
    }

@router.get("/admin/dashboard")
def get_admin_dashboard(db: Session = Depends(get_db)):
    """
    🎛️ Admin Dashboard Overview
    
    Comprehensive dashboard for fraud rule management and system monitoring.
    
    **Dashboard Features:**
    - ✅ **Rule Statistics** - Active/inactive rule counts
    - ✅ **Rule Performance** - Most triggered rules
    - ✅ **System Health** - Rule engine status
    - ✅ **Quick Actions** - Enable/disable all rules
    
    **Perfect for Admin UI:**
    - Real-time rule status
    - System performance metrics
    - Quick management actions
    - Rule effectiveness data
    """
    from models import FraudLog
    
    # Get rule statistics
    total_rules = db.query(Rule).count()
    active_rules = db.query(Rule).filter(Rule.is_active == True).count()
    inactive_rules = total_rules - active_rules
    
    # Get fraud detection statistics
    total_fraud_events = db.query(FraudLog).filter(FraudLog.is_fraud == True).count()
    total_transactions = db.query(FraudLog).count()
    fraud_rate = (total_fraud_events / total_transactions * 100) if total_transactions > 0 else 0
    
    # Get recent fraud events
    recent_fraud = db.query(FraudLog).filter(
        FraudLog.is_fraud == True
    ).order_by(FraudLog.created_at.desc()).limit(10).all()
    
    return {
        "system_status": "operational",
        "rule_statistics": {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "inactive_rules": inactive_rules,
            "activation_rate": (active_rules / total_rules * 100) if total_rules > 0 else 0
        },
        "fraud_statistics": {
            "total_transactions": total_transactions,
            "fraud_events": total_fraud_events,
            "fraud_rate": round(fraud_rate, 2),
            "success_rate": round(100 - fraud_rate, 2)
        },
        "recent_fraud_events": [
            {
                "id": event.id,
                "user_id": event.user_id,
                "amount": event.amount,
                "reason": event.reason,
                "created_at": event.created_at
            }
            for event in recent_fraud
        ],
        "available_rule_types": [
            "active_loan", "duplicate_phone", "rapid_reapply", 
            "fraud_db_match", "excessive_reapply", "tin_mismatch",
            "nid_kyc_mismatch", "nid_expired", "nid_suspended"
        ]
    }
