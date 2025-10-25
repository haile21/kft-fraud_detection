# services/fraud_orchestrator.py
from sqlalchemy.orm import Session
from .rule_engine import evaluate_rules
# from .anomaly_detector import is_anomalous  # Commented out for now
from .identity_manager import get_identity_by_national_id, is_blacklisted
from models import FraudLog

def assess_fraud_risk(db: Session, user_id: int, amount: float, ip_address: str, national_id: str):
    reasons = []

    # 1. Check identity & blacklist
    identity = get_identity_by_national_id(db, national_id)
    if not identity:
        return True, "Identity not verified", 1.0

    if is_blacklisted(db, national_id):
        return True, "National ID blacklisted", 1.0

    # 2. Apply rule engine
    # Get identity details for NID-specific checks
    identity = get_identity_by_national_id(db, national_id)
    nid_expired = False
    nid_suspended = False
    
    if identity:
        # Check if NID is expired
        if identity.nid_status == 'expired':
            nid_expired = True
        # Check if NID is suspended
        elif identity.nid_status == 'suspended':
            nid_suspended = True
    
    context = {
        "has_active_loan": False,  # ← You'll compute this from your loan system
        "is_phone_changed_with_same_name": False,
        "applied_within_24h_after_close": False,
        "matches_fraud_db": False,
        "reapply_count_today": 0,
        "tin_name_mismatch": False,
        "nid_kyc_mismatch": False,
        "nid_expired": nid_expired,
        "nid_suspended": nid_suspended,
        # Add more as needed
    }

    rule_fraud, rule_reason = evaluate_rules(db, user_id, context)
    if rule_fraud:
        reasons.append(rule_reason)

    # 3. Apply anomaly detection (commented out for now)
    # if is_anomalous(amount):
    #     reasons.append("Unusual transaction amount")

    # 4. Compute risk score (rule-based only for now)
    risk_score = 0.0
    if rule_fraud:
        risk_score = 1.0  # High risk if any rule triggers
    else:
        risk_score = 0.0  # Low risk if no rules trigger

    is_fraud = len(reasons) > 0

    # 5. Log event
    log = FraudLog(
        user_id=user_id,
        event_type="transaction",
        amount=amount,
        ip_address=ip_address,
        is_fraud=is_fraud,
        reason="; ".join(reasons) if reasons else "None"
    )
    db.add(log)
    db.commit()

    return is_fraud, "; ".join(reasons) if reasons else "Approved", risk_score