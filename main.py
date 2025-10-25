from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, SessionLocal
from models import Base, Rule
from routers import nid_router, identity_router, transaction_router, rules_router, loan_router
from seed_data import seed_dummy_data


# Create tables (DEV )
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
    {"name": "NID Expired", "description": "Fraud if NID has expired", "condition_type": "nid_expired"},
    {"name": "NID Suspended", "description": "Fraud if NID is suspended", "condition_type": "nid_suspended"},
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
    # Startup: seed rules and dummy data
    db = SessionLocal()
    try:
        seed_initial_rules(db)
        # Seed dummy data for development
        print("Seeding dummy data for test")
        seed_dummy_data()
    finally:
        db.close()
    yield
    # Shutdown: nothing to do here for now

# Create FastAPI app with lifespan
app = FastAPI(
    title="Fraud Management System API",
    description="""
    ## Fraud Management System
    
    A comprehensive fraud detection system that combines static rules with NID verification and TIN validation.
    
    ### Key Features:
    - **NID Verification** - National ID validation with government database simulation
    - **TIN Verification** - Real-time TIN validation with eTrade API
    - **Fraud Detection** - 9 static rules for comprehensive fraud detection
    - **Loan Management** - Complete loan application and management system
    - **Identity Management** - User identity verification and KYC
    
    ###  Available Endpoints:
    - **NID** (`/nid/`) - National ID verification and validation
    - **Identity** (`/identity/`) - User identity management
    - **Transaction** (`/transaction/`) - Fraud detection for transactions
    - **Rules** (`/rules/`) - Fraud detection rule management
    - **Loans** (`/loans/`) - Loan application and management
    
    ###  Getting Started:
    1. **Verify NID**: Use `/nid/verify/` to verify national IDs
    2. **Create Identity**: Use `/identity/` to register users
    3. **Check Transaction**: Use `/transaction/` for fraud detection
    4. **Manage Loans**: Use `/loans/` for loan operations
    
    ### Development:
    - **Swagger UI**: Available at `/docs`
    - **ReDoc**: Available at `/redoc`
    - **OpenAPI JSON**: Available at `/openapi.json`
    """,
    version="1.0.0",
    contact={
        "name": "Fraud Management Team",
        "email": "hweleslassie@kifiya.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nid_router)
app.include_router(identity_router)
app.include_router(transaction_router)
app.include_router(rules_router)
app.include_router(loan_router)

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Fraud Management System API",
        "version": "1.0.0",
        "endpoints": {
            "nid": "/nid/",
            "identity": "/identity/",
            "transaction": "/transaction/",
            "rules": "/rules/",
            "loans": "/loans/",
            "docs": "/docs"
        }
    }