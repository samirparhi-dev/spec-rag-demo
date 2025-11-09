from typing import Optional
import re

class Filter:
    def __init__(self):
        self.name = "MLSecOps Guardrails"
        
        # Sensitive patterns to redact
        self.patterns = [
            (r'Bearer [A-Za-z0-9\-._~+/]+=*', '[REDACTED_TOKEN]'),
            (r'password["\s:=]+[^\s"]+', 'password=[REDACTED]'),
            (r'(ghp|gho|gitlab)_[A-Za-z0-9]{20,}', '[REDACTED_PAT]'),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]'),
            (r'(JWT|jwt)[-_]?[sS]ecret["\s:=]+[^\s"]+', 'jwt_secret=[REDACTED]')
        ]
    
    def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """Validate and sanitize user input"""
        messages = body.get("messages", [])
        
        # Check for prompt injection attempts
        for msg in messages:
            content = msg.get("content", "")
            if any(keyword in content.lower() for keyword in ["ignore previous", "disregard", "system prompt"]):
                raise ValueError("Potential prompt injection detected")
        
        return body
    
    def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """Sanitize LLM output"""
        messages = body.get("messages", [])
        
        for msg in messages:
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                
                # Redact sensitive data
                for pattern, replacement in self.patterns:
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                
                msg["content"] = content
        
        return body