# services/alert_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models import Alert, FraudLog, User
from schemas import AlertCreate, AlertUpdate

class AlertService:
    def __init__(self):
        pass
    
    def create_alert_from_fraud_log(self, db: Session, fraud_log_id: int) -> Alert:
        """Create an alert from a fraud log entry"""
        fraud_log = db.query(FraudLog).filter(FraudLog.id == fraud_log_id).first()
        if not fraud_log:
            raise ValueError("Fraud log not found")
        
        # Determine alert type and severity based on fraud reason
        alert_type = "transaction_fraud"
        severity = "medium"
        
        if "blacklist" in fraud_log.reason.lower():
            severity = "high"
        elif "active loan" in fraud_log.reason.lower():
            severity = "medium"
        elif "expired" in fraud_log.reason.lower() or "suspended" in fraud_log.reason.lower():
            severity = "high"
        
        # Create alert
        alert = Alert(
            fraud_log_id=fraud_log_id,
            user_id=fraud_log.user_id,
            alert_type=alert_type,
            severity=severity,
            status="open",
            description=f"Fraud detected: {fraud_log.reason}",
            fraud_reason=fraud_log.reason,
            risk_score=1.0 if fraud_log.is_fraud else 0.0
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    
    def get_alerts(self, db: Session, status: Optional[str] = None, assigned_to: Optional[int] = None) -> List[Alert]:
        """Get all alerts with optional filtering"""
        query = db.query(Alert)
        
        if status:
            query = query.filter(Alert.status == status)
        if assigned_to:
            query = query.filter(Alert.assigned_to == assigned_to)
        
        return query.order_by(Alert.created_at.desc()).all()
    
    def get_alert_by_id(self, db: Session, alert_id: int) -> Optional[Alert]:
        """Get alert by ID"""
        return db.query(Alert).filter(Alert.id == alert_id).first()
    
    def update_alert(self, db: Session, alert_id: int, alert_update: AlertUpdate) -> Optional[Alert]:
        """Update alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        update_data = alert_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(alert, field, value)
        
        alert.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(alert)
        return alert
    
    def assign_alert(self, db: Session, alert_id: int, analyst_id: int) -> Optional[Alert]:
        """Assign alert to a fraud analyst"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.assigned_to = analyst_id
        alert.status = "assigned"
        alert.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(alert)
        return alert
    
    def close_alert(self, db: Session, alert_id: int) -> Optional[Alert]:
        """Close an alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.status = "closed"
        alert.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(alert)
        return alert
    
    def get_alert_statistics(self, db: Session) -> dict:
        """Get alert statistics for dashboard"""
        total_alerts = db.query(Alert).count()
        open_alerts = db.query(Alert).filter(Alert.status == "open").count()
        assigned_alerts = db.query(Alert).filter(Alert.status == "assigned").count()
        investigating_alerts = db.query(Alert).filter(Alert.status == "investigating").count()
        resolved_alerts = db.query(Alert).filter(Alert.status == "resolved").count()
        closed_alerts = db.query(Alert).filter(Alert.status == "closed").count()
        
        return {
            "total_alerts": total_alerts,
            "open_alerts": open_alerts,
            "assigned_alerts": assigned_alerts,
            "investigating_alerts": investigating_alerts,
            "resolved_alerts": resolved_alerts,
            "closed_alerts": closed_alerts
        }

# Create service instance
alert_service = AlertService()
