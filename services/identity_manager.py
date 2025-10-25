from sqlalchemy.orm import Session
from models import Identity, Blacklist
from .nid_service import nid_service
from .tin_service import tin_service

def get_identity_by_national_id(db: Session, nid: str):
    return db.query(Identity).filter(Identity.national_id == nid).first()

def is_blacklisted(db: Session, nid: str):
    return db.query(Blacklist).filter(Blacklist.national_id == nid).first() is not None

def verify_nid_with_government(nid: str, name: str, dob: str = None, gender: str = None, country_code: str = 'ET'):
    """Verify NID with government database and cross-check KYC data"""
    # Validate NID format first
    if not nid_service.validate_nid_format(nid, country_code):
        return False, "Invalid NID format", None
    
    # Check if NID is blacklisted (using database session)
    from database import SessionLocal
    db = SessionLocal()
    try:
        blacklist_entry = db.query(Blacklist).filter(Blacklist.national_id == nid).first()
        if blacklist_entry:
            return False, f"NID blacklisted: {blacklist_entry.reason}", None
    finally:
        db.close()
    
    # Verify with government database
    is_valid, nid_data = nid_service.verify_nid_with_government_db(nid)
    if not is_valid:
        return False, "NID not found in government database", None
    
    # Cross-verify KYC data
    kyc_valid, kyc_message = nid_service.cross_verify_kyc_data(nid, name, dob, gender)
    if not kyc_valid:
        return False, kyc_message, nid_data
    
    return True, "NID verification successful", nid_data

def dedup_identity(db: Session, national_id: str):
    """dedup: if national_id exists, return existing; else allow creation."""
    return get_identity_by_national_id(db, national_id)

def verify_tin_with_ministry(tin_number: str, business_name: str = None):
    """Verify TIN with trade ministry API"""
    if business_name:
        # Cross-verify TIN with business name
        return tin_service.cross_verify_tin_name(tin_number, business_name)
    else:
        # Just verify TIN exists
        is_valid, tin_data, message = tin_service.verify_tin_with_ministry(tin_number)
        return is_valid, message

def create_identity(db: Session, identity_data):
    """Create identity with NID and TIN verification"""
    nid = identity_data.get('national_id')
    name = identity_data.get('name')
    dob = identity_data.get('date_of_birth')
    gender = identity_data.get('gender')
    country_code = identity_data.get('country_code', 'ET')
    tin_number = identity_data.get('tin_number')
    business_name = identity_data.get('business_name')
    
    # Verify NID first
    is_valid, message, nid_details = verify_nid_with_government(
        nid, name, dob, gender, country_code
    )
    
    if not is_valid:
        raise ValueError(f"NID verification failed: {message}")
    
    # Verify TIN if provided
    if tin_number:
        tin_valid, tin_message = verify_tin_with_ministry(tin_number, business_name)
        if not tin_valid:
            raise ValueError(f"TIN verification failed: {tin_message}")
    
    # Create identity with NID details
    identity_data.update({
        'date_of_birth': nid_details.get('date_of_birth'),
        'gender': nid_details.get('gender'),
        'place_of_birth': nid_details.get('place_of_birth'),
        'father_name': nid_details.get('father_name'),
        'mother_name': nid_details.get('mother_name'),
        'nid_issue_date': nid_details.get('issue_date'),
        'nid_expiry_date': nid_details.get('expiry_date'),
        'nid_status': nid_details.get('status'),
        'is_verified': True,
        'country_code': country_code
    })
    
    db_identity = Identity(**identity_data)
    db.add(db_identity)
    db.commit()
    db.refresh(db_identity)
    return db_identity