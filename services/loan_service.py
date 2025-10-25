# services/loan_service.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from models import Loan, LoanApplication, User

class LoanService:
    """Loan management service"""
    
    def __init__(self):
        pass
    
    def has_active_loan(self, db: Session, user_id: int) -> bool:
        """Check if user has any active loans"""
        active_loans = db.query(Loan).filter(
            Loan.user_id == user_id,
            Loan.status.in_(['active', 'approved']),
            Loan.is_active == True
        ).count()
        
        return active_loans > 0
    
    def get_user_loans(self, db: Session, user_id: int) -> List[Loan]:
        """Get all loans for a user"""
        return db.query(Loan).filter(Loan.user_id == user_id).all()
    
    def get_active_loans(self, db: Session, user_id: int) -> List[Loan]:
        """Get active loans for a user"""
        return db.query(Loan).filter(
            Loan.user_id == user_id,
            Loan.status.in_(['active', 'approved']),
            Loan.is_active == True
        ).all()
    
    def get_recent_applications(self, db: Session, user_id: int, days: int = 30) -> List[LoanApplication]:
        """Get recent loan applications for a user"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return db.query(LoanApplication).filter(
            LoanApplication.user_id == user_id,
            LoanApplication.application_date >= cutoff_date
        ).order_by(LoanApplication.application_date.desc()).all()
    
    def get_applications_today(self, db: Session, user_id: int) -> int:
        """Get count of applications made today"""
        today = datetime.now().date()
        return db.query(LoanApplication).filter(
            LoanApplication.user_id == user_id,
            LoanApplication.application_date >= datetime.combine(today, datetime.min.time())
        ).count()
    
    def get_applications_within_hours(self, db: Session, user_id: int, hours: int = 24) -> List[LoanApplication]:
        """Get applications within specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return db.query(LoanApplication).filter(
            LoanApplication.user_id == user_id,
            LoanApplication.application_date >= cutoff_time
        ).order_by(LoanApplication.application_date.desc()).all()
    
    def create_loan_application(self, db: Session, user_id: int, amount: float, 
                              purpose: str = None, employment_status: str = None,
                              monthly_income: float = None, ip_address: str = None,
                              user_agent: str = None) -> LoanApplication:
        """Create a new loan application"""
        application = LoanApplication(
            user_id=user_id,
            application_amount=amount,
            loan_purpose=purpose,
            employment_status=employment_status,
            monthly_income=monthly_income,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        return application
    
    def approve_loan_application(self, db: Session, application_id: int, 
                               interest_rate: float, loan_term_months: int) -> Optional[Loan]:
        """Approve a loan application and create a loan"""
        application = db.query(LoanApplication).filter(
            LoanApplication.id == application_id
        ).first()
        
        if not application:
            return None
        
        # Create loan
        loan = Loan(
            user_id=application.user_id,
            loan_amount=application.application_amount,
            loan_purpose=application.loan_purpose,
            interest_rate=interest_rate,
            loan_term_months=loan_term_months,
            status='approved',
            approval_date=datetime.now(),
            monthly_payment=self._calculate_monthly_payment(
                application.application_amount, 
                interest_rate, 
                loan_term_months
            ),
            remaining_balance=application.application_amount
        )
        
        db.add(loan)
        
        # Update application status
        application.status = 'approved'
        application.loan_id = loan.id
        
        db.commit()
        db.refresh(loan)
        return loan
    
    def reject_loan_application(self, db: Session, application_id: int, reason: str):
        """Reject a loan application"""
        application = db.query(LoanApplication).filter(
            LoanApplication.id == application_id
        ).first()
        
        if application:
            application.status = 'rejected'
            application.rejection_reason = reason
            db.commit()
    
    def close_loan(self, db: Session, loan_id: int):
        """Close a loan"""
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if loan:
            loan.status = 'closed'
            loan.closure_date = datetime.now()
            loan.is_active = False
            loan.remaining_balance = 0
            db.commit()
    
    def _calculate_monthly_payment(self, principal: float, interest_rate: float, 
                                 term_months: int) -> float:
        """Calculate monthly payment using standard formula"""
        if interest_rate == 0:
            return principal / term_months
        
        monthly_rate = interest_rate / 100 / 12
        return principal * (monthly_rate * (1 + monthly_rate) ** term_months) / \
               ((1 + monthly_rate) ** term_months - 1)

# Global instance
loan_service = LoanService()
