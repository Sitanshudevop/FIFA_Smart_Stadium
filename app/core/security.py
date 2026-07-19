import re

def sanitize_user_input(text: str) -> str:
    # Strip markdown escapes
    text = text.replace('\\', '')
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Truncate aggressively to prevent buffer overflow/prompt bomb attacks
    text = text[:500]
    
    # Neutralize injection payloads
    injection_patterns = [
        r"(?i)ignore previous",
        r"(?i)override",
        r"(?i)system prompt",
        r"(?i)bypass"
    ]
    
    flagged = False
    for pattern in injection_patterns:
        if re.search(pattern, text):
            flagged = True
            text = re.sub(pattern, "[REDACTED]", text)
            
    return text, flagged
