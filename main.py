from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import engine, SessionLocal
from models import Base, Rule
from schemas import (
    TransactionRequest,
    FraudResponse,
    IdentityCreate,
    RuleCreate,
    RuleUpdate,
    RuleResponse,
)
from services.fraud_orchestrator import assess_fraud_risk
from services.identity_manager import create_identity, dedup_identity


# Create tables (DEV ONLY – use Alembic in production)
Base.metadata.create_all(bind=engine)

# Initial rules data
INITIAL_RULES = [
    {"name": "Active Loan Check", "description": "Fraud if applicant has active loan", "condition_type": "active_loan"},
    {"name": "Varying Phone with Similar Name/Gender", "description": "Fraud if applicant uses different phone but similar name/gender", "condition_type": "duplicate_phone"},
    {"name": "Reapply Within 24h", "description": "Fraud if applicant reapplies within 24h of closing a loan", "condition_type": "rapid_reapply"},
    {"name": "Fraud DB Match", "description": "Fraud if applicant matches known fraudster", "condition_type": "fraud_db_match"},
    {"name": "Multiple Reapplies (>2/day)", "description": "Fraud if applicant reapplies >2 times/day with altered financial data", "condition_type": "excessive_reapply"},
    {"name": "TIN Name Mismatch", "description": "Fraud if TIN is registered under different name", "condition_type": "tin_mismatch"},
    {"name": "NID KYC Mismatch", "description": "Fraud if NID was previously registered with different KYC", "condition_type": "nid_kyc_mismatch"},
]

def seed_initial_rules(db: Session):
    """Seed initial rules only if the rules table is empty."""
    existing = db.query(Rule).first()
    if not existing:
        for rule_data in INITIAL_RULES:
            db.add(Rule(**rule_data))
        db.commit()

# Lifespan manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed rules
    db = SessionLocal()
    try:
        seed_initial_rules(db)
    finally:
        db.close()
    yield
    # Shutdown: nothing to do here for now

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    #CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Identity Endpoints ---
@app.post("/identity/")
def register_identity(identity: IdentityCreate, db: Session = Depends(get_db)):
    existing = dedup_identity(db, identity.national_id)
    if existing:
        return {"message": "Identity already exists", "id": existing.id}
    new_identity = create_identity(db, identity.dict())
    return {"message": "Identity created", "id": new_identity.id}

# --- Transaction Endpoint ---
@app.post("/transaction/", response_model=FraudResponse)
def check_transaction(
    request: TransactionRequest,
    national_id: str,
    db: Session = Depends(get_db)
):
    is_fraud, reason, risk_score = assess_fraud_risk(
        db, request.user_id, request.amount, request.ip_address, national_id
    )
    if is_fraud:
        raise HTTPException(status_code=403, detail=reason)
    return {"is_fraud": False, "reason": reason, "risk_score": risk_score}

# --- Rule Management Endpoints ---
@app.post("/rules/", response_model=RuleResponse)
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    db_rule = Rule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@app.get("/rules/", response_model=List[RuleResponse])
def list_rules(db: Session = Depends(get_db)):
    return db.query(Rule).all()

@app.put("/rules/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: int, rule_update: RuleUpdate, db: Session = Depends(get_db)):
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for key, value in rule_update.dict(exclude_unset=True).items():
        setattr(db_rule, key, value)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(db_rule)
    db.commit()
    return {"message": "Rule deleted"}