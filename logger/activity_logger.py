import os
import csv
from datetime import datetime
import config

def initialize_csvs():
    """Ensure data files exist with correct headers."""
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # 1. buyers.csv
    if not os.path.exists(config.BUYERS_CSV):
        with open(config.BUYERS_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['buyer_name', 'company_name', 'email', 'website', 'country', 'source_platform'])
            
    # 2. sent_log.csv
    if not os.path.exists(config.SENT_LOG_CSV):
        with open(config.SENT_LOG_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email_address', 'status', 'timestamp'])
            
    # 3. business_emails.csv
    if not os.path.exists(config.BUSINESS_CSV):
        with open(config.BUSINESS_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email_address'])
            
    # 4. individual_emails.csv
    if not os.path.exists(config.INDIVIDUAL_CSV):
        with open(config.INDIVIDUAL_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email_address'])

def get_discovered_buyers():
    """Load all discovered buyers from buyers.csv."""
    initialize_csvs()
    buyers = []
    with open(config.BUYERS_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            buyers.append(dict(row))
    return buyers

def log_discovered_buyers(new_buyers):
    """Append a list of new buyers to buyers.csv, avoiding exact duplicates."""
    initialize_csvs()
    existing = {b['email'].strip().lower() for b in get_discovered_buyers() if b.get('email')}
    
    logged_count = 0
    with open(config.BUYERS_CSV, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for buyer in new_buyers:
            email = buyer.get('email', '').strip().lower()
            if email and email not in existing:
                writer.writerow([
                    buyer.get('buyer_name', ''),
                    buyer.get('company_name', ''),
                    buyer.get('email', ''),
                    buyer.get('website', ''),
                    buyer.get('country', ''),
                    buyer.get('source_platform', '')
                ])
                existing.add(email)
                logged_count += 1
    return logged_count

def get_sent_emails():
    """Return a set of lowercase email addresses that have a status of 'sent'."""
    initialize_csvs()
    sent_emails = set()
    with open(config.SENT_LOG_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('status') == 'sent':
                sent_emails.add(row.get('email_address', '').strip().lower())
    return sent_emails

def log_send_attempt(email, status):
    """Log an outreach dispatch attempt to sent_log.csv."""
    initialize_csvs()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(config.SENT_LOG_CSV, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([email.strip(), status, timestamp])

def save_classified_emails(business_list, individual_list):
    """Save lists of classified email addresses to their respective CSV files."""
    initialize_csvs()
    with open(config.BUSINESS_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['email_address'])
        for email in business_list:
            writer.writerow([email.strip()])
            
    with open(config.INDIVIDUAL_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['email_address'])
        for email in individual_list:
            writer.writerow([email.strip()])

def get_classified_emails():
    """Return dictionary with sets of business and individual emails."""
    initialize_csvs()
    business = set()
    individual = set()
    
    with open(config.BUSINESS_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('email_address'):
                business.add(row['email_address'].strip().lower())
                
    with open(config.INDIVIDUAL_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('email_address'):
                individual.add(row['email_address'].strip().lower())
                
    return {'business': business, 'individual': individual}
