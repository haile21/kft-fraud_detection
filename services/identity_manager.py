from sqlalchemy.orm import Session
from ..models import Identity, Blacklist

def get_identity_by_national_id(db: Session, nid: str):
    return db.query(Identity).filter(Identity.national_id == nid).first()

def is_blacklisted(db: Session, nid: str):
    return db.query(Blacklist).filter(Blacklist.national_id == nid).first() is not None

def dedup_identity(db: Session, national_id: str):
    """dedup: if national_id exists, return existing; else allow creation."""
    return get_identity_by_national_id(db, national_id)

def create_identity(db: Session, identity_data):
    db_identity = Identity(**identity_data)
    db.add(db_identity)
    db.commit()
    db.refresh(db_identity)
    return db_identity