
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
