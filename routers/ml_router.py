# routers/ml_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from database import SessionLocal
from services.ml_fraud_detector import ml_fraud_detector
from services.user_service import user_service

# Create router
router = APIRouter(prefix="/ml", tags=["AI Fraud Detection"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication dependency (simplified for now)
def get_current_user_id() -> int:
    # In a real implementation, this would extract user ID from JWT token
    return 1

# Schemas
class VFeature(BaseModel):
    value: float

class TransactionInput(BaseModel):
    V: List[float] = Field(..., description="List of 28 V features")
    Time: float = Field(0.0, description="Transaction time")
    Amount: float = Field(..., description="Transaction amount")
    
    class Config:
        schema_extra = {
            "example": {
                "V": [0.0] * 28,
                "Time": 0.0,
                "Amount": 100.0
            }
        }

class MLPredictionResponse(BaseModel):
    is_fraud: bool
    is_anomaly: bool
    anomaly_score: float
    risk_level: str
    explanation: str
    confidence: str
    transaction_index: int

class MLBatchRequest(BaseModel):
    transactions: List[TransactionInput]

class MLBatchResponse(BaseModel):
    predictions: List[MLPredictionResponse]

class FraudDecisionRequest(BaseModel):
    amount: float
    user_id: int
    transaction_time: Optional[float] = 0.0
    v_features: Optional[List[float]] = None

class FraudDecisionResponse(BaseModel):
    decision: str  # "allow" or "block"
    fraud_risk: str  # "Low", "Medium", "High", "Critical"
    anomaly_score: float
    explanation: str
    recommendation: str

@router.post("/predict", response_model=MLPredictionResponse)
def predict_fraud_single(transaction: TransactionInput):
    """
    Predict fraud for a single transaction using AI/ML model
    
    This endpoint uses the trained machine learning model to detect fraud
    based on transaction patterns and features.
    
    **Features:**
    - 28 V features (PCA-transformed features)
    - Transaction amount
    - Transaction time
    
    **Example Request:**
    ```json
    {
      "V": [0.0, 0.0, 0.0, ...],
      "Time": 0.0,
      "Amount": 1000.0
    }
    ```
    
    **Example Response:**
    ```json
    {
      "is_fraud": false,
      "is_anomaly": false,
      "anomaly_score": 0.25,
      "risk_level": "Low",
      "explanation": "AI detected normal transaction (score: 0.2500)",
      "confidence": "High"
    }
    ```
    """
    try:
        # Prepare transaction data
        transaction_data = {
            "V": transaction.V,
            "Time": transaction.Time,
            "Amount": transaction.Amount
        }
        
        # Get ML prediction
        is_fraud, anomaly_score, explanation = ml_fraud_detector.predict_fraud(transaction_data)
        
        # Calculate risk level
        risk_level = ml_fraud_detector.calculate_risk_level(anomaly_score)
        
        # Determine confidence based on anomaly score
        if anomaly_score < 0.25 or anomaly_score > 0.75:
            confidence = "High"
        elif anomaly_score < 0.50 or anomaly_score > 0.60:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return MLPredictionResponse(
            is_fraud=is_fraud,
            is_anomaly=is_fraud,
            anomaly_score=round(anomaly_score, 4),
            risk_level=risk_level,
            explanation=explanation,
            confidence=confidence,
            transaction_index=0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing ML prediction: {str(e)}"
        )

@router.post("/predict/batch", response_model=MLBatchResponse)
def predict_fraud_batch(batch_request: MLBatchRequest):
    """
    Predict fraud for multiple transactions at once using AI/ML model
    
    This endpoint processes multiple transactions in a single request.
    
    **Example Request:**
    ```json
    {
      "transactions": [
        {
          "V": [0.0, 0.0, 0.0, ...],
          "Time": 0.0,
          "Amount": 1000.0
        },
        {
          "V": [0.0, 0.0, 0.0, ...],
          "Time": 10.0,
          "Amount": 5000.0
        }
      ]
    }
    ```
    """
    try:
        # Prepare transaction data
        transactions = []
        for tx in batch_request.transactions:
            transactions.append({
                "V": tx.V,
                "Time": tx.Time,
                "Amount": tx.Amount
            })
        
        # Get ML predictions
        predictions = ml_fraud_detector.predict_batch(transactions)
        
        # Format response
        formatted_predictions = []
        for pred in predictions:
            risk_level = ml_fraud_detector.calculate_risk_level(pred["anomaly_score"])
            
            if pred["anomaly_score"] < 0.25 or pred["anomaly_score"] > 0.75:
                confidence = "High"
            elif pred["anomaly_score"] < 0.50 or pred["anomaly_score"] > 0.60:
                confidence = "Medium"
            else:
                confidence = "Low"
            
            formatted_predictions.append(
                MLPredictionResponse(
                    is_fraud=pred["is_fraud"],
                    is_anomaly=pred["is_fraud"],
                    anomaly_score=round(pred["anomaly_score"], 4),
                    risk_level=risk_level,
                    explanation=pred["explanation"],
                    confidence=confidence,
                    transaction_index=pred.get("transaction_index", 0)
                )
            )
        
        return MLBatchResponse(predictions=formatted_predictions)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing batch ML predictions: {str(e)}"
        )

@router.post("/decision", response_model=FraudDecisionResponse)
def get_fraud_decision(
    request: FraudDecisionRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get AI-based fraud decision for a transaction
    
    This endpoint combines AI fraud detection with business logic to provide
    a clear decision and recommendation.
    
    **Example Request:**
    ```json
    {
      "amount": 50000.0,
      "user_id": 1,
      "transaction_time": 0.0
    }
    ```
    
    **Example Response:**
    ```json
    {
      "decision": "allow",
      "fraud_risk": "Low",
      "anomaly_score": 0.25,
      "explanation": "AI detected normal transaction",
      "recommendation": "Transaction approved - No fraud detected"
    }
    ```
    """
    try:
        # Prepare transaction data
        transaction_data = ml_fraud_detector.create_transaction_features(
            amount=request.amount,
            time=request.transaction_time,
            v_features=request.v_features
        )
        
        # Get ML prediction
        is_fraud, anomaly_score, explanation = ml_fraud_detector.predict_fraud(transaction_data)
        
        # Calculate risk level
        risk_level = ml_fraud_detector.calculate_risk_level(anomaly_score)
        
        # Make decision
        if is_fraud or risk_level in ["High", "Critical"]:
            decision = "block"
            recommendation = f"Transaction blocked - {risk_level} fraud risk detected"
        elif risk_level == "Medium":
            decision = "review"
            recommendation = f"Transaction requires manual review - {risk_level} fraud risk"
        else:
            decision = "allow"
            recommendation = "Transaction approved - Low fraud risk"
        
        return FraudDecisionResponse(
            decision=decision,
            fraud_risk=risk_level,
            anomaly_score=round(anomaly_score, 4),
            explanation=explanation,
            recommendation=recommendation
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting fraud decision: {str(e)}"
        )

@router.get("/health")
def ml_health_check():
    """
    Check if the ML fraud detection service is available
    
    Returns the status of the ML endpoint connectivity.
    """
    try:
        # Try a simple prediction to test connectivity
        test_transaction = ml_fraud_detector.create_transaction_features(
            amount=0.0,
            time=0.0
        )
        
        is_fraud, anomaly_score, explanation = ml_fraud_detector.predict_fraud(test_transaction)
        
        return {
            "status": "healthy",
            "ml_endpoint": ml_fraud_detector.ml_endpoint,
            "connectivity": "OK",
            "message": "ML fraud detection service is operational"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "ml_endpoint": ml_fraud_detector.ml_endpoint,
            "connectivity": "ERROR",
            "message": f"ML fraud detection service is unavailable: {str(e)}"
        }
