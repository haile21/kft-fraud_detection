from sqlalchemy.orm import Session
from typing import List, Tuple, Callable, Dict
from ..models import Rule


# --- Rule Evaluation Functions (Stubs) ---
# In real system, these would call other services (loan DB, NID API, etc.)

def check_active_loan(user_id: int, **kwargs) -> bool:
    # Placeholder: assume we have a loan service
    # Return True if user has active loan
    return kwargs.get("has_active_loan", False)


def check_duplicate_phone(user_id: int, **kwargs) -> bool:
    # Fuzzy match name + gender + phone variation
    # For demo: flag if phone changed but name same
    return kwargs.get("is_phone_changed_with_same_name", False)


def check_rapid_reapply(user_id: int, **kwargs) -> bool:
    return kwargs.get("applied_within_24h_after_close", False)


def check_fraud_db_match(user_id: int, **kwargs) -> bool:
    return kwargs.get("matches_fraud_db", False)


def check_excessive_reapply(user_id: int, **kwargs) -> bool:
    return kwargs.get("reapply_count_today", 0) > 2


def check_tin_mismatch(user_id: int, **kwargs) -> bool:
    return kwargs.get("tin_name_mismatch", False)


def check_nid_kyc_mismatch(user_id: int, **kwargs) -> bool:
    return kwargs.get("nid_kyc_mismatch", False)


# --- Registry ---
RULE_HANDLERS: Dict[str, Callable] = {
    "active_loan": check_active_loan,
    "duplicate_phone": check_duplicate_phone,
    "rapid_reapply": check_rapid_reapply,
    "fraud_db_match": check_fraud_db_match,
    "excessive_reapply": check_excessive_reapply,
    "tin_mismatch": check_tin_mismatch,
    "nid_kyc_mismatch": check_nid_kyc_mismatch,
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
            if handler(user_id=user_id, **context):
                triggered_reasons.append(rule.description)
        except Exception as e:
            # Log error in real system
            continue

    is_fraud = len(triggered_reasons) > 0
    reason = "; ".join(triggered_reasons) if triggered_reasons else ""
    return is_fraud, reason