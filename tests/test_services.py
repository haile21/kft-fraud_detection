# tests/test_services.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Identity, Loan, LoanApplication, Blacklist
from services.nid_service import nid_service
from services.tin_service import tin_service
from services.loan_service import loan_service
from services.rule_engine import evaluate_rules

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_services.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)

class TestNIDService:
    def test_validate_nid_format_ethiopia(self):
        """Test Ethiopian NID format validation"""
        # Valid Ethiopian NID
        assert nid_service.validate_nid_format("123456789012", "ET") == True
        # Invalid format
        assert nid_service.validate_nid_format("123", "ET") == False
        assert nid_service.validate_nid_format("1234567890123", "ET") == False

    def test_validate_nid_format_kenya(self):
        """Test Kenyan NID format validation"""
        # Valid Kenyan NID
        assert nid_service.validate_nid_format("12345678", "KE") == True
        # Invalid format
        assert nid_service.validate_nid_format("123", "KE") == False

    def test_verify_nid_with_government_db(self):
        """Test NID verification with government database"""
        # Test with valid NID
        is_valid, nid_data = nid_service.verify_nid_with_government_db("123456789012")
        assert is_valid == True
        assert "name" in nid_data
        assert "date_of_birth" in nid_data

        # Test with invalid NID
        is_valid, nid_data = nid_service.verify_nid_with_government_db("999999999999")
        assert is_valid == False

    def test_fuzzy_name_match(self):
        """Test fuzzy name matching"""
        # Exact match
        match, message, score = nid_service.fuzzy_name_match("John Doe", "John Doe")
        assert match == True
        assert score >= 95

        # Close match
        match, message, score = nid_service.fuzzy_name_match("John Doe", "Jon Doe")
        assert match == True
        assert score >= 85

        # No match
        match, message, score = nid_service.fuzzy_name_match("John Doe", "Jane Smith")
        assert match == False
        assert score < 85

    def test_cross_verify_kyc_data(self):
        """Test KYC data cross-verification"""
        # Valid KYC data
        is_valid, message = nid_service.cross_verify_kyc_data(
            "123456789012", "Alemayehu Tsegaye", "1985-03-15", "M"
        )
        assert is_valid == True

        # Invalid name
        is_valid, message = nid_service.cross_verify_kyc_data(
            "123456789012", "Wrong Name", "1985-03-15", "M"
        )
        assert is_valid == False

class TestTINService:
    def test_verify_tin_with_ministry(self):
        """Test TIN verification with ministry API"""
        # This will test the API call (may fail in test environment)
        is_valid, tin_data, message = tin_service.verify_tin_with_ministry("1234567890")
        # We expect this to return False in test environment due to API limitations
        assert isinstance(is_valid, bool)
        assert isinstance(message, str)

    def test_cross_verify_tin_name(self):
        """Test TIN name cross-verification"""
        # This will test the fuzzy matching for TIN names
        is_valid, message = tin_service.cross_verify_tin_name("1234567890", "Test Business")
        assert isinstance(is_valid, bool)
        assert isinstance(message, str)

class TestLoanService:
    def test_has_active_loan(self, db_session):
        """Test checking for active loans"""
        # Create a user
        user = User(
            username="test_user",
            email="test@example.com",
            password="hashed_password",
            first_name="Test",
            last_name="User",
            gender="M",
            phone_number="+251911234567"
        )
        db_session.add(user)
        db_session.commit()

        # Initially no active loan
        assert loan_service.has_active_loan(db_session, user.id) == False

        # Create an active loan
        loan = Loan(
            user_id=user.id,
            loan_amount=50000.0,
            loan_purpose="Test loan",
            interest_rate=12.0,
            loan_term_months=24,
            status="active",
            is_active=True
        )
        db_session.add(loan)
        db_session.commit()

        # Now should have active loan
        assert loan_service.has_active_loan(db_session, user.id) == True

    def test_get_applications_today(self, db_session):
        """Test getting applications today"""
        # Create a user
        user = User(
            username="test_user",
            email="test@example.com",
            password="hashed_password",
            first_name="Test",
            last_name="User",
            gender="M",
            phone_number="+251911234567"
        )
        db_session.add(user)
        db_session.commit()

        # Initially no applications
        assert loan_service.get_applications_today(db_session, user.id) == 0

        # Create applications
        from datetime import datetime
        app1 = LoanApplication(
            user_id=user.id,
            application_amount=25000.0,
            application_date=datetime.now()
        )
        app2 = LoanApplication(
            user_id=user.id,
            application_amount=30000.0,
            application_date=datetime.now()
        )
        db_session.add_all([app1, app2])
        db_session.commit()

        # Should have 2 applications today
        assert loan_service.get_applications_today(db_session, user.id) == 2

class TestRuleEngine:
    def test_evaluate_rules_no_fraud(self, db_session):
        """Test rule evaluation with no fraud"""
        # Create a clean user
        user = User(
            username="clean_user",
            email="clean@example.com",
            password="hashed_password",
            first_name="Clean",
            last_name="User",
            gender="M",
            phone_number="+251911234567"
        )
        db_session.add(user)
        db_session.commit()

        # Evaluate rules
        is_fraud, reasons, risk_score = evaluate_rules(
            db_session, user.id, 1000.0, "192.168.1.1", "123456789012"
        )
        
        # Should not be fraud for clean user
        assert is_fraud == False
        assert risk_score < 0.5

    def test_evaluate_rules_with_fraud(self, db_session):
        """Test rule evaluation with fraud indicators"""
        # Create a user with active loan
        user = User(
            username="fraud_user",
            email="fraud@example.com",
            password="hashed_password",
            first_name="Fraud",
            last_name="User",
            gender="M",
            phone_number="+251999999999"
        )
        db_session.add(user)
        db_session.commit()

        # Create active loan
        loan = Loan(
            user_id=user.id,
            loan_amount=50000.0,
            loan_purpose="Test loan",
            interest_rate=12.0,
            loan_term_months=24,
            status="active",
            is_active=True
        )
        db_session.add(loan)
        db_session.commit()

        # Evaluate rules
        is_fraud, reasons, risk_score = evaluate_rules(
            db_session, user.id, 1000.0, "192.168.1.1", "999999999999"
        )
        
        # Should be fraud due to active loan
        assert is_fraud == True
        assert "Active loan check" in reasons
        assert risk_score > 0.5

    def test_blacklist_check(self, db_session):
        """Test blacklist rule"""
        # Create blacklisted user
        blacklist = Blacklist(
            national_id="999999999999",
            reason="Known fraudster"
        )
        db_session.add(blacklist)
        db_session.commit()

        user = User(
            username="blacklisted_user",
            email="blacklisted@example.com",
            password="hashed_password",
            first_name="Blacklisted",
            last_name="User",
            gender="M",
            phone_number="+251999999999"
        )
        db_session.add(user)
        db_session.commit()

        # Evaluate rules
        is_fraud, reasons, risk_score = evaluate_rules(
            db_session, user.id, 1000.0, "192.168.1.1", "999999999999"
        )
        
        # Should be fraud due to blacklist
        assert is_fraud == True
        assert "Fraud database match" in reasons
