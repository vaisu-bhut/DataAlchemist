import re
from typing import Dict, List

class PIIRedactor:
    """Simple PII redaction service"""
    
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        }
        
        self.replacements = {
            'email': '[EMAIL_REDACTED]',
            'phone': '[PHONE_REDACTED]',
            'ssn': '[SSN_REDACTED]',
            'credit_card': '[CARD_REDACTED]',
            'ip_address': '[IP_REDACTED]'
        }
    
    def redact_text(self, text: str) -> str:
        """Redact PII from text"""
        redacted_text = text
        
        for pii_type, pattern in self.patterns.items():
            replacement = self.replacements[pii_type]
            redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)
        
        return redacted_text
    
    def redact_conversation(self, conversation_data: Dict) -> Dict:
        """Redact PII from entire conversation"""
        redacted = conversation_data.copy()
        
        # Redact messages
        if 'messages' in redacted:
            for message in redacted['messages']:
                if 'content' in message:
                    message['content'] = self.redact_text(message['content'])
        
        # Redact metadata if present
        if 'metadata' in redacted:
            for key, value in redacted['metadata'].items():
                if isinstance(value, str):
                    redacted['metadata'][key] = self.redact_text(value)
        
        return redacted