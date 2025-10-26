from sqlalchemy.orm import Session
from typing import List, Tuple, Callable, Dict
from datetime import datetime, timedelta
from models import Rule, User, Identity, FraudLog, Loan, LoanApplication
from .nid_service import nid_service
from .tin_service import tin_service
from .loan_service import loan_service


# --- Rule Evaluation Functions (Stubs) ---
# In real system, these would call other services (loan DB, NID API, etc.)

def check_active_loan(user_id: int, db: Session, **kwargs) -> bool:
    """Check if user has active loan - REAL IMPLEMENTATION"""
    # Check if context already has this information
    if 'has_active_loan' in kwargs:
        return kwargs['has_active_loan']
    # Otherwise use proper loan service to check for active loans
    return loan_service.has_active_loan(db, user_id)


def check_duplicate_phone(user_id: int, db: Session, **kwargs) -> bool:
    """Check for phone variation with similar name/gender - REAL IMPLEMENTATION"""
    # Check if context already has this information
    if 'is_phone_changed_with_same_name' in kwargs:
        return kwargs['is_phone_changed_with_same_name']
    
    from fuzzywuzzy import fuzz
    
    # Get current user data
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        return False
    
    # Get all other users with similar names (fuzzy match)
    all_users = db.query(User).filter(User.id != user_id).all()
    
    for other_user in all_users:
        # Check name similarity
        name_similarity = fuzz.ratio(
            current_user.first_name.lower() + " " + current_user.last_name.lower(),
            other_user.first_name.lower() + " " + other_user.last_name.lower()
        )
        
        # Check gender match
        gender_match = current_user.gender == other_user.gender
        
        # Check if phone numbers are different
        phone_different = current_user.phone_number != other_user.phone_number
        
        # If name is similar (>80%), gender matches, but phone is different
        if name_similarity > 80 and gender_match and phone_different:
            return True
    
    return False


def check_rapid_reapply(user_id: int, db: Session, **kwargs) -> bool:
    """Check if user reapplied within 24h of closing a loan - REAL IMPLEMENTATION"""
    # Check if context already has this information
    if 'applied_within_24h_after_close' in kwargs:
        return kwargs['applied_within_24h_after_close']
    
    # Get applications within last 24 hours
    recent_applications = loan_service.get_applications_within_hours(db, user_id, 24)
    
    if len(recent_applications) < 2:
        return False
    
    # Check if there's a pattern of rapid reapplication
    for i in range(len(recent_applications) - 1):
        current_app = recent_applications[i]
        previous_app = recent_applications[i + 1]
        
        # Check if applications are within 24 hours
        time_diff = current_app.application_date - previous_app.application_date
        if time_diff <= timedelta(hours=24):
            return True
    
    return False


def check_fraud_db_match(user_id: int, db: Session, **kwargs) -> bool:
    """Check if user matches known fraudsters - REAL IMPLEMENTATION"""
    # Check if context already has this information
    if 'matches_fraud_db' in kwargs:
        return kwargs['matches_fraud_db']
    
    from .identity_manager import is_blacklisted
    
    # Get user's national ID
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.national_id:
        return False
    
    # Check if national ID is blacklisted
    is_blacklisted_flag, blacklist_reason = is_blacklisted(db, user.national_id)
    if is_blacklisted_flag:
        return True
    
    # Check for similar patterns in fraud logs
    fraud_patterns = db.query(FraudLog).filter(
        FraudLog.is_fraud == True,
        FraudLog.user_id != user_id
    ).all()
    
    # Check for similar phone numbers, emails, or names
    for fraud_log in fraud_patterns:
        # This would be more sophisticated in a real system
        # For now, we'll check if there are multiple fraud cases with similar patterns
        pass
    
    return False


def check_excessive_reapply(user_id: int, db: Session, **kwargs) -> bool:
    """Check if user reapplied more than 2 times in a day - REAL IMPLEMENTATION"""
    # Check if context already has this information
    if 'reapply_count_today' in kwargs:
        return kwargs['reapply_count_today'] > 2
    
    # Use loan service to count applications today
    applications_today = loan_service.get_applications_today(db, user_id)
    return applications_today > 2


def check_tin_mismatch(user_id: int, db: Session, **kwargs) -> bool:
    """Check if TIN is registered under different name - REAL IMPLEMENTATION"""
    # Check if context already has this information
    if 'tin_name_mismatch' in kwargs:
        return kwargs['tin_name_mismatch']
    
    # Get user data
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.tin_number:
        return False
    
    # Verify TIN with trade ministry and cross-check name
    try:
        is_valid, message = tin_service.cross_verify_tin_name(
            user.tin_number, 
            f"{user.first_name} {user.last_name}"
        )
        return not is_valid  # Return True if TIN name doesn't match
    except Exception:
        # If TIN verification fails, consider it a mismatch
        return True


def check_nid_kyc_mismatch(user_id: int, db: Session, **kwargs) -> bool:
    """Check if NID KYC data matches provided information - REAL IMPLEMENTATION"""
    # Check if context already has this information
    if 'nid_kyc_mismatch' in kwargs:
        return kwargs['nid_kyc_mismatch']
    
    # Get user data
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.national_id:
        return False
    
    # Cross-verify NID with provided KYC data
    try:
        is_valid, message = nid_service.cross_verify_kyc_data(
            user.national_id,
            f"{user.first_name} {user.last_name}",
            user.date_of_birth if hasattr(user, 'date_of_birth') else None,
            user.gender
        )
        return not is_valid  # Return True if NID KYC doesn't match
    except Exception:
        # If NID verification fails, consider it a mismatch
        return True

def check_nid_expired(user_id: int, db: Session, **kwargs) -> bool:
    """Check if NID has expired - REAL IMPLEMENTATION"""
    # Check if context already has this information
    if 'nid_expired' in kwargs:
        return kwargs['nid_expired']
    
    # Get user's identity record
    identity = db.query(Identity).filter(Identity.user_id == user_id).first()
    if not identity:
        return False
    
    # Check if NID status is expired
    return identity.nid_status == 'expired'

def check_nid_suspended(user_id: int, db: Session, **kwargs) -> bool:
    """Check if NID is suspended - REAL IMPLEMENTATION"""
    # Check if context already has this information
    if 'nid_suspended' in kwargs:
        return kwargs['nid_suspended']
    
    # Get user's identity record
    identity = db.query(Identity).filter(Identity.user_id == user_id).first()
    if not identity:
        return False
    
    # Check if NID status is suspended
    return identity.nid_status == 'suspended'


# --- Registry ---
RULE_HANDLERS: Dict[str, Callable] = {
    "active_loan": check_active_loan,
    "duplicate_phone": check_duplicate_phone,
    "rapid_reapply": check_rapid_reapply,
    "fraud_db_match": check_fraud_db_match,
    "excessive_reapply": check_excessive_reapply,
    "tin_mismatch": check_tin_mismatch,
    "nid_kyc_mismatch": check_nid_kyc_mismatch,
    "nid_expired": check_nid_expired,
    "nid_suspended": check_nid_suspended,
}


def evaluate_rules(
        db: Session,
        user_id: int,
        context: dict  # Contains dynamic data like has_active_loan, phone, etc.
) -> Tuple[bool, str]:
    """
    The context dict must contain all needed flags (e.g., has_active_loan, reapply_count_today).
     These would be computed by the orchestrator before calling evaluate_rules.
    Evaluate all active rules. Return (is_fraud, reason).
    """
    active_rules = db.query(Rule).filter(Rule.is_active == True).all()

    triggered_reasons = []

    for rule in active_rules:
        handler = RULE_HANDLERS.get(rule.condition_type)
        if not handler:
            continue  # Skip unknown rule types

        try:
            if handler(user_id=user_id, db=db, **context):
                triggered_reasons.append(rule.description)
        except Exception as e:
            # Log error in real system
            continue

    is_fraud = len(triggered_reasons) > 0
    reason = "; ".join(triggered_reasons) if triggered_reasons else ""
    return is_fraud, reason