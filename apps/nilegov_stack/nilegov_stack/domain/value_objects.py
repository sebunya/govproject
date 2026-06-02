# Core Value Objects for NileGov Stack
# Digi-Verse Uganda Limited

import re
from nilegov_stack.domain.exceptions import InvalidNINException


class NIN:
    """Uganda National Identification Number (NIN) Value Object.
    
    Standard structure: 14 characters, starting with specific letters (CF or CM for Citizens).
    """
    def __init__(self, value: str):
        if not value:
            raise InvalidNINException("NIN value cannot be empty.")
            
        clean_value = value.strip().upper()
        if len(clean_value) != 14:
            raise InvalidNINException("NIN must be exactly 14 characters long.")
            
        # Basic validation: must match character class regex for Ugandan NINs
        # Usually: C followed by F/M/R/O, then 8 alphanumeric digits, then 4 alphabetic characters
        pattern = r"^[C][A-Z0-9]{13}$"
        if not re.match(pattern, clean_value):
            raise InvalidNINException(f"NIN structure '{clean_value}' is invalid.")
            
        self.value = clean_value

    def __eq__(self, other):
        if not isinstance(other, NIN):
            return False
        return self.value == other.value

    def __str__(self):
        return self.value


class Email:
    """Email address Value Object validating standard formatting."""
    def __init__(self, value: str):
        if not value:
            raise ValueError("Email address cannot be empty.")
            
        clean_value = value.strip().lower()
        # Basic regex check for standard format
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, clean_value):
            raise ValueError(f"Email address structure '{clean_value}' is invalid.")
            
        self.value = clean_value

    def __eq__(self, other):
        if not isinstance(other, Email):
            return False
        return self.value == other.value

    def __str__(self):
        return self.value


class PhoneNumber:
    """Ugandan phone number Value Object.
    
    Validates E.164 formatting or local prefix formats (e.g. +2567...).
    """
    def __init__(self, value: str):
        if not value:
            raise ValueError("Phone number cannot be empty.")
            
        clean_value = re.sub(r"\s+", "", value) # remove whitespace
        
        # Verify Ugandan mobile formats: e.g. +2567..., 2567..., or 07...
        pattern = r"^(?:\+?256|0)7[0-9]{8}$"
        if not re.match(pattern, clean_value):
            raise ValueError(f"Phone number format '{clean_value}' is invalid for Uganda.")
            
        self.value = clean_value

    def __eq__(self, other):
        if not isinstance(other, PhoneNumber):
            return False
        return self.value == other.value

    def __str__(self):
        return self.value
