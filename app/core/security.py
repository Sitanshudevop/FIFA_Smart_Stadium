import re


def sanitize_user_input(text: str) -> str:
    """
    Sanitize and validate user input.
    
    Args:
        text (str): The raw input string.
        
    Returns:
        str: The sanitized output string.
    """
    # Strip markdown escapes
    text = text.replace("\\", "")

    # Exclude base64 strings from aggressive truncation
    is_base64_image = (
        text.startswith("data:image/")
        or text.startswith("/9j/")
        or text.startswith("iVBORw0K")
    )

    if not is_base64_image:
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        # Truncate aggressively to prevent buffer overflow/prompt bomb attacks
        text = text[:500]

    # Neutralize injection payloads
    injection_patterns = [
        r"(?i)ignore previous",
        r"(?i)override",
        r"(?i)system prompt",
        r"(?i)bypass",
    ]

    flagged = False
    for pattern in injection_patterns:
        if re.search(pattern, text):
            flagged = True
            text = re.sub(pattern, "[REDACTED]", text)

    return text, flagged
