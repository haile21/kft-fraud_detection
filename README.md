# Fraud Management System

A comprehensive fraud detection and management system built with FastAPI, featuring dynamic rule-based and AI based fraud detection, alert management, case tracking and user role management.

## Features

### Core Fraud Detection
- **NID Verification** - National ID validation with government database simulation
- **TIN Verification** - Real-time TIN validation with eTrade API integration
- **Dynamic Rule Engine** - 9 configurable fraud detection rules
- **Real-time Fraud Detection** - Automatic fraud detection for transactions and loan applications

### Alert & Case Management
- **Automatic Alert Generation** - Alerts are automatically created when fraud is detected
- **Case Management** - Fraud analysts can create and manage cases from alerts
- **Follow-up Tracking** - Log follow-ups and investigation notes for each case
- **Status Management** - Track case progress from open to closed

### User & Role Management
- **JWT Authentication** - Secure token-based authentication
- **Role-based Access Control** - Super Admin and Fraud Analyst roles
- **User Management** - Complete user registration and management system
- **Permission Control** - Different access levels for different user types

### API-First Design
- **RESTful API** - Complete API for frontend developers to build custom interfaces
- **Comprehensive Endpoints** - All functionality exposed through well-documented APIs
- **Real-time Data** - APIs provide live data for dashboards and management interfaces
- **Role-based Access** - API endpoints respect user roles and permissions

## Architecture

### Backend (FastAPI)
- **Models**: User, Identity, FraudLog, Alert, Case, CaseFollowUp, UserRole, Rule, Loan, etc.
- **Services**: AlertService, CaseService, UserService, FraudOrchestrator, RuleEngine
- **Routers**: RESTful API endpoints for all functionality
- **Authentication**: JWT-based authentication with role-based access control

### Frontend Development
- **API-Ready**: Complete REST API for frontend developers
- **Authentication**: JWT-based authentication endpoints
- **Real-time Data**: Live data endpoints for dashboards
- **Role-based UI**: Different endpoints for different user roles

## Frontend Development Guide

This API is designed to be consumed by frontend developers to build custom fraud management interfaces. Here's what you need to know:

### Authentication Flow
1. **Register/Login**: Use `/users/register` and `/users/login` endpoints
2. **Store JWT Token**: Save the `access_token` from login response
3. **Include Token**: Add `Authorization: Bearer <token>` header to all requests
4. **Handle Expiration**: Tokens expire in 60 minutes, implement refresh logic

### User Roles & Permissions
- **Super Admin**: Full access to all endpoints
- **Fraud Analyst**: Limited access to assigned alerts/cases only
- **Regular User**: Basic user management endpoints

### Key Frontend Features to Implement

#### Dashboard Overview
- **Statistics**: Use `/alerts/dashboard/statistics` and `/cases/dashboard/statistics`
- **Recent Alerts**: Use `/alerts/?limit=5` for recent activity
- **Quick Actions**: Direct links to create cases, assign alerts

#### Alert Management
- **List View**: Use `/alerts/` with filtering (`?status=open&assigned_to=123`)
- **Detail View**: Use `/alerts/{id}` for full alert details
- **Assignment**: Use `/alerts/{id}/assign/{analyst_id}` for assignment
- **Status Updates**: Use `PATCH /alerts/{id}` to update status

#### Case Management
- **List View**: Use `/cases/` with filtering
- **Create Case**: Use `POST /cases/` with alert_id
- **Follow-ups**: Use `/cases/{id}/follow-ups` for case history
- **Close Case**: Use `POST /cases/{id}/close` with resolution notes

#### User Management (Super Admin Only)
- **User List**: Use `/users/` to get all users
- **Role Assignment**: Use `POST /users/{id}/roles` to assign roles
- **Analyst List**: Use `/users/analysts/list` for assignment dropdowns

### Sample Frontend Implementation

```javascript
// Authentication
const login = async (username, password) => {
  const response = await fetch('/users/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  return data;
};

// Get alerts with authentication
const getAlerts = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch('/alerts/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};

// Assign alert
const assignAlert = async (alertId, analystId) => {
  const token = localStorage.getItem('token');
  const response = await fetch(`/alerts/${alertId}/assign/${analystId}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

### UI/UX Recommendations
- **Role-based Navigation**: Show different menu items based on user role
- **Real-time Updates**: Implement polling or WebSocket for live updates
- **Responsive Design**: Ensure mobile compatibility
- **Status Indicators**: Use color coding for alert/case status
- **Bulk Operations**: Allow multiple selections for efficiency
- **Search & Filter**: Implement search and filtering capabilities

## API Endpoints

### Authentication
- `POST /users/register` - Register new user
- `POST /users/login` - Login and get JWT token
- `GET /users/me` - Get current user info

### Fraud Detection
- `POST /transaction/` - Check transaction for fraud
- `GET /transaction/history/{user_id}` - Get transaction history

### Alert Management
- `GET /alerts/` - Get all alerts (with filtering)
- `GET /alerts/{alert_id}` - Get specific alert
- `PATCH /alerts/{alert_id}` - Update alert
- `POST /alerts/{alert_id}/assign/{analyst_id}` - Assign alert to analyst
- `POST /alerts/{alert_id}/close` - Close alert
- `GET /alerts/dashboard/statistics` - Get alert statistics

### Case Management
- `GET /cases/` - Get all cases (with filtering)
- `GET /cases/{case_id}` - Get specific case
- `POST /cases/` - Create new case from alert
- `PATCH /cases/{case_id}` - Update case
- `POST /cases/{case_id}/assign/{analyst_id}` - Assign case to analyst
- `POST /cases/{case_id}/close` - Close case
- `POST /cases/{case_id}/follow-ups` - Add follow-up to case
- `GET /cases/{case_id}/follow-ups` - Get case follow-ups
- `GET /cases/dashboard/statistics` - Get case statistics

### User Management
- `GET /users/` - Get all users (Super Admin only)
- `GET /users/{user_id}` - Get specific user
- `POST /users/{user_id}/roles` - Assign role to user
- `GET /users/{user_id}/roles` - Get user roles
- `GET /users/analysts/list` - Get all fraud analysts

### Other Endpoints
- `GET /nid/` - NID verification endpoints
- `GET /identity/` - Identity management endpoints
- `GET /rules/` - Rule management endpoints
- `GET /loans/` - Loan management endpoints

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```bash
   python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
   ```

4. Seed initial data:
   ```bash
   python run_seed.py
   ```

5. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

6. Open the fraud portal:
   - Open `fraud_portal.html` in your browser
   - Or visit `http://localhost:8000/docs` for API documentation

## User Roles

### Super Admin
- Full access to all features
- Can create and assign cases
- Can manage users and roles
- Can view all statistics and reports
- Can manage fraud detection rules

### Fraud Analyst
- Can view assigned alerts and cases
- Can add follow-ups to cases
- Can update case status
- Can close cases with resolution notes
- Limited access to user management

##  Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - Bcrypt password hashing
- **Role-based Access Control** - Different permissions for different roles
- **Input Validation** - Pydantic models for request validation
- **SQL Injection Protection** - SQLAlchemy ORM prevents SQL injection

##  Fraud Detection Rules

The system includes 9 configurable fraud detection rules:

1. **Active Loan Check** - Flag if user has active loan
2. **Phone Variation Check** - Detect different phone with same name/gender
3. **Rapid Reapply Check** - Flag reapplications within 24h
4. **Fraud Database Match** - Check against known fraudsters
5. **Excessive Reapply Check** - Flag >2 applications/day
6. **TIN Mismatch Check** - Verify TIN matches registered name
7. **NID KYC Mismatch Check** - Cross-verify NID with KYC data
8. **NID Expired Check** - Flag expired NIDs
9. **NID Suspended Check** - Flag suspended NIDs

##  Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

##  Monitoring & Analytics

The system provides comprehensive monitoring through:
- **Alert Statistics** - Total, open, assigned, investigating, resolved, closed alerts
- **Case Statistics** - Total, open, investigating, resolved, closed cases
- **Fraud Detection Metrics** - Success rates and false positive tracking
- **User Activity Logs** - Track user actions and system usage

##  Workflow

### Fraud Detection Workflow
1. Transaction/loan application is submitted
2. Fraud detection rules are evaluated
3. If fraud is detected, an alert is automatically created
4. Super admin can assign alert to fraud analyst
5. Fraud analyst creates case from alert
6. Case is investigated with follow-ups logged
7. Case is closed with resolution notes

### Alert Management Workflow
1. Alert is created automatically when fraud is detected
2. Alert is assigned to fraud analyst by super admin
3. Fraud analyst investigates the alert
4. Alert status is updated (assigned → investigating → resolved)
5. Alert is closed when investigation is complete

##  Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Production Considerations
- Use environment variables for sensitive configuration
- Set up proper database backups
- Configure HTTPS for production
- Set up monitoring and logging
- Use a production WSGI server like Gunicorn

##  API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
 

For support and questions, contact the Fraud Management Team at hweleslassie@kifiya.com.
