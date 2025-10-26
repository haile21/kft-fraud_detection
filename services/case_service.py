# services/case_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models import Case, CaseFollowUp, Alert, User
from schemas import CaseCreate, CaseUpdate, CaseFollowUpCreate

class CaseService:
    def __init__(self):
        pass
    
    def generate_case_number(self, db: Session) -> str:
        """Generate unique case number"""
        # Get the count of cases created today
        today = datetime.utcnow().date()
        count = db.query(Case).filter(
            Case.created_at >= today
        ).count()
        
        # Format: CASE-YYYYMMDD-XXX
        case_number = f"CASE-{today.strftime('%Y%m%d')}-{count + 1:03d}"
        return case_number
    
    def create_case_from_alert(self, db: Session, alert_id: int, created_by: int, case_data: CaseCreate) -> Case:
        """Create a case from an alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ValueError("Alert not found")
        
        case_number = self.generate_case_number(db)
        
        case = Case(
            alert_id=alert_id,
            case_number=case_number,
            title=case_data.title,
            description=case_data.description,
            status="open",
            priority=case_data.priority,
            assigned_to=case_data.assigned_to,
            created_by=created_by
        )
        
        db.add(case)
        db.commit()
        db.refresh(case)
        
        # Update alert status to assigned if case is assigned
        if case_data.assigned_to:
            alert.status = "assigned"
            alert.assigned_to = case_data.assigned_to
            db.commit()
        
        return case
    
    def get_cases(self, db: Session, status: Optional[str] = None, assigned_to: Optional[int] = None) -> List[Case]:
        """Get all cases with optional filtering"""
        query = db.query(Case)
        
        if status:
            query = query.filter(Case.status == status)
        if assigned_to:
            query = query.filter(Case.assigned_to == assigned_to)
        
        return query.order_by(Case.created_at.desc()).all()
    
    def get_case_by_id(self, db: Session, case_id: int) -> Optional[Case]:
        """Get case by ID"""
        return db.query(Case).filter(Case.id == case_id).first()
    
    def get_case_by_number(self, db: Session, case_number: str) -> Optional[Case]:
        """Get case by case number"""
        return db.query(Case).filter(Case.case_number == case_number).first()
    
    def update_case(self, db: Session, case_id: int, case_update: CaseUpdate) -> Optional[Case]:
        """Update case"""
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return None
        
        update_data = case_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(case, field, value)
        
        # If status is being changed to closed, set closed_at
        if case_update.status == "closed":
            case.closed_at = datetime.utcnow()
        
        case.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(case)
        return case
    
    def assign_case(self, db: Session, case_id: int, analyst_id: int) -> Optional[Case]:
        """Assign case to a fraud analyst"""
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return None
        
        case.assigned_to = analyst_id
        case.status = "investigating"
        case.updated_at = datetime.utcnow()
        
        # Also update the associated alert
        alert = db.query(Alert).filter(Alert.id == case.alert_id).first()
        if alert:
            alert.assigned_to = analyst_id
            alert.status = "assigned"
        
        db.commit()
        db.refresh(case)
        return case
    
    def close_case(self, db: Session, case_id: int, resolution_notes: str) -> Optional[Case]:
        """Close a case"""
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return None
        
        case.status = "closed"
        case.closed_at = datetime.utcnow()
        case.resolution_notes = resolution_notes
        case.updated_at = datetime.utcnow()
        
        # Also close the associated alert
        alert = db.query(Alert).filter(Alert.id == case.alert_id).first()
        if alert:
            alert.status = "closed"
        
        db.commit()
        db.refresh(case)
        return case
    
    def add_follow_up(self, db: Session, case_id: int, created_by: int, follow_up_data: CaseFollowUpCreate) -> CaseFollowUp:
        """Add follow-up to a case"""
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise ValueError("Case not found")
        
        follow_up = CaseFollowUp(
            case_id=case_id,
            created_by=created_by,
            follow_up_type=follow_up_data.follow_up_type,
            notes=follow_up_data.notes
        )
        
        db.add(follow_up)
        db.commit()
        db.refresh(follow_up)
        
        # Update case updated_at timestamp
        case.updated_at = datetime.utcnow()
        db.commit()
        
        return follow_up
    
    def get_case_follow_ups(self, db: Session, case_id: int) -> List[CaseFollowUp]:
        """Get all follow-ups for a case"""
        return db.query(CaseFollowUp).filter(
            CaseFollowUp.case_id == case_id
        ).order_by(CaseFollowUp.created_at.desc()).all()
    
    def get_case_statistics(self, db: Session) -> dict:
        """Get case statistics for dashboard"""
        total_cases = db.query(Case).count()
        open_cases = db.query(Case).filter(Case.status == "open").count()
        investigating_cases = db.query(Case).filter(Case.status == "investigating").count()
        resolved_cases = db.query(Case).filter(Case.status == "resolved").count()
        closed_cases = db.query(Case).filter(Case.status == "closed").count()
        
        return {
            "total_cases": total_cases,
            "open_cases": open_cases,
            "investigating_cases": investigating_cases,
            "resolved_cases": resolved_cases,
            "closed_cases": closed_cases
        }

# Create service instance
case_service = CaseService()
