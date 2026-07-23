import os
import json
import google.generativeai as genai
import config

def classify_emails(emails_list):
    """
    Classifies a list of email addresses as 'business' or 'individual' using Gemini API.
    If the API key is missing or calls fail, falls back to a heuristic rule-based classifier.
    """
    # Deduplicate
    emails_list = list(set(emails_list))
    if not emails_list:
        return {'business': [], 'individual': []}
        
    api_key = config.GEMINI_API_KEY
    if not api_key or api_key == 'your_gemini_api_key_here':
        # Fallback to local heuristic classifier if API key is not configured
        print("Gemini API key not set. Using heuristic fallback.")
        return heuristic_classify_emails(emails_list)
        
    try:
        genai.configure(api_key=api_key)
        # Using gemini-1.5-flash for fast and cost-efficient text classification
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
You are an AI assistant designed to classify email addresses into two categories: "business" or "individual".

Instructions:
- "business" emails are associated with companies, brands, domains, retailers, or wholesale institutions (e.g., contact@yogastudio.com, sales@soundhealing.org, info@lotuswellness.de).
- "individual" emails belong to personal, standard, or generic mail domains (like gmail.com, yahoo.com, hotmail.com, icloud.com, aol.com) UNLESS they contain clear business indicators in the local prefix, but generally label generic provider domains as "individual".
- Return the response strictly as a JSON object where keys are the email addresses and values are either "business" or "individual". Do not include markdown code block formatting (such as ```json) or any text other than the JSON object itself.

Emails to classify:
{json.dumps(emails_list)}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean response in case the model returns markdown code block formatting
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        classification = json.loads(text)
        
        business_emails = []
        individual_emails = []
        for email, label in classification.items():
            if label.strip().lower() == 'business':
                business_emails.append(email)
            else:
                individual_emails.append(email)
                
        # Handle any emails that were missed in the JSON response
        missed = set(emails_list) - set(classification.keys())
        if missed:
            missed_classified = heuristic_classify_emails(list(missed))
            business_emails.extend(missed_classified['business'])
            individual_emails.extend(missed_classified['individual'])
            
        return {'business': business_emails, 'individual': individual_emails}
        
    except Exception as e:
        print(f"Gemini API error: {e}. Falling back to heuristic classification.")
        return heuristic_classify_emails(emails_list)

def heuristic_classify_emails(emails_list):
    """
    Heuristic rule-based fallback classification when Gemini API is unavailable.
    """
    business = []
    individual = []
    
    generic_domains = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
        'icloud.com', 'mail.com', 'protonmail.com', 'zoho.com', 'yandex.com'
    }
    
    for email in emails_list:
        email = email.strip()
        parts = email.split('@')
        if len(parts) == 2:
            domain = parts[1].lower()
            if domain in generic_domains:
                individual.append(email)
            else:
                business.append(email)
        else:
            individual.append(email)
            
    return {'business': business, 'individual': individual}
