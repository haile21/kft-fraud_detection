# services/ml_fraud_detector.py
import requests
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MLFraudDetector:
    def __init__(self):
        self.ml_endpoint = "http://3.216.34.218:8027/predict"
        self.timeout = 30  # seconds
    
    def predict_fraud(self, transaction_data: Dict) -> Tuple[bool, float, str]:
        """
        Predict fraud for a single transaction using ML model
        
        Args:
            transaction_data: Dictionary containing transaction features
                Expected keys: V (list of 28 features), Time, Amount
        
        Returns:
            Tuple of (is_fraud: bool, anomaly_score: float, explanation: str)
        """
        try:
            # Prepare request data
            request_data = {
                "transactions": [transaction_data]
            }
            
            # Call ML endpoint
            response = requests.post(
                self.ml_endpoint,
                json=request_data,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json"
                },
                timeout=self.timeout
            )
            
            # Check response status
            if response.status_code != 200:
                logger.error(f"ML endpoint returned status {response.status_code}: {response.text}")
                return False, 0.0, "ML model unavailable - using rule-based detection only"
            
            # Parse response
            result = response.json()
            
            if "predictions" not in result or len(result["predictions"]) == 0:
                logger.error("ML endpoint returned invalid response")
                return False, 0.0, "ML model returned invalid response"
            
            prediction = result["predictions"][0]
            is_fraud = prediction.get("is_anomaly", False)
            anomaly_score = prediction.get("anomaly_score", 0.0)
            transaction_index = prediction.get("transaction_index", 0)
            
            # Generate explanation
            if is_fraud:
                explanation = f"AI detected anomaly (score: {anomaly_score:.4f}) - Transaction pattern matches known fraud indicators"
            else:
                explanation = f"AI detected normal transaction (score: {anomaly_score:.4f}) - Customer activity appears legitimate"
            
            return is_fraud, anomaly_score, explanation
            
        except requests.exceptions.Timeout:
            logger.error("ML endpoint request timed out")
            return False, 0.0, "ML model timeout - using rule-based detection only"
        except requests.exceptions.RequestException as e:
            logger.error(f"ML endpoint request failed: {str(e)}")
            return False, 0.0, f"ML model unavailable: {str(e)}"
        except Exception as e:
            logger.error(f"Error calling ML endpoint: {str(e)}")
            return False, 0.0, f"ML model error: {str(e)}"
    
    def predict_batch(self, transactions: List[Dict]) -> List[Dict]:
        """
        Predict fraud for multiple transactions at once
        
        Args:
            transactions: List of transaction dictionaries
        
        Returns:
            List of prediction results with is_fraud, anomaly_score, and explanation
        """
        try:
            # Prepare request data
            request_data = {
                "transactions": transactions
            }
            
            # Call ML endpoint
            response = requests.post(
                self.ml_endpoint,
                json=request_data,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json"
                },
                timeout=self.timeout
            )
            
            # Check response status
            if response.status_code != 200:
                logger.error(f"ML endpoint returned status {response.status_code}: {response.text}")
                return []
            
            # Parse response
            result = response.json()
            
            if "predictions" not in result:
                logger.error("ML endpoint returned invalid response")
                return []
            
            predictions = []
            for pred in result["predictions"]:
                is_fraud = pred.get("is_anomaly", False)
                anomaly_score = pred.get("anomaly_score", 0.0)
                transaction_index = pred.get("transaction_index", 0)
                
                explanation = (
                    f"AI detected {'anomaly' if is_fraud else 'normal transaction'} "
                    f"(score: {anomaly_score:.4f})"
                )
                
                predictions.append({
                    "is_fraud": is_fraud,
                    "anomaly_score": anomaly_score,
                    "explanation": explanation,
                    "transaction_index": transaction_index
                })
            
            return predictions
            
        except requests.exceptions.Timeout:
            logger.error("ML endpoint request timed out")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"ML endpoint request failed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error calling ML endpoint: {str(e)}")
            return []
    
    def create_transaction_features(
        self,
        amount: float,
        time: float = 0.0,
        v_features: Optional[List[float]] = None
    ) -> Dict:
        """
        Create transaction features for ML model
        
        Args:
            amount: Transaction amount
            time: Transaction time (optional)
            v_features: List of 28 V features (if not provided, will use zeros)
        
        Returns:
            Dictionary with transaction features ready for ML endpoint
        """
        if v_features is None:
            # Use zeros as default for V features
            v_features = [0.0] * 28
        
        return {
            "V": v_features,
            "Time": time,
            "Amount": amount
        }
    
    def calculate_risk_level(self, anomaly_score: float) -> str:
        """
        Calculate fraud risk level based on anomaly score
        
        Args:
            anomaly_score: Anomaly score from ML model
        
        Returns:
            Risk level: "Low", "Medium", "High", or "Critical"
        """
        if anomaly_score < 0.25:
            return "Low"
        elif anomaly_score < 0.50:
            return "Medium"
        elif anomaly_score < 0.75:
            return "High"
        else:
            return "Critical"

# Create service instance
ml_fraud_detector = MLFraudDetector()
