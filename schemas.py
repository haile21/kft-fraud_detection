
from pydantic import BaseModel
from typing import Optional

class TransactionRequest(BaseModel):
    user_id: int
    amount: float
    ip_address: str

class IdentityCreate(BaseModel):
    user_id: int
    name: str
    national_id: str

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
