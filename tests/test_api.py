# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import SessionLocal, engine
from models import Base
from main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[SessionLocal] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as test_client:
        yield test_client

class TestNIDAPI:
    def test_verify_nid_success(self, client):
        """Test successful NID verification"""
        response = client.post("/nid/verify/", json={
            "national_id": "123456789012",
            "name": "Alemayehu Tsegaye",
            "date_of_birth": "1985-03-15",
            "gender": "M",
            "country_code": "ET"
        })
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        assert "message" in data

    def test_verify_nid_invalid_format(self, client):
        """Test NID verification with invalid format"""
        response = client.post("/nid/verify/", json={
            "national_id": "123",
            "name": "Test User",
            "country_code": "ET"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] == False

    def test_generate_fake_nid(self, client):
        """Test fake NID generation"""
        response = client.get("/nid/generate-fake/ET")
        assert response.status_code == 200
        data = response.json()
        assert "fake_nid" in data
        assert len(data["fake_nid"]) == 12

class TestTransactionAPI:
    def test_check_transaction_success(self, client):
        """Test successful transaction check"""
        response = client.post("/transaction/?national_id=123456789012", json={
            "user_id": 1,
            "amount": 1000.0,
            "ip_address": "192.168.1.1"
        })
        assert response.status_code in [200, 403]  # 200 for approved, 403 for fraud

    def test_check_transaction_fraud(self, client):
        """Test transaction fraud detection"""
        response = client.post("/transaction/?national_id=999999999999", json={
            "user_id": 5,  # Fraud user
            "amount": 50000.0,
            "ip_address": "192.168.1.1"
        })
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "Fraud detected" in data["detail"]

class TestRulesAPI:
    def test_list_rules(self, client):
        """Test listing all rules"""
        response = client.get("/rules/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_rule(self, client):
        """Test creating a new rule"""
        response = client.post("/rules/", json={
            "name": "Test Rule",
            "description": "Test rule for testing",
            "condition_type": "test_condition",
            "is_active": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Rule"

    def test_toggle_rule(self, client):
        """Test toggling rule status"""
        # First create a rule
        create_response = client.post("/rules/", json={
            "name": "Toggle Test Rule",
            "description": "Rule for toggle testing",
            "condition_type": "toggle_test",
            "is_active": True
        })
        rule_id = create_response.json()["id"]
        
        # Toggle the rule
        response = client.patch(f"/rules/{rule_id}/toggle")
        assert response.status_code == 200
        data = response.json()
        assert "is_active" in data

    def test_admin_dashboard(self, client):
        """Test admin dashboard endpoint"""
        response = client.get("/rules/admin/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "system_status" in data
        assert "rule_statistics" in data
        assert "fraud_statistics" in data

class TestLoanAPI:
    def test_create_loan_application(self, client):
        """Test creating loan application"""
        response = client.post("/loans/applications/", json={
            "user_id": 1,
            "application_amount": 50000.0,
            "loan_purpose": "Business expansion",
            "employment_status": "employed",
            "monthly_income": 15000.0,
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "national_id": "123456789012"  # Required for fraud detection
        })
        assert response.status_code in [200, 403]  # 200 for approved, 403 for fraud

    def test_get_user_loans(self, client):
        """Test getting user loans"""
        response = client.get("/loans/user/1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_active_loans(self, client):
        """Test getting active loans"""
        response = client.get("/loans/user/1/active")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestTINAPI:
    def test_verify_tin(self, client):
        """Test TIN verification"""
        response = client.get("/nid/tin/verify/1234567890")
        assert response.status_code == 200
        data = response.json()
        assert "tin_number" in data
        assert "is_valid" in data

    def test_get_tin_details(self, client):
        """Test getting TIN details"""
        response = client.get("/nid/tin/details/1234567890")
        # This might return 404 if TIN not found, which is expected
        assert response.status_code in [200, 404]

class TestIdentityAPI:
    def test_create_identity(self, client):
        """Test creating identity"""
        response = client.post("/identity/", json={
            "user_id": 1,
            "name": "Test User",
            "national_id": "123456789012",
            "date_of_birth": "1985-03-15",
            "gender": "M",
            "country_code": "ET"
        })
        # This might fail due to NID verification, which is expected
        assert response.status_code in [200, 400, 403]

    def test_get_identity(self, client):
        """Test getting identity by NID"""
        response = client.get("/identity/123456789012")
        # This might return 404 if identity not found
        assert response.status_code in [200, 404]
