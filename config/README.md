# Configuration Guide

## Environment Variables

Create a `.env` file in the root directory with the following variables:

### Database Configuration
```bash
DATABASE_URL=postgresql://fraud_user:kft_123@localhost:5432/fraud_db
```

### TIN API Configuration (eTrade - Trade Ministry)
```bash
# Real eTrade API credentials (already configured in code)
# Username: fast_etrade
# Password: etrade_data
# URL: https://lmgrctnqmzbh52gs2fy6swvvgi0zsjfc.lambda-url.us-east-1.on.aws
TIN_API_TIMEOUT=30
```

### NID Service Configuration
```bash
NID_SIMULATION_MODE=true  # Set to false for production with real NID API
```

### Fraud Detection Configuration
```bash
FRAUD_RISK_THRESHOLD=0.7
NAME_SIMILARITY_THRESHOLD=85
```

## API Configuration

### TIN API Setup
1. Contact the trade ministry to get API credentials
2. Set `TIN_API_KEY` with your API key
3. Configure `TIN_API_BASE_URL` if different from default
4. Set appropriate timeout for your network

### NID Service
- Currently uses simulated data for testing
- Set `NID_SIMULATION_MODE=false` when real NID API is available
- Configure real NID API endpoints when available
