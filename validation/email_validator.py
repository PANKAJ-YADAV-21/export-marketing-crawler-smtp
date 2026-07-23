import re

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff')

def is_valid_email(email):
    """
    Validate email based on syntax, length constraints, and file extension checks.
    """
    if not email:
        return False
    
    email = email.strip()
    
    # 1. Regex check for standard email format
    if not re.match(EMAIL_REGEX, email):
        return False
        
    # 2. Check if it ends with an image extension (which might be matched by generic regex in HTML parsing)
    if email.lower().endswith(IMAGE_EXTENSIONS):
        return False
        
    # 3. Check domain length (Section 12.1 Algorithm)
    try:
        parts = email.split('@')
        if len(parts) == 2:
            domain = parts[1]
            if len(domain) > 50:
                return False
    except Exception:
        return False
        
    return True
