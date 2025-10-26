# routers/nid_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from database import SessionLocal
from schemas import NIDVerificationRequest, NIDVerificationResponse
from services.identity_manager import verify_nid_with_government, verify_tin_with_ministry
from services.nid_service import nid_service
from services.tin_service import tin_service

# Create router
router = APIRouter(prefix="/nid", tags=["NID"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/verify", response_model=NIDVerificationResponse)
def verify_nid(request: NIDVerificationRequest, db: Session = Depends(get_db)):
    """
     Verify NID with Government Database
    
    Verifies a National ID against the simulated government database and cross-checks KYC data.
    
    **Features:**
    -  NID format validation
    -  Government database lookup
    -  KYC data cross-verification
    -  Fuzzy name matching
    -  Blacklist checking
    
    **Example Request:**
    ```json
    {
        "national_id": "123456789012",
        "name": "Alemayehu Tsegaye",
        "date_of_birth": "1985-03-15",
        "gender": "M",
        "country_code": "ET"
    }
    ```
    
    **Example Response:**
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
    """
    is_valid, message, nid_details = verify_nid_with_government(
        request.national_id, 
        request.name, 
        request.date_of_birth, 
        request.gender, 
        request.country_code
    )
    
    if is_valid:
        return NIDVerificationResponse(
            is_valid=True,
            message=message,
            nid_details=nid_details,
            verification_status="verified"
        )
    else:
        return NIDVerificationResponse(
            is_valid=False,
            message=message,
            nid_details=nid_details,
            verification_status="failed"
        )

@router.get("/details/{nid}")
def get_nid_details(nid: str):
    """Get NID details from government database"""
    nid_details = nid_service.get_nid_details(nid)
    if nid_details:
        return {"nid": nid, "details": nid_details}
    else:
        raise HTTPException(status_code=404, detail="NID not found")

@router.get("/generate-fake/{country_code}")
def generate_fake_nid(country_code: str = 'ET'):
    """Generate a fake NID for testing purposes"""
    fake_nid = nid_service.generate_fake_nid(country_code)
    return {"fake_nid": fake_nid, "country_code": country_code}

@router.get("/validate-format/{nid}")
def validate_nid_format(nid: str, country_code: str = 'ET'):
    """Validate NID format for a specific country"""
    is_valid = nid_service.validate_nid_format(nid, country_code)
    return {
        "nid": nid,
        "country_code": country_code,
        "is_valid_format": is_valid,
        "message": "Valid format" if is_valid else "Invalid format"
    }

# TIN Verification Endpoints
@router.get("/tin/verify/{tin_number}")
def verify_tin(tin_number: str, business_name: str = None):
    """Verify TIN with trade ministry API"""
    if business_name:
        is_valid, message = verify_tin_with_ministry(tin_number, business_name)
    else:
        is_valid, message = verify_tin_with_ministry(tin_number)
    
    return {
        "tin_number": tin_number,
        "business_name": business_name,
        "is_valid": is_valid,
        "message": message
    }

@router.get("/tin/details/{tin_number}")
def get_tin_details(tin_number: str):
    """Get TIN details from trade ministry"""
    tin_details = tin_service.get_tin_details(tin_number)
    if tin_details:
        return {"tin_number": tin_number, "details": tin_details}
    else:
        raise HTTPException(status_code=404, detail="TIN not found")

@router.get("/tin/status/{tin_number}")
def check_tin_status(tin_number: str):
    """Check if TIN is active/valid"""
    is_active, message = tin_service.check_tin_status(tin_number)
    return {
        "tin_number": tin_number,
        "is_active": is_active,
        "message": message
    }
