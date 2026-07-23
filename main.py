import os
import csv
import pandas as pd
from flask import Flask, render_react, render_template, request, redirect, url_for, flash, Response
import config
from logging import activity_logger
from search import google_search, facebook_search, linkedin_search, directory_search, website_search
from outreach.classification import classify_emails
from outreach.gmail_sender import send_campaign

app = Flask(__name__)
app.secret_key = "export_marketing_secret_key"

# Ensure database files are initialized on start
activity_logger.initialize_csvs()

def update_env_file(updates):
    """Dynamically write settings changes back to the .env file."""
    env_path = os.path.join(config.BASE_DIR, '.env')
    env_lines = []
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_lines = f.readlines()
            
    # Parse existing variables
    env_dict = {}
    for line in env_lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_dict[k.strip()] = v.strip()
            
    # Apply updates
    for k, v in updates.items():
        env_dict[k] = v
        
    # Write back to .env
    with open(env_path, 'w') as f:
        # Write some header comments
        f.write("# --- Generated/Updated via Web Interface Settings ---\n")
        for k, v in env_dict.items():
            f.write(f"{k}={v}\n")
            
    # Reload in-memory config variables
    config.GMAIL_EMAIL = updates.get('GMAIL_EMAIL', config.GMAIL_EMAIL)
    config.GMAIL_APP_PASSWORD = updates.get('GMAIL_APP_PASSWORD', config.GMAIL_APP_PASSWORD)
    config.GEMINI_API_KEY = updates.get('GEMINI_API_KEY', config.GEMINI_API_KEY)
    config.SEARCH_KEYWORD = updates.get('SEARCH_KEYWORD', config.SEARCH_KEYWORD)
    if 'DAILY_SEND_LIMIT' in updates:
        config.DAILY_SEND_LIMIT = int(updates['DAILY_SEND_LIMIT'])
    if 'SEND_DELAY' in updates:
        config.SEND_DELAY = float(updates['SEND_DELAY'])
    config.PRESENTATION_PATH = updates.get('PRESENTATION_PATH', config.PRESENTATION_PATH)
    config.DEFAULT_SUBJECT = updates.get('DEFAULT_SUBJECT', config.DEFAULT_SUBJECT)
    config.DEFAULT_BODY = updates.get('DEFAULT_BODY', config.DEFAULT_BODY)

@app.route('/')
def index():
    buyers = activity_logger.get_discovered_buyers()
    sent_list = activity_logger.get_sent_emails()
    classified = activity_logger.get_classified_emails()
    
    total_buyers = len(buyers)
    
    # Calculate sent stats from sent_log.csv
    logs = []
    success_sent = 0
    failed_sent = 0
    if os.path.exists(config.SENT_LOG_CSV):
        with open(config.SENT_LOG_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                logs.append(row)
                if row.get('status') == 'sent':
                    success_sent += 1
                elif row.get('status') == 'failed':
                    failed_sent += 1
                    
    total_attempts = success_sent + failed_sent
    success_rate = round((success_sent / total_attempts) * 100, 1) if total_attempts > 0 else 0.0
    
    stats = {
        'total_buyers': total_buyers,
        'sent_count': len(sent_list),
        'unsent_count': max(0, total_buyers - len(sent_list)),
        'success_rate': success_rate,
        'business_count': len(classified['business']),
        'individual_count': len(classified['individual']),
        'success_sent': success_sent,
        'failed_sent': failed_sent
    }
    
    # Take latest 5 buyers
    latest_buyers = buyers[-5:][::-1]
    
    return render_template('index.html', stats=stats, latest_buyers=latest_buyers)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Handing CSV file uploads
        if 'csv_file' not in request.files:
            flash("No file part in request", "error")
            return redirect(request.url)
            
        file = request.files['csv_file']
        if file.filename == '':
            flash("No selected file", "error")
            return redirect(request.url)
            
        if file and file.filename.endswith('.csv'):
            try:
                # Read CSV via pandas
                df = pd.read_csv(file)
                # Normalize column headers to lowercase
                df.columns = [col.strip().lower() for col in df.columns]
                
                if 'email' not in df.columns:
                    flash("CSV must contain at least an 'email' column.", "error")
                    return redirect(request.url)
                    
                new_leads = []
                for _, row in df.iterrows():
                    email = str(row.get('email', '')).strip()
                    if email:
                        new_leads.append({
                            'buyer_name': str(row.get('buyer_name', row.get('name', 'Proprietor'))),
                            'company_name': str(row.get('company_name', row.get('company', 'Wellness Boutique'))),
                            'email': email,
                            'website': str(row.get('website', '')),
                            'country': str(row.get('country', 'Global')),
                            'source_platform': 'Imported CSV'
                        })
                
                added = activity_logger.log_discovered_buyers(new_leads)
                flash(f"Successfully uploaded CSV and merged {added} new leads into database.", "success")
            except Exception as e:
                flash(f"Error parsing CSV: {str(e)}", "error")
                
            return redirect(url_for('upload'))
            
    buyers = activity_logger.get_discovered_buyers()
    return render_template('upload.html', buyers=buyers, default_keyword=config.SEARCH_KEYWORD)

@app.route('/search', methods=['POST'])
def search():
    keyword = request.form.get('keyword', config.SEARCH_KEYWORD).strip()
    limit = int(request.form.get('limit', '5'))
    selected_platforms = request.form.getlist('platforms')
    
    if not selected_platforms:
        flash("Please select at least one target platform to crawl.", "error")
        return redirect(url_for('upload'))
        
    all_discovered = []
    
    # Run the selected adapters
    if 'google' in selected_platforms:
        all_discovered.extend(google_search.search_buyers(keyword, limit))
    if 'facebook' in selected_platforms:
        all_discovered.extend(facebook_search.search_buyers(keyword, limit))
    if 'linkedin' in selected_platforms:
        all_discovered.extend(linkedin_search.search_buyers(keyword, limit))
    if 'directory' in selected_platforms:
        all_discovered.extend(directory_search.search_buyers(keyword, limit))
    if 'website' in selected_platforms:
        all_discovered.extend(website_search.search_buyers(keyword, limit))
        
    added = activity_logger.log_discovered_buyers(all_discovered)
    flash(f"Crawl finished. Discovered {len(all_discovered)} potential leads. Merged {added} new records.", "success")
    return redirect(url_for('upload'))

@app.route('/classify', methods=['GET', 'POST'])
def classify():
    buyers = activity_logger.get_discovered_buyers()
    classified = activity_logger.get_classified_emails()
    
    total_buyers_emails = {b['email'].strip().lower() for b in buyers if b.get('email')}
    classified_emails = classified['business'].union(classified['individual'])
    unclassified_count = len(total_buyers_emails - classified_emails)
    
    if request.method == 'POST':
        if not total_buyers_emails:
            flash("No emails in database to classify.", "error")
            return redirect(url_for('classify'))
            
        # Run classification
        print("Starting AI classification on leads...")
        result = classify_emails(list(total_buyers_emails))
        
        # Save output
        activity_logger.save_classified_emails(result['business'], result['individual'])
        flash(f"AI Classification complete! Categorized {len(result['business'])} B2B business entities and {len(result['individual'])} individuals.", "success")
        return redirect(url_for('classify'))
        
    return render_template(
        'classify.html', 
        total_buyers=len(buyers), 
        unclassified_count=unclassified_count,
        business_emails=list(classified['business']),
        individual_emails=list(classified['individual'])
    )

@app.route('/send', methods=['GET', 'POST'])
def send():
    buyers = activity_logger.get_discovered_buyers()
    classified = activity_logger.get_classified_emails()
    
    counts = {
        'total': len(buyers),
        'business': len(classified['business']),
        'individual': len(classified['individual'])
    }
    
    if request.method == 'POST':
        subject = request.form.get('subject', config.DEFAULT_SUBJECT)
        body = request.form.get('body', config.DEFAULT_BODY)
        audience = request.form.get('audience', 'business')
        
        # Dispatch campaign
        result = send_campaign(
            subject=subject,
            body_template=body,
            audience_type=audience,
            sender_email=config.GMAIL_EMAIL,
            sender_password=config.GMAIL_APP_PASSWORD,
            presentation_path=config.PRESENTATION_PATH
        )
        
        if result.get('success'):
            stats = result.get('stats', {})
            flash(f"Campaign Complete! Sent: {stats.get('success', 0)} successfully, Failed: {stats.get('failed', 0)}.", "success")
            return redirect(url_for('report'))
        else:
            flash(result.get('message', "Outreach failed to launch."), "error")
            return redirect(url_for('send'))
            
    return render_template('send.html', counts=counts, config_data=config)

@app.route('/report')
def report():
    logs = []
    success_count = 0
    failed_count = 0
    
    if os.path.exists(config.SENT_LOG_CSV):
        with open(config.SENT_LOG_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                logs.append(row)
                if row.get('status') == 'sent':
                    success_count += 1
                elif row.get('status') == 'failed':
                    failed_count += 1
                    
    # Show newest first in transactions
    logs = logs[::-1]
    
    return render_template('report.html', logs=logs, success_count=success_count, failed_count=failed_count)

@app.route('/download-report')
def download_report():
    if not os.path.exists(config.SENT_LOG_CSV):
        return "No report data available.", 404
        
    with open(config.SENT_LOG_CSV, 'r', encoding='utf-8') as f:
        csv_data = f.read()
        
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=campaign_sent_report.csv"}
    )

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        updates = {
            'GMAIL_EMAIL': request.form.get('gmail_email', '').strip(),
            'GMAIL_APP_PASSWORD': request.form.get('gmail_app_password', '').strip(),
            'GEMINI_API_KEY': request.form.get('gemini_api_key', '').strip(),
            'SEARCH_KEYWORD': request.form.get('search_keyword', 'Singing Bowls').strip(),
            'DAILY_SEND_LIMIT': request.form.get('daily_send_limit', '100').strip(),
            'SEND_DELAY': request.form.get('send_delay', '2.0').strip(),
            'PRESENTATION_PATH': request.form.get('presentation_path', 'assets/company_presentation.pdf').strip(),
            'DEFAULT_SUBJECT': request.form.get('default_subject', config.DEFAULT_SUBJECT).strip(),
            'DEFAULT_BODY': request.form.get('default_body', config.DEFAULT_BODY)
        }
        try:
            update_env_file(updates)
            flash("Settings saved successfully and .env file updated.", "success")
        except Exception as e:
            flash(f"Error saving settings: {str(e)}", "error")
            
        return redirect(url_for('settings'))
        
    return render_template('settings.html', config_data=config)

if __name__ == '__main__':
    # Initialize database files
    activity_logger.initialize_csvs()
    print("Export Automation Server starting on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
