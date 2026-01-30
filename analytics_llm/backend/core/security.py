"""
Security utilities for enterprise-grade protection
"""
from fastapi import Response, Request
from typing import Dict
import secrets
import hashlib
import re

class SecurityHeaders:
    """Add security headers to responses"""
    
    @staticmethod
    def add_headers(response: Response) -> Response:
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class InputValidator:
    """Validate and sanitize user inputs"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, any]:
        """Validate password strength"""
        result = {"valid": True, "errors": []}
        
        if len(password) < 8:
            result["valid"] = False
            result["errors"].append("Password must be at least 8 characters")
        
        if not re.search(r'[A-Z]', password):
            result["valid"] = False
            result["errors"].append("Password must contain uppercase letter")
        
        if not re.search(r'[a-z]', password):
            result["valid"] = False
            result["errors"].append("Password must contain lowercase letter")
        
        if not re.search(r'\d', password):
            result["valid"] = False
            result["errors"].append("Password must contain digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["valid"] = False
            result["errors"].append("Password must contain special character")
        
        return result
    
    @staticmethod
    def sanitize_sql_input(input_str: str) -> str:
        """Sanitize input to prevent SQL injection"""
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        sanitized = input_str
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        return sanitized


def mask_pii(df):
    """Mask PII in dataframes"""
    for col in df.columns:
        if "email" in col.lower():
            df[col] = "***MASKED***"
    return df


def mask_email(email: str) -> str:
    """Mask email for logging"""
    if '@' not in email:
        return "***"
    local, domain = email.split('@')
    if len(local) <= 2:
        masked_local = local[0] + '***'
    else:
        masked_local = local[0] + '***' + local[-1]
    return f"{masked_local}@{domain}"


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    return secrets.token_urlsafe(length)


# Global instances
input_validator = InputValidator()
