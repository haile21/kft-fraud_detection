# ML Fraud Detection API - Frontend Integration Guide

## Overview

The AI Fraud Detection API provides machine learning-based fraud detection capabilities. This API allows your frontend to get AI-generated fraud scores and decisions for transactions.

## Base URL
```
http://localhost:8000/ml
```

## Key Endpoints

### 1. Single Transaction Prediction
**Endpoint**: `POST /ml/predict`

Predict fraud for a single transaction using AI/ML model.

**Request:**
```json
{
  "V": [0.0, 0.0, 0.0, ...],  // 28 features
  "Time": 0.0,
  "Amount": 1000.0
}
```

**Response:**
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

**Risk Levels:**
- `Low`: anomaly_score < 0.25
- `Medium`: 0.25 ≤ anomaly_score < 0.50
- `High`: 0.50 ≤ anomaly_score < 0.75
- `Critical`: anomaly_score ≥ 0.75

### 2. Batch Transaction Prediction
**Endpoint**: `POST /ml/predict/batch`

Predict fraud for multiple transactions at once.

**Request:**
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

### 3. Fraud Decision with Business Logic
**Endpoint**: `POST /ml/decision`

Get AI-based fraud decision with recommendation.

**Request:**
```json
{
  "amount": 50000.0,
  "user_id": 1,
  "transaction_time": 0.0
}
```

**Response:**
```json
{
  "decision": "allow",
  "fraud_risk": "Low",
  "anomaly_score": 0.25,
  "explanation": "AI detected normal transaction",
  "recommendation": "Transaction approved - Low fraud risk"
}
```

**Decision Values:**
- `allow`: Transaction approved
- `block`: Transaction blocked
- `review`: Manual review required

### 4. Health Check
**Endpoint**: `GET /ml/health`

Check if ML fraud detection service is available.

**Response:**
```json
{
  "status": "healthy",
  "ml_endpoint": "http://3.216.34.218:8027/predict",
  "connectivity": "OK",
  "message": "ML fraud detection service is operational"
}
```

## Frontend Integration Examples

### React Example

```jsx
import React, { useState } from 'react';

const FraudDetectionComponent = () => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const checkFraud = async (transactionData) => {
    setLoading(true);
    try {
      const response = await fetch('/ml/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(transactionData)
      });
      
      const data = await response.json();
      setPrediction(data);
    } catch (error) {
      console.error('Error checking fraud:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => checkFraud({
        V: [0.0] * 28,
        Time: 0.0,
        Amount: 1000.0
      })}>
        Check Transaction
      </button>
      
      {loading && <p>Analyzing transaction...</p>}
      
      {prediction && (
        <div>
          <h3>Fraud Detection Result</h3>
          <p>Risk Level: {prediction.risk_level}</p>
          <p>Anomaly Score: {prediction.anomaly_score}</p>
          <p>Decision: {prediction.is_fraud ? 'FRAUD DETECTED' : 'NO FRAUD'}</p>
          <p>Explanation: {prediction.explanation}</p>
        </div>
      )}
    </div>
  );
};

export default FraudDetectionComponent;
```

 
## UI Components Suggestions

### 1. Fraud Risk Badge Component
Display the fraud risk level with appropriate color coding:
- **Low**: Green badge
- **Medium**: Yellow badge
- **High**: Orange badge
- **Critical**: Red badge

### 2. Anomaly Score Gauge
Visual gauge showing the anomaly score (0-1 scale).

### 3. AI Explanation Card
Display the explanation text in an expandable card.

### 4. Decision Status Banner
Show the decision (allow/block/review) prominently at the top.

### 5. Real-time Testing Interface
Allow users to test the AI model with sample transactions.

## Integration with Existing Fraud Detection

The AI fraud detection can be used alongside the existing rule-based system:

1. **Rule-based Detection**: Checks against predefined fraud rules
2. **AI-based Detection**: Uses ML to detect complex patterns
3. **Combined Decision**: Final decision considers both systems

## Error Handling

```javascript
try {
  const prediction = await mlService.checkSingleTransaction(transaction);
  
  if (prediction.is_fraud) {
    showAlert('Fraud detected by AI');
  }
} catch (error) {
  // Handle ML service unavailability
  console.error('ML service unavailable:', error);
  // Fall back to rule-based detection
}
```

## Best Practices

1. **Caching**: Cache health check results to avoid frequent calls
2. **Loading States**: Show loading indicators while waiting for predictions
3. **Error Boundaries**: Handle cases where ML service is unavailable
4. **User Feedback**: Provide clear explanations of AI decisions
5. **Fallback**: Always have a fallback when ML service is down

## Testing Tips

1. Use the `/ml/health` endpoint to verify service availability
2. Test with various transaction amounts and patterns
3. Verify that risk levels are displayed correctly
4. Test error handling when ML endpoint is unavailable


