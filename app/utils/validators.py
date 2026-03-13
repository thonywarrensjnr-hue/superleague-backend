import re
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """Utility class for input validation"""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email format and domain"""
        # Basic format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "Invalid email format"

        # Check for common disposable email domains
        disposable_domains = ['tempmail.com', 'throwaway.com', 'mailinator.com']
        domain = email.split('@')[1].lower()
        if domain in disposable_domains:
            return False, "Please use a permanent email address"

        return True, None

    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input by removing dangerous characters"""
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        # Remove SQL injection attempts
        text = re.sub(r'(\-\-)|(\;)|(\|\|)|(DROP)|(SELECT)|(INSERT)|(DELETE)', '', text, flags=re.IGNORECASE)
        # Truncate
        if len(text) > max_length:
            text = text[:max_length]
        return text.strip()

    @staticmethod
    def is_rate_limited(ip: str, email: str, redis_client=None) -> bool:
        """Check if request is rate limited"""
        # This would check Redis for rate limiting
        # Return True if rate limited, False otherwise
        return False


class DataSanitizer:
    """Data sanitization utilities"""

    @staticmethod
    def sanitize_user_data(data: dict) -> dict:
        """Remove sensitive or unnecessary fields"""
        sensitive_fields = ['password', 'credit_card', 'ssn']
        return {k: v for k, v in data.items() if k.lower() not in sensitive_fields}

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email for privacy (e.g., j***@example.com)"""
        if '@' not in email:
            return email
        local, domain = email.split('@')
        if len(local) <= 2:
            masked_local = local[0] + '*' * len(local[1:])
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"