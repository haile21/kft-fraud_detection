# services/tin_service.py
import requests
import os
from typing import Dict, Optional, Tuple
from datetime import datetime

class TINService:
    """TIN verification service using real trade ministry API"""
    
    def __init__(self):
        # Real trade ministry API configuration
        self.ethrade_username = 'fast_etrade'
        self.ethrade_password = 'etrade_data'
        self.ethrade_url = "https://lmgrctnqmzbh52gs2fy6swvvgi0zsjfc.lambda-url.us-east-1.on.aws"
        self.timeout = int(os.getenv("TIN_API_TIMEOUT", "30"))
        
        # Headers for API requests
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "FraudManagementSystem/1.0"
        }
    
    def verify_tin_with_ministry(self, tin_number: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Verify TIN with real trade ministry API (eTrade)
        
        Returns:
            Tuple[bool, Optional[Dict], str]: (is_valid, tin_data, message)
        """
        try:
            # Prepare request payload for eTrade API
            payload = {
                "username": self.ethrade_username,
                "password": self.ethrade_password,
                "tin_number": tin_number
            }
            
            # Call real trade ministry API
            response = requests.post(
                self.ethrade_url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if TIN was found in the response
                if data.get('success', False) and data.get('data'):
                    return True, data.get('data'), "TIN verified successfully with eTrade"
                else:
                    return False, None, data.get('message', 'TIN not found in eTrade database')
            
            elif response.status_code == 401:
                return False, None, "eTrade API authentication failed"
            
            elif response.status_code == 404:
                return False, None, "TIN not found in eTrade database"
            
            else:
                return False, None, f"eTrade API error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return False, None, "eTrade API request timeout"
        except requests.exceptions.ConnectionError:
            return False, None, "Unable to connect to eTrade API"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    def cross_verify_tin_name(self, tin_number: str, provided_name: str) -> Tuple[bool, str]:
        """
        Cross-verify TIN with provided name using real eTrade data
        """
        is_valid, tin_data, message = self.verify_tin_with_ministry(tin_number)
        
        if not is_valid:
            return False, f"TIN verification failed: {message}"
        
        # Extract registered name from eTrade API response
        # The actual field name may vary based on eTrade API response structure
        registered_name = (
            tin_data.get('business_name') or 
            tin_data.get('company_name') or 
            tin_data.get('entity_name') or 
            tin_data.get('name', '')
        ).strip()
        
        if not registered_name:
            return False, "No business name found for this TIN in eTrade database"
        
        # Use fuzzy matching for name comparison
        from fuzzywuzzy import fuzz
        
        similarity = fuzz.ratio(
            registered_name.lower(), 
            provided_name.lower()
        )
        
        if similarity >= 85:  # 85% similarity threshold
            return True, f"TIN name matches with {similarity}% similarity (eTrade: '{registered_name}')"
        else:
            return False, f"TIN name mismatch: eTrade has '{registered_name}', provided '{provided_name}' (only {similarity}% similar)"
    
    def get_tin_details(self, tin_number: str) -> Optional[Dict]:
        """Get full TIN details from trade ministry"""
        is_valid, tin_data, message = self.verify_tin_with_ministry(tin_number)
        if is_valid:
            return tin_data
        return None
    
    def check_tin_status(self, tin_number: str) -> Tuple[bool, str]:
        """Check if TIN is active/valid"""
        is_valid, tin_data, message = self.verify_tin_with_ministry(tin_number)
        
        if not is_valid:
            return False, message
        
        # Check if TIN is active (not suspended/cancelled)
        status = tin_data.get('status', '').lower()
        if status in ['active', 'valid', 'registered']:
            return True, "TIN is active"
        else:
            return False, f"TIN is {status}"

# Global instance
tin_service = TINService()
