import re
import random
from datetime import datetime, date
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from fuzzywuzzy import fuzz
from models import Identity, Blacklist

class NIDService:
    """National ID verification and management service"""
    
    def __init__(self):
        # NID format patterns for different countries (example: Ethiopian format)
        self.nid_patterns = {
            'ET': r'^\d{12}$',  # Ethiopian: 12 digits
            'KE': r'^\d{8}$',   # Kenyan: 8 digits  
            'NG': r'^\d{11}$',  # Nigerian: 11 digits
            'GH': r'^GHA-\d{9}-\d$',  # Ghanaian: GHA-123456789-1
        }
        
        # Fuzzy matching configuration
        self.name_similarity_threshold = 85  # Minimum similarity percentage for name matching
        self.strict_name_similarity_threshold = 95  # High confidence threshold
        
        # Simulated NID database with sample data
        self.simulated_nid_db = {
            '123456789012': {
                'name': 'Alemayehu Tsegaye',
                'date_of_birth': '1985-03-15',
                'gender': 'M',
                'place_of_birth': 'Addis Ababa',
                'father_name': 'Tsegaye Bekele',
                'mother_name': 'Marta Assefa',
                'issue_date': '2010-05-20',
                'expiry_date': '2030-05-20',
                'status': 'active',
                'photo_url': '/photos/1234567890.jpg'
            },
            '234567890123': {
                'name': 'Hirut Bekele',
                'date_of_birth': '1992-07-22',
                'gender': 'F', 
                'place_of_birth': 'Bahir Dar',
                'father_name': 'Bekele Assefa',
                'mother_name': 'Tigist Hailu',
                'issue_date': '2015-08-10',
                'expiry_date': '2035-08-10',
                'status': 'active',
                'photo_url': '/photos/234567890123.jpg'
            },
            '345678901234': {
                'name': 'Dawit Hailu',
                'date_of_birth': '1988-11-08',
                'gender': 'M',
                'place_of_birth': 'Mekelle',
                'father_name': 'Hailu Gebre',
                'mother_name': 'Aster Yohannes',
                'issue_date': '2012-12-01',
                'expiry_date': '2032-12-01',
                'status': 'expired',
                'photo_url': '/photos/345678901234.jpg'
            }
        }
    
    def validate_nid_format(self, nid: str, country_code: str = 'ET') -> bool:
        """Validate NID format based on country"""
        pattern = self.nid_patterns.get(country_code)
        if not pattern:
            return False
        return bool(re.match(pattern, nid.strip()))
    
    def fuzzy_name_match(self, nid_name: str, provided_name: str) -> Tuple[bool, str, int]:
        """
        Perform fuzzy name matching with multiple algorithms
        
        Returns:
            Tuple[bool, str, int]: (is_match, message, similarity_score)
        """
        # Normalize names for comparison
        nid_name_clean = nid_name.lower().strip()
        provided_name_clean = provided_name.lower().strip()
        
        # Try different fuzzy matching algorithms
        ratio_score = fuzz.ratio(nid_name_clean, provided_name_clean)
        partial_ratio = fuzz.partial_ratio(nid_name_clean, provided_name_clean)
        token_sort_ratio = fuzz.token_sort_ratio(nid_name_clean, provided_name_clean)
        token_set_ratio = fuzz.token_set_ratio(nid_name_clean, provided_name_clean)
        
        # Use the highest score from all algorithms
        max_similarity = max(ratio_score, partial_ratio, token_sort_ratio, token_set_ratio)
        
        # Determine match based on similarity thresholds
        if max_similarity >= self.strict_name_similarity_threshold:
            return True, f"Names match with high confidence ({max_similarity}% similarity)", max_similarity
        elif max_similarity >= self.name_similarity_threshold:
            return True, f"Names match with good confidence ({max_similarity}% similarity)", max_similarity
        else:
            return False, f"Names don't match (only {max_similarity}% similar). NID has '{nid_name}', provided '{provided_name}'", max_similarity
    
    def verify_nid_with_government_db(self, nid: str) -> Tuple[bool, Optional[Dict]]:
        """Simulate government NID database verification"""
        nid_clean = nid.strip()
        
        # Check if NID exists in simulated database
        if nid_clean in self.simulated_nid_db:
            nid_data = self.simulated_nid_db[nid_clean]
            
            # Check if NID is expired
            if nid_data['status'] == 'expired':
                return False, {
                    'error': 'NID expired',
                    'expiry_date': nid_data['expiry_date'],
                    'details': nid_data
                }
            
            return True, nid_data
        
        return False, {'error': 'NID not found in government database'}
    
    def cross_verify_kyc_data(self, nid: str, provided_name: str, 
                             provided_dob: str = None, provided_gender: str = None) -> Tuple[bool, str]:
        """Cross-verify provided KYC data with NID database"""
        is_valid, nid_data = self.verify_nid_with_government_db(nid)
        
        if not is_valid:
            return False, "NID verification failed"
        
        # Use fuzzy name matching instead of exact matching
        name_match, name_message, similarity_score = self.fuzzy_name_match(
            nid_data['name'], provided_name
        )
        
        if not name_match:
            return False, name_message
        
        # Check date of birth if provided
        if provided_dob and nid_data['date_of_birth'] != provided_dob:
            return False, f"DOB mismatch: NID has '{nid_data['date_of_birth']}', provided '{provided_dob}'"
        
        # Check gender if provided
        if provided_gender and nid_data['gender'] != provided_gender.upper():
            return False, f"Gender mismatch: NID has '{nid_data['gender']}', provided '{provided_gender}'"
        
        return True, f"KYC data matches NID. {name_message}"
    
    def check_nid_blacklist(self, db: Session, nid: str) -> Tuple[bool, Optional[str]]:
        """Check if NID is blacklisted"""
        blacklist_entry = db.query(Blacklist).filter(Blacklist.national_id == nid).first()
        if blacklist_entry:
            return True, blacklist_entry.reason
        return False, None
    
    def get_nid_details(self, nid: str) -> Optional[Dict]:
        """Get full NID details for display"""
        is_valid, nid_data = self.verify_nid_with_government_db(nid)
        if is_valid:
            return nid_data
        return None
    
    def generate_fake_nid(self, country_code: str = 'ET') -> str:
        """Generate a fake NID for testing purposes"""
        if country_code == 'ET':
            return str(random.randint(100000000000, 999999999999))  # 12 digits
        elif country_code == 'KE':
            return str(random.randint(10000000, 99999999))  # 8 digits
        elif country_code == 'NG':
            return str(random.randint(10000000000, 99999999999))  # 11 digits
        elif country_code == 'GH':
            return f"GHA-{random.randint(100000000, 999999999)}-{random.randint(1, 9)}"
        return ""

# Global instance
nid_service = NIDService()
