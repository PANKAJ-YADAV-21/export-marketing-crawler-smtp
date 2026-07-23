import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config
from logger import activity_logger
from outreach.attachment_handler import load_attachment
from outreach.personalization import generate_personalized_line

def send_campaign(subject, body_template, audience_type, sender_email=None, sender_password=None, presentation_path=None):
    """
    Orchestrates the dispatch of outreach emails.
    - audience_type: 'business', 'individual', or 'all'
    - sender_email / sender_password: uses config defaults if not provided
    - presentation_path: uses config default if not provided
    """
    # 1. Fetch credentials
    email = sender_email or config.GMAIL_EMAIL
    password = sender_password or config.GMAIL_APP_PASSWORD
    pdf_path = presentation_path or config.PRESENTATION_PATH
    
    if not email or not password:
        return {
            'success': False,
            'message': "Gmail credentials not configured. Please set them in Settings.",
            'stats': {'total': 0, 'success': 0, 'failed': 0}
        }
        
    # 2. Get list of recipients based on audience selection
    all_buyers = activity_logger.get_discovered_buyers()
    sent_emails = activity_logger.get_sent_emails()
    classified = activity_logger.get_classified_emails()
    
    target_emails = set()
    if audience_type == 'business':
        target_emails = classified['business']
    elif audience_type == 'individual':
        target_emails = classified['individual']
    else: # 'all'
        target_emails = {b['email'].strip().lower() for b in all_buyers if b.get('email')}
        
    # Filter out duplicates (already sent)
    pending_emails = target_emails - sent_emails
    
    if not pending_emails:
        return {
            'success': True,
            'message': "No pending unsent emails found for the selected audience.",
            'stats': {'total': 0, 'success': 0, 'failed': 0}
        }
        
    # Build a lookup dictionary of buyer records
    buyer_lookup = {b['email'].strip().lower(): b for b in all_buyers if b.get('email')}
    
    # 3. Load attachment
    attachment_part = load_attachment(pdf_path)
    if not attachment_part:
        return {
            'success': False,
            'message': f"Presentation attachment file not found or load failed at: {pdf_path}",
            'stats': {'total': 0, 'success': 0, 'failed': 0}
        }
        
    # 4. Initialize SMTP Connection
    try:
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
        smtp_server.starttls()
        smtp_server.login(email, password)
    except Exception as e:
        return {
            'success': False,
            'message': f"Failed to log in to Gmail SMTP server: {str(e)}",
            'stats': {'total': 0, 'success': 0, 'failed': 0}
        }
        
    success_count = 0
    failed_count = 0
    successful_list = []
    failed_list = []
    
    # 5. Send emails
    for rec_email in pending_emails:
        buyer = buyer_lookup.get(rec_email, {})
        name = buyer.get('buyer_name') or "Wellness Partner"
        company = buyer.get('company_name') or "Wellness Center"
        
        # Build MIME Message
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = buyer.get('email') or rec_email
        msg['Subject'] = subject
        
        # Personalize body using AI-generated introductory line
        try:
            country = buyer.get('country') or "Global"
            platform = buyer.get('source_platform') or "Google"
            personal_line = generate_personalized_line(name, company, country, platform)
            body = body_template.format(name=name, company=company, personalization=personal_line)
        except Exception:
            # Fallback if key formatting issues occur
            body = body_template.replace('{name}', name).replace('{company}', company)
            if '{personalization}' in body:
                fallback_line = f"I came across {company} and was very impressed by your dedication to wellness products."
                body = body.replace('{personalization}', fallback_line)
            
        msg.attach(MIMEText(body, 'plain'))
        msg.attach(attachment_part)
        
        # Send
        sent_ok = False
        try:
            smtp_server.send_message(msg)
            sent_ok = True
        except smtplib.SMTPServerDisconnected:
            # Reconnect & try again
            try:
                smtp_server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
                smtp_server.starttls()
                smtp_server.login(email, password)
                smtp_server.send_message(msg)
                sent_ok = True
            except Exception as retry_err:
                print(f"SMTP retry error for {rec_email}: {retry_err}")
        except Exception as send_err:
            print(f"SMTP error for {rec_email}: {send_err}")
            
        # Log outcome
        if sent_ok:
            success_count += 1
            activity_logger.log_send_attempt(rec_email, 'sent')
            successful_list.append(rec_email)
        else:
            failed_count += 1
            activity_logger.log_send_attempt(rec_email, 'failed')
            failed_list.append(rec_email)
            
        # Cooldown sleep to avoid SMTP rate-limiting
        time.sleep(config.SEND_DELAY)
        
    # Close SMTP session
    try:
        smtp_server.quit()
    except Exception:
        pass
        
    return {
        'success': True,
        'message': f"Campaign completed. Sent: {success_count}, Failed: {failed_count}",
        'stats': {
            'total': len(pending_emails),
            'success': success_count,
            'failed': failed_count
        },
        'successful_emails': successful_list,
        'failed_emails': failed_list
    }
