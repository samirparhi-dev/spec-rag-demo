from guardrails import Guard
from guardrails.validators import (
    RegexMatch,
    DetectPII,
    RestrictToTopic,
    ToxicLanguage
)

# Input guardrail: Sanitize user queries
input_guard = Guard.from_string(
    validators=[
        DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "AWS_ACCESS_KEY"]),
        RestrictToTopic(valid_topics=["kubernetes", "devops", "security", "networking"]),
        ToxicLanguage()
    ],
    description="Validate user input before sending to LLM"
)

# Output guardrail: Prevent data leaks
output_guard = Guard.from_string(
    validators=[
        DetectPII(pii_entities=["API_KEY", "PASSWORD", "SECRET"]),
        RegexMatch(
            regex=r"(ghp|gho|gitlab)_[A-Za-z0-9]{20,}",
            match_type="none",
            on_fail="fix"  # Redact tokens
        )
    ],
    description="Sanitize LLM output before showing to user"
)

def validate_query(user_input):
    result = input_guard.validate(user_input)
    if not result.validation_passed:
        raise ValueError(f"Input validation failed: {result.error}")
    return result.validated_output

def validate_response(llm_output):
    result = output_guard.validate(llm_output)
    if not result.validation_passed:
        # Redact sensitive data
        return result.validated_output.replace_sensitive_data("[REDACTED]")
    return llm_output