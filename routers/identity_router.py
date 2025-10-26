# routers/identity_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas import IdentityCreate
from services.identity_manager import create_identity, dedup_identity

# Create router
router = APIRouter(prefix="/identity", tags=["Identity"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("")
def register_identity(identity: IdentityCreate, db: Session = Depends(get_db)):
    """Register a new identity with NID verification"""
    existing = dedup_identity(db, identity.national_id)
    if existing:
        return {"message": "Identity already exists", "id": existing.id}
    
    try:
        new_identity = create_identity(db, identity.dict())
        return {
            "message": "Identity created successfully", 
            "id": new_identity.id,
            "national_id": new_identity.national_id,
            "name": new_identity.name,
            "is_verified": new_identity.is_verified
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{national_id}")
def get_identity(national_id: str, db: Session = Depends(get_db)):
    """Get identity details by national ID"""
    from services.identity_manager import get_identity_by_national_id
    
    identity = get_identity_by_national_id(db, national_id)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    
    return {
        "id": identity.id,
        "user_id": identity.user_id,
        "name": identity.name,
        "national_id": identity.national_id,
        "date_of_birth": identity.date_of_birth,
        "gender": identity.gender,
        "place_of_birth": identity.place_of_birth,
        "father_name": identity.father_name,
        "mother_name": identity.mother_name,
        "nid_issue_date": identity.nid_issue_date,
        "nid_expiry_date": identity.nid_expiry_date,
        "nid_status": identity.nid_status,
        "is_verified": identity.is_verified,
        "verification_date": identity.verification_date,
        "risk_score": identity.risk_score,
        "country_code": identity.country_code
    }

@router.get("")
def get_identity_list_route(db: Session = Depends(get_db)):
    """Get a list of all identity records"""
    from services.identity_manager import get_identity_list

    identities = get_identity_list(db)
    
    # If you want to return an empty list when no records exist (common for lists),
    # you don't need to raise a 404. But if you prefer to enforce non-empty, you could.
    # Here, we'll just return the list (even if empty).

    return [
        {
            "id": identity.id,
            "user_id": identity.user_id,
            "name": identity.name,
            "national_id": identity.national_id,
            "date_of_birth": identity.date_of_birth,
            "gender": identity.gender,
            "place_of_birth": identity.place_of_birth,
            "father_name": identity.father_name,
            "mother_name": identity.mother_name,
            "nid_issue_date": identity.nid_issue_date,
            "nid_expiry_date": identity.nid_expiry_date,
            "nid_status": identity.nid_status,
            "is_verified": identity.is_verified,
            "verification_date": identity.verification_date,
            "risk_score": identity.risk_score,
            "country_code": identity.country_code
        }
        for identity in identities
    ]
