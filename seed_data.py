# seed_data.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from database import SessionLocal
from models import User, Identity, Loan, LoanApplication, Blacklist, Rule

def seed_dummy_data():
    """Seed database with dummy data for testing"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Data already exists, skipping seed...")
            return
        
        print("Seeding dummy data...")
        
        # Create dummy users
        users = [
            User(
                username="john_doe",
                email="john.doe@email.com",
                password="hashed_password_1",
                first_name="John",
                last_name="Doe",
                gender="M",
                tin_number="1234567890",
                phone_number="+251911234567",
                national_id="123456789012"
            ),
            User(
                username="jane_smith",
                email="jane.smith@email.com",
                password="hashed_password_2",
                first_name="Jane",
                last_name="Smith",
                gender="F",
                tin_number="2345678901",
                phone_number="+251922345678",
                national_id="234567890123"
            ),
            User(
                username="mike_wilson",
                email="mike.wilson@email.com",
                password="hashed_password_3",
                first_name="Mike",
                last_name="Wilson",
                gender="M",
                tin_number="3456789012",
                phone_number="+251933456789",
                national_id="345678901234"
            ),
            User(
                username="sarah_jones",
                email="sarah.jones@email.com",
                password="hashed_password_4",
                first_name="Sarah",
                last_name="Jones",
                gender="F",
                tin_number="4567890123",
                phone_number="+251944567890",
                national_id="456789012345"
            ),
            User(
                username="fraud_user",
                email="fraud@email.com",
                password="hashed_password_5",
                first_name="Fraud",
                last_name="User",
                gender="M",
                tin_number="9999999999",
                phone_number="+251999999999",
                national_id="999999999999"
            )
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        
        # Create identities for users
        identities = [
            Identity(
                user_id=1,
                name="John Doe",
                national_id="123456789012",
                date_of_birth="1985-03-15",
                gender="M",
                place_of_birth="Addis Ababa",
                father_name="Robert Doe",
                mother_name="Mary Doe",
                nid_issue_date="2010-05-20",
                nid_expiry_date="2030-05-20",
                nid_status="active",
                is_verified=True,
                risk_score=0.1,
                country_code="ET"
            ),
            Identity(
                user_id=2,
                name="Jane Smith",
                national_id="234567890123",
                date_of_birth="1990-07-22",
                gender="F",
                place_of_birth="Bahir Dar",
                father_name="David Smith",
                mother_name="Lisa Smith",
                nid_issue_date="2015-08-10",
                nid_expiry_date="2035-08-10",
                nid_status="active",
                is_verified=True,
                risk_score=0.2,
                country_code="ET"
            ),
            Identity(
                user_id=3,
                name="Mike Wilson",
                national_id="345678901234",
                date_of_birth="1988-11-08",
                gender="M",
                place_of_birth="Mekelle",
                father_name="Tom Wilson",
                mother_name="Anna Wilson",
                nid_issue_date="2012-12-01",
                nid_expiry_date="2032-12-01",
                nid_status="expired",
                is_verified=True,
                risk_score=0.8,
                country_code="ET"
            ),
            Identity(
                user_id=4,
                name="Sarah Jones",
                national_id="456789012345",
                date_of_birth="1992-04-12",
                gender="F",
                place_of_birth="Hawassa",
                father_name="Paul Jones",
                mother_name="Emma Jones",
                nid_issue_date="2018-03-15",
                nid_expiry_date="2038-03-15",
                nid_status="suspended",
                is_verified=True,
                risk_score=0.9,
                country_code="ET"
            ),
            Identity(
                user_id=5,
                name="Fraud User",
                national_id="999999999999",
                date_of_birth="1980-01-01",
                gender="M",
                place_of_birth="Unknown",
                father_name="Unknown",
                mother_name="Unknown",
                nid_issue_date="2020-01-01",
                nid_expiry_date="2030-01-01",
                nid_status="active",
                is_verified=True,
                risk_score=1.0,
                country_code="ET"
            )
        ]
        
        for identity in identities:
            db.add(identity)
        db.commit()
        
        # Create blacklist entry for fraud user
        blacklist_entry = Blacklist(
            national_id="999999999999",
            reason="Known fraudster - multiple fake applications"
        )
        db.add(blacklist_entry)
        db.commit()
        
        # Create loan applications
        loan_applications = [
            LoanApplication(
                user_id=1,
                application_amount=50000.0,
                loan_purpose="Business expansion",
                employment_status="employed",
                monthly_income=15000.0,
                application_date=datetime.now() - timedelta(days=30),
                status="approved",
                ip_address="192.168.1.100"
            ),
            LoanApplication(
                user_id=1,
                application_amount=25000.0,
                loan_purpose="Home improvement",
                employment_status="employed",
                monthly_income=15000.0,
                application_date=datetime.now() - timedelta(days=15),
                status="pending",
                ip_address="192.168.1.100"
            ),
            LoanApplication(
                user_id=2,
                application_amount=75000.0,
                loan_purpose="Vehicle purchase",
                employment_status="employed",
                monthly_income=20000.0,
                application_date=datetime.now() - timedelta(days=20),
                status="approved",
                ip_address="192.168.1.101"
            ),
            LoanApplication(
                user_id=2,
                application_amount=30000.0,
                loan_purpose="Education",
                employment_status="employed",
                monthly_income=20000.0,
                application_date=datetime.now() - timedelta(days=5),
                status="rejected",
                rejection_reason="Insufficient income",
                ip_address="192.168.1.101"
            ),
            LoanApplication(
                user_id=3,
                application_amount=100000.0,
                loan_purpose="Real estate",
                employment_status="self_employed",
                monthly_income=25000.0,
                application_date=datetime.now() - timedelta(days=10),
                status="pending",
                ip_address="192.168.1.102"
            ),
            LoanApplication(
                user_id=3,
                application_amount=40000.0,
                loan_purpose="Business startup",
                employment_status="self_employed",
                monthly_income=25000.0,
                application_date=datetime.now() - timedelta(days=2),
                status="pending",
                ip_address="192.168.1.102"
            ),
            LoanApplication(
                user_id=3,
                application_amount=60000.0,
                loan_purpose="Equipment purchase",
                employment_status="self_employed",
                monthly_income=25000.0,
                application_date=datetime.now() - timedelta(hours=12),
                status="pending",
                ip_address="192.168.1.102"
            ),
            LoanApplication(
                user_id=4,
                application_amount=80000.0,
                loan_purpose="Medical expenses",
                employment_status="employed",
                monthly_income=18000.0,
                application_date=datetime.now() - timedelta(days=7),
                status="rejected",
                rejection_reason="High risk profile",
                ip_address="192.168.1.103"
            ),
            LoanApplication(
                user_id=5,
                application_amount=200000.0,
                loan_purpose="Investment",
                employment_status="employed",
                monthly_income=50000.0,
                application_date=datetime.now() - timedelta(days=1),
                status="rejected",
                rejection_reason="Fraud detected",
                ip_address="192.168.1.104"
            ),
            LoanApplication(
                user_id=5,
                application_amount=150000.0,
                loan_purpose="Business",
                employment_status="employed",
                monthly_income=50000.0,
                application_date=datetime.now() - timedelta(hours=6),
                status="rejected",
                rejection_reason="Blacklisted user",
                ip_address="192.168.1.104"
            )
        ]
        
        for application in loan_applications:
            db.add(application)
        db.commit()
        
        # Create loans (approved applications)
        loans = [
            Loan(
                user_id=1,
                loan_amount=50000.0,
                loan_purpose="Business expansion",
                interest_rate=12.5,
                loan_term_months=24,
                status="active",
                application_date=datetime.now() - timedelta(days=30),
                approval_date=datetime.now() - timedelta(days=28),
                disbursement_date=datetime.now() - timedelta(days=25),
                monthly_payment=2350.0,
                remaining_balance=45000.0,
                is_active=True
            ),
            Loan(
                user_id=2,
                loan_amount=75000.0,
                loan_purpose="Vehicle purchase",
                interest_rate=10.0,
                loan_term_months=36,
                status="active",
                application_date=datetime.now() - timedelta(days=20),
                approval_date=datetime.now() - timedelta(days=18),
                disbursement_date=datetime.now() - timedelta(days=15),
                monthly_payment=2420.0,
                remaining_balance=70000.0,
                is_active=True
            ),
            Loan(
                user_id=1,
                loan_amount=30000.0,
                loan_purpose="Personal loan",
                interest_rate=15.0,
                loan_term_months=12,
                status="closed",
                application_date=datetime.now() - timedelta(days=365),
                approval_date=datetime.now() - timedelta(days=360),
                disbursement_date=datetime.now() - timedelta(days=355),
                closure_date=datetime.now() - timedelta(days=30),
                monthly_payment=2700.0,
                remaining_balance=0.0,
                is_active=False
            )
        ]
        
        for loan in loans:
            db.add(loan)
        db.commit()
        
        # Update loan applications with loan IDs
        app1 = db.query(LoanApplication).filter(LoanApplication.id == 1).first()
        app3 = db.query(LoanApplication).filter(LoanApplication.id == 3).first()
        if app1:
            app1.loan_id = 1
        if app3:
            app3.loan_id = 2
        db.commit()
        
        print("✅ Dummy data seeded successfully!")
        print(f"   - {len(users)} users created")
        print(f"   - {len(identities)} identities created")
        print(f"   - {len(loan_applications)} loan applications created")
        print(f"   - {len(loans)} loans created")
        print(f"   - 1 blacklist entry created")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_dummy_data()
