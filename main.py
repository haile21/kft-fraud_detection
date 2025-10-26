from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import traceback

from database import engine, SessionLocal
from models import Base, Rule
from routers.nid_router import router as nid_router
from routers.identity_router import router as identity_router
from routers.transaction_router import router as transaction_router
from routers.rules_router import router as rules_router
from routers.loan_router import router as loan_router
from routers.alert_router import router as alert_router
from routers.case_router import router as case_router
from routers.user_router import router as user_router
from routers.ml_router import router as ml_router
from seed_data import seed_dummy_data
from fastapi.logger import logger



# Create tables 
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
    - **Alert System** - Automatic fraud alerts for detected activities
    - **Case Management** - Fraud case tracking and management system
    - **User Management** - JWT-based authentication and role management
    - **AI Fraud Detection** - Machine learning-based fraud detection with anomaly scoring
    
    ###  Available Endpoints:
    - **NID** (`/nid/`) - National ID verification and validation
    - **Identity** (`/identity/`) - User identity management
    - **Transaction** (`/transaction/`) - Fraud detection for transactions
    - **Rules** (`/rules/`) - Fraud detection rule management
    - **Loans** (`/loans/`) - Loan application and management
    - **Alerts** (`/alerts/`) - Fraud alert management
    - **Cases** (`/cases/`) - Fraud case management
    - **Users** (`/users/`) - User and role management
    - **ML** (`/ml/`) - AI-based fraud detection
    
    ###  Getting Started:
    1. **API Documentation**: Visit `/docs` for interactive API documentation
    2. **Authentication**: Use `/users/register` and `/users/login` for JWT authentication
    3. **Fraud Detection**: Use `/transaction/` for real-time fraud detection
    4. **Alert Management**: Use `/alerts/` to manage fraud alerts
    5. **Case Management**: Use `/cases/` to create and track fraud cases
    6. **User Management**: Use `/users/` to manage users and roles
    
    ###  For Frontend Developers:
    - **Complete API**: All functionality exposed through RESTful endpoints
    - **JWT Authentication**: Secure token-based authentication
    - **Role-based Access**: Different permissions for Super Admin and Fraud Analysts
    - **Real-time Data**: Live endpoints for dashboards and management interfaces
    
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
    lifespan=lifespan
)

# Configure OpenAPI security schemes
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

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
app.include_router(alert_router)
app.include_router(case_router)
app.include_router(user_router)
app.include_router(ml_router)

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
            "alerts": "/alerts/",
            "cases": "/cases/",
            "users": "/users/",
            "ml": "/ml/",
            "docs": "/docs"
        }
    }

# add logging middleware(Log all requests)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response