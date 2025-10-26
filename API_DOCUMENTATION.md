#  Fraud Management System API Documentation

##  Overview

The Fraud Management System API provides comprehensive fraud detection capabilities with NID verification, TIN validation, and loan management.

##  Quick Start

### Base URL
```
http://localhost:8000
```

### Swagger UI
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

##  API Endpoints

###  NID Verification (`/nid/`)

#### `POST /nid/verify/`
Verify National ID with government database
```json
{
  "national_id": "123456789012",
  "name": "Alemayehu Tsegaye",
  "date_of_birth": "1985-03-15",
  "gender": "M",
  "country_code": "ET"
}
```

#### `GET /nid/details/{nid}`
Get NID details from government database

#### `GET /nid/generate-fake/{country_code}`
Generate fake NID for testing

#### `GET /nid/validate-format/{nid}`
Validate NID format

###  TIN Verification (`/nid/tin/`)

#### `GET /nid/tin/verify/{tin_number}`
Verify TIN with eTrade API

#### `GET /nid/tin/details/{tin_number}`
Get TIN details from trade ministry

#### `GET /nid/tin/status/{tin_number}`
Check TIN status

###  Identity Management (`/identity/`)

#### `POST /identity/`
Register new identity with NID verification
```json
{
  "user_id": 1,
  "name": "Alemayehu Tsegaye",
  "national_id": "123456789012",
  "date_of_birth": "1985-03-15",
  "gender": "M",
  "country_code": "ET"
}
```

#### `GET /identity/{national_id}`
Get identity details by national ID

###  Transaction Fraud Detection (`/transaction/`)

#### `POST /transaction/`
Check transaction for fraud
```json
{
  "user_id": 1,
  "amount": 50000.0,
  "ip_address": "192.168.1.100"
}
```

#### `GET /transaction/history/{user_id}`
Get transaction history for a user

###  Loan Management (`/loans/`)

#### `POST /loans/applications/`
Create loan application
```json
{
  "user_id": 1,
  "application_amount": 50000.0,
  "loan_purpose": "Business expansion",
  "employment_status": "employed",
  "monthly_income": 15000.0,
  "ip_address": "192.168.1.100"
}
```

#### `GET /loans/applications/user/{user_id}`
Get user's loan applications

#### `POST /loans/applications/{application_id}/approve`
Approve loan application

#### `POST /loans/applications/{application_id}/reject`
Reject loan application

#### `GET /loans/user/{user_id}`
Get user's loans

#### `GET /loans/user/{user_id}/active`
Get active loans for user

###  Rule Management (`/rules/`)

#### `GET /rules/`
List all fraud detection rules

#### `POST /rules/`
Create new fraud detection rule

#### `PUT /rules/{rule_id}`
Update fraud detection rule

#### `DELETE /rules/{rule_id}`
Delete fraud detection rule

#### `PATCH /rules/{rule_id}/toggle`
Toggle rule active/inactive status

##  Fraud Detection Rules

The system uses 9 static rules for fraud detection:

1. **Active Loan Check** - Flag if user has active loan
2. **Phone Variation** - Detect different phone with same name/gender
3. **Rapid Reapply** - Flag reapplications within 24h
4. **Fraud DB Match** - Check against known fraudsters
5. **Excessive Reapply** - Flag >2 applications/day
6. **TIN Mismatch** - Verify TIN matches registered name
7. **NID KYC Mismatch** - Cross-verify NID with KYC data
8. **NID Expired** - Flag expired NIDs
9. **NID Suspended** - Flag suspended NIDs

##  Response Examples

### Successful NID Verification
```json
{
  "is_valid": true,
  "message": "Names match with high confidence (95% similarity)",
  "nid_details": {
    "name": "Alemayehu Tsegaye",
    "date_of_birth": "1985-03-15",
    "gender": "M",
    "status": "active"
  },
  "verification_status": "verified"
}
```

### Fraud Detected
```json
{
  "is_fraud": true,
  "reason": "NID expired; Active loan check",
  "risk_score": 1.0
}
```

### Transaction Approved
```json
{
  "is_fraud": false,
  "reason": "Approved",
  "risk_score": 0.0
}
```

## Testing

### Test Data Available
The system comes with pre-seeded test data:

- **5 Users** with different profiles
- **5 Identities** with various NID statuses
- **10 Loan Applications** with different statuses
- **3 Loans** (active and closed)
- **1 Blacklist Entry** for fraud testing

### Test Scenarios
-  Normal user transactions
-  Fraud detection with expired NID
-  Fraud detection with suspended NID
-  Fraud detection with blacklisted user
-  Excessive reapply detection
-  Active loan detection

##  Development

### Running the API
```bash
uvicorn main:app --reload
```

### Seeding Data
```bash
python run_seed.py
```

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Error Handling

The API returns appropriate HTTP status codes:

- **200** - Success
- **400** - Bad Request (validation errors)
- **403** - Forbidden (fraud detected)
- **404** - Not Found
- **500** - Internal Server Error

## Security

- **CORS** enabled for frontend integration
- **Input validation** on all endpoints
- **Fraud detection** on all transactions
- **NID/TIN verification** with government APIs
