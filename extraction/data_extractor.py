import re
from validation.email_validator import is_valid_email

# Simple email regex for unstructured text extraction
EMAIL_REGEX_PATTERN = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

def extract_emails_from_text(text):
    """Find all potential email strings in unstructured text."""
    if not text:
        return []
    return re.findall(EMAIL_REGEX_PATTERN, text)

def parse_lead_from_raw_data(email, raw_snippet, platform_name):
    """
    Attempt to extract/infer buyer_name, company_name, website, country
    from raw snippet text surrounding the email.
    """
    email = email.strip()
    
    # Defaults
    buyer_name = "Proprietor"
    company_name = "Wellness Center"
    website = ""
    country = "Global"
    
    # Simple heuristic inference
    # Try to infer company name from email domain if not public domain
    public_domains = {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'icloud.com', 'mail.com'}
    parts = email.split('@')
    if len(parts) == 2:
        domain = parts[1].lower()
        if domain not in public_domains:
            domain_name = domain.split('.')[0]
            company_name = domain_name.replace('-', ' ').title()
            website = f"https://www.{domain}"
            
    # Parse snippets for Country
    country_keywords = {
        'USA': ['united states', 'usa', 'america', 'california', 'ny', 'texas', 'florida'],
        'UK': ['united kingdom', 'uk', 'london', 'england', 'scotland'],
        'Germany': ['germany', 'deutschland', 'berlin', 'munich'],
        'Australia': ['australia', 'sydney', 'melbourne', 'au'],
        'Canada': ['canada', 'toronto', 'vancouver', 'ca'],
        'France': ['france', 'paris'],
        'India': ['india', 'in', 'delhi', 'mumbai'],
        'Nepal': ['nepal', 'ktm', 'kathmandu']
    }
    
    snippet_lower = raw_snippet.lower()
    for country_name, keywords in country_keywords.items():
        if any(kw in snippet_lower for kw in keywords):
            country = country_name
            break
            
    # Try to find contact name in snippet
    name_match = re.search(r'(?:owner|contact|founder|name|manager|ceo|hi|hello)\s*(?:is|:|\-)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', raw_snippet)
    if name_match:
        buyer_name = name_match.group(1).title()
        
    return {
        'buyer_name': buyer_name,
        'company_name': company_name,
        'email': email,
        'website': website,
        'country': country,
        'source_platform': platform_name
    }
