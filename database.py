# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# PostgreSQL URL format: postgresql://user:password@host:port/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://fraud_user:kft_123@localhost:5432/fraud_db")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Handles stale connections
    echo=False  # Set to True for SQL debug logs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()