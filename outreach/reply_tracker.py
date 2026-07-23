import imaplib
import email
from email.header import decode_header
import google.generativeai as genai
import config

def analyze_reply_sentiment(reply_text):
    """
    Use Gemini AI to classify reply sentiment into: Positive, Neutral, or Unsubscribe.
    """
    api_key = config.GEMINI_API_KEY
    if not api_key or api_key == 'your_gemini_api_key_here':
        return heuristic_sentiment_analysis(reply_text)
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
Analyze the following email response from a prospective B2B buyer and classify it into one of these three categories:
1. "Positive" (e.g., they ask for pricing, catalogs, want to hop on a call, express interest).
2. "Neutral" (e.g., out of office, asking to contact later, asking general unrelated questions).
3. "Unsubscribe" (e.g., "do not contact", "remove me", "not interested").

Return ONLY the single word: "Positive", "Neutral", or "Unsubscribe". Do not include quotes, punctuation, or explanations.

Email body:
{reply_text}
"""
        response = model.generate_content(prompt)
        sentiment = response.text.strip().replace('"', '').replace("'", "")
        if sentiment in ["Positive", "Neutral", "Unsubscribe"]:
            return sentiment
        return "Neutral"
    except Exception as e:
        print(f"Gemini sentiment error: {e}")
        return heuristic_sentiment_analysis(reply_text)

def heuristic_sentiment_analysis(text):
    """Fallback sentiment checker."""
    text_lower = text.lower()
    
    # Check for unsubscribe keywords
    unsub_keywords = ['remove', 'unsubscribe', 'not interested', 'stop', 'do not contact', 'delete', 'please stop']
    if any(kw in text_lower for kw in unsub_keywords):
        return "Unsubscribe"
        
    # Check for positive keywords
    pos_keywords = ['price', 'pricing', 'catalog', 'wholesale', 'interested', 'call', 'meeting', 'send details', 'quote', 'cost']
    if any(kw in text_lower for kw in pos_keywords):
        return "Positive"
        
    return "Neutral"

def fetch_email_replies(user_email=None, app_password=None):
    """
    Checks Gmail Inbox via IMAP for replies.
    Returns list of reply objects.
    Falls back to mock replies if credentials aren't set or connection fails.
    """
    email_addr = user_email or config.GMAIL_EMAIL
    password = app_password or config.GMAIL_APP_PASSWORD
    
    replies = []
    
    # 1. Attempt live IMAP fetch if credentials are configured
    if email_addr and password and email_addr != 'your_gmail_address@gmail.com':
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(email_addr, password)
            mail.select("inbox")
            
            # Search for unread emails or replies
            status, messages = mail.search(None, 'UNSEEN')
            if status == "OK" and messages[0]:
                for num in messages[0].split()[-10:]: # Limit to last 10 emails
                    status, data = mail.fetch(num, "(RFC822)")
                    if status != "OK":
                        continue
                        
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extract sender
                    from_header, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(from_header, bytes):
                        from_header = from_header.decode(encoding or "utf-8", errors="ignore")
                        
                    # Extract subject
                    subject_header, encoding = decode_header(msg.get("Subject"))[0]
                    if isinstance(subject_header, bytes):
                        subject_header = subject_header.decode(encoding or "utf-8", errors="ignore")
                        
                    # Extract body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        
                    # Extract email address from From header
                    import re
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+', from_header)
                    sender_email = email_match.group(0) if email_match else from_header
                    
                    sentiment = analyze_reply_sentiment(body)
                    
                    replies.append({
                        'sender': from_header,
                        'email': sender_email,
                        'subject': subject_header,
                        'snippet': body[:200] + ("..." if len(body) > 200 else ""),
                        'sentiment': sentiment,
                        'is_mock': False
                    })
            mail.logout()
        except Exception as e:
            print(f"IMAP fetch error: {e}. Falling back to simulated replies.")
            
    # 2. Return mock replies as fallback to show functionality
    if not replies:
        mock_data = [
            {
                'sender': 'Sarah Jenkins <sarah@zensoundtherapy.com>',
                'email': 'sarah@zensoundtherapy.com',
                'subject': 'Re: Wholesale Singing Bowls Partnership Opportunity',
                'snippet': 'Hi! Thank you for the presentation. I really love the look of your hand-carved singing bowls. Can you please send over your wholesale price list for bulk orders of 100+ units?',
                'sentiment': 'Positive',
                'is_mock': True
            },
            {
                'sender': 'David Miller <info@sacredspaceyoga.co.uk>',
                'email': 'info@sacredspaceyoga.co.uk',
                'subject': 'Automatic Reply: Wholesale Singing Bowls Partnership',
                'snippet': 'Thank you for your email. I am currently out of the office on a yoga retreat returning next Monday. I will review your presentation as soon as I return.',
                'sentiment': 'Neutral',
                'is_mock': True
            },
            {
                'sender': 'Liam Nelson <liam@mindfulretailers.ca>',
                'email': 'liam@mindfulretailers.ca',
                'subject': 'Re: Wholesale Singing Bowls Partnership Opportunity',
                'snippet': 'Please unsubscribe me from this list. We do not source bowls from external vendors.',
                'sentiment': 'Unsubscribe',
                'is_mock': True
            }
        ]
        
        # Analyze sentiment for mock data
        for mock in mock_data:
            mock['sentiment'] = analyze_reply_sentiment(mock['snippet'])
        replies.extend(mock_data)
        
    return replies
