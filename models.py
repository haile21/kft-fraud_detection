from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, engine, Text
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    gender = Column(String)
    tin_number = Column(String)
    phone_number = Column(String)
    national_id = Column(String)

class Identity(Base):
    __tablename__ = "identities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String)
    national_id = Column(String, unique=True)  # Simplified KYC
    is_verified = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)

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
    condition_type = Column(String, nullable=False)       # e.g., "active_loan", "duplicate_phone", "rapid_reapply", etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Blacklist(Base):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True, index=True)
    national_id = Column(String, unique=True)
    reason = Column(String)

Base.metadata.create_all(bind=engine)