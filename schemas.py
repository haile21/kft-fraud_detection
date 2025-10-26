
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionRequest(BaseModel):
    user_id: int
    amount: float
    ip_address: str
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "amount": 50000.0,
                "ip_address": "192.168.1.100"
            }
        }

class IdentityCreate(BaseModel):
    user_id: int
    name: str
    national_id: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    place_of_birth: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    country_code: str = 'ET'

class NIDVerificationRequest(BaseModel):
    national_id: str
    name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    country_code: str = 'ET'
    
    class Config:
        schema_extra = {
            "example": {
                "national_id": "123456789012",
                "name": "Alemayehu Tsegaye",
                "date_of_birth": "1985-03-15",
                "gender": "M",
                "country_code": "ET"
            }
        }

class NIDVerificationResponse(BaseModel):
    is_valid: bool
    message: str
    nid_details: Optional[dict] = None
    verification_status: str  # verified, failed, expired, blacklisted

class FraudResponse(BaseModel):
    is_fraud: bool
    reason: str
    risk_score: Optional[float] = None

class RuleBase(BaseModel):
    name: str
    description: str
    condition_type: str  # Must be one of predefined types
    is_active: bool = True

class RuleCreate(RuleBase):
    pass

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition_type: Optional[str] = None
    is_active: Optional[bool] = None

class RuleResponse(RuleBase):
    id: int

# Loan-related schemas
class LoanApplicationCreate(BaseModel):
    user_id: int
    application_amount: float
    loan_purpose: Optional[str] = None
    employment_status: Optional[str] = None
    monthly_income: Optional[float] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "application_amount": 50000.0,
                "loan_purpose": "Business expansion",
                "employment_status": "employed",
                "monthly_income": 15000.0,
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        }

class LoanApplicationResponse(BaseModel):
    id: int
    user_id: int
    loan_id: Optional[int] = None
    application_amount: float
    loan_purpose: Optional[str] = None
    employment_status: Optional[str] = None
    monthly_income: Optional[float] = None
    application_date: datetime
    status: str
    rejection_reason: Optional[str] = None

class LoanCreate(BaseModel):
    user_id: int
    loan_amount: float
    loan_purpose: Optional[str] = None
    interest_rate: float
    loan_term_months: int

class LoanResponse(BaseModel):
    id: int
    user_id: int
    loan_amount: float
    loan_purpose: Optional[str] = None
    interest_rate: float
    loan_term_months: int
    status: str
    application_date: datetime
    approval_date: Optional[datetime] = None
    disbursement_date: Optional[datetime] = None
    closure_date: Optional[datetime] = None
    monthly_payment: Optional[float] = None
    remaining_balance: Optional[float] = None
    is_active: bool
    rejection_reason: Optional[str] = None

# Alert and Case Management Schemas
class AlertResponse(BaseModel):
    id: int
    fraud_log_id: int
    user_id: int
    alert_type: str
    severity: str
    status: str
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = None
    fraud_reason: Optional[str] = None
    risk_score: Optional[float] = None

class AlertCreate(BaseModel):
    fraud_log_id: int
    user_id: int
    alert_type: str
    severity: str = 'medium'
    description: Optional[str] = None
    fraud_reason: Optional[str] = None
    risk_score: Optional[float] = None

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    description: Optional[str] = None

class CaseResponse(BaseModel):
    id: int
    alert_id: int
    case_number: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assigned_to: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

class CaseCreate(BaseModel):
    alert_id: int
    title: str
    description: Optional[str] = None
    priority: str = 'medium'
    assigned_to: Optional[int] = None

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    resolution_notes: Optional[str] = None

class CaseFollowUpCreate(BaseModel):
    case_id: int
    follow_up_type: str
    notes: str

class CaseFollowUpResponse(BaseModel):
    id: int
    case_id: int
    created_by: int
    follow_up_type: str
    notes: str
    created_at: datetime

# User and Authentication Schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    gender: Optional[str] = None
    phone_number: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    national_id: Optional[str] = None
    tin_number: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserRoleCreate(BaseModel):
    user_id: int
    role: str  # super_admin, fraud_analyst

class UserRoleResponse(BaseModel):
    id: int
    user_id: int
    role: str
    created_at: datetime

# ML Fraud Detection Schemas
class TransactionInput(BaseModel):
    V: list[float]  # 28 V features
    Time: float
    Amount: float

class MLPredictionResponse(BaseModel):
    is_fraud: bool
    is_anomaly: bool
    anomaly_score: float
    risk_level: str
    explanation: str
    confidence: str
    transaction_index: int

class FraudDecisionResponse(BaseModel):
    decision: str  # "allow", "block", or "review"
    fraud_risk: str  # "Low", "Medium", "High", "Critical"
    anomaly_score: float
    explanation: str
    recommendation: str