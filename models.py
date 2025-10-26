from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text
from sqlalchemy.sql import func
from database import Base, engine

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    gender = Column(String, nullable=True)
    tin_number = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    national_id = Column(String, nullable=True)

class Identity(Base):
    __tablename__ = "identities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String)
    national_id = Column(String, unique=True)   
    date_of_birth = Column(String)   
    gender = Column(String)  
    place_of_birth = Column(String)   
    father_name = Column(String)   
    mother_name = Column(String)   
    nid_issue_date = Column(String)   
    nid_expiry_date = Column(String)    
    nid_status = Column(String, default='active')  
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True), server_default=func.now())
    risk_score = Column(Float, default=0.0)
    country_code = Column(String, default='ET')   

class FraudLog(Base):
    __tablename__ = "fraud_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    event_type = Column(String)  # e.g., "transaction", "login"
    amount = Column(Float, nullable=True)
    ip_address = Column(String)
    is_fraud = Column(Boolean, default=False)
    reason = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Rule(Base):
    __tablename__ = "rules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)                 # e.g., "Active Loan Check"
    description = Column(Text)
    condition_type = Column(String)   # e.g., "active_loan", "duplicate_phone", "rapid_reapply", etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Blacklist(Base):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True, index=True)
    national_id = Column(String, unique=True)
    reason = Column(String)

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    loan_amount = Column(Float, nullable=False)
    loan_purpose = Column(String)
    interest_rate = Column(Float)
    loan_term_months = Column(Integer)
    status = Column(String, default='pending')  # pending, approved, active, closed, rejected
    application_date = Column(DateTime(timezone=True), server_default=func.now())
    approval_date = Column(DateTime(timezone=True), nullable=True)
    disbursement_date = Column(DateTime(timezone=True), nullable=True)
    closure_date = Column(DateTime(timezone=True), nullable=True)
    monthly_payment = Column(Float)
    remaining_balance = Column(Float)
    is_active = Column(Boolean, default=False)
    rejection_reason = Column(String, nullable=True)

class LoanApplication(Base):
    __tablename__ = "loan_applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    loan_id = Column(Integer, nullable=True)  # Links to loan if approved
    application_amount = Column(Float, nullable=False)
    loan_purpose = Column(String)
    employment_status = Column(String)
    monthly_income = Column(Float)
    application_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default='pending')  # pending, approved, rejected
    rejection_reason = Column(String, nullable=True)
    ip_address = Column(String)
    user_agent = Column(String)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    fraud_log_id = Column(Integer, index=True)  # Links to FraudLog
    user_id = Column(Integer, index=True)
    alert_type = Column(String)  # transaction_fraud, identity_fraud, etc.
    severity = Column(String, default='medium')  # low, medium, high, critical
    status = Column(String, default='open')  # open, assigned, investigating, resolved, closed
    assigned_to = Column(Integer, nullable=True)  # User ID of assigned analyst
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    description = Column(Text)
    fraud_reason = Column(Text)
    risk_score = Column(Float)

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, index=True)  # Links to Alert
    case_number = Column(String, unique=True, index=True)  # Auto-generated case number
    title = Column(String)
    description = Column(Text)
    status = Column(String, default='open')  # open, investigating, resolved, closed
    priority = Column(String, default='medium')  # low, medium, high, urgent
    assigned_to = Column(Integer, nullable=True)  # User ID of assigned analyst
    created_by = Column(Integer)  # User ID of creator (super admin)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

class CaseFollowUp(Base):
    __tablename__ = "case_followups"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, index=True)  # Links to Case
    created_by = Column(Integer)  # User ID of creator
    follow_up_type = Column(String)  # investigation, communication, resolution, etc.
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserRole(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    role = Column(String)  # super_admin, fraud_analyst
    created_at = Column(DateTime(timezone=True), server_default=func.now())

Base.metadata.create_all(bind=engine)