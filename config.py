import os
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data storage paths
DATA_DIR = os.path.join(BASE_DIR, "data")
BUYERS_CSV = os.path.join(DATA_DIR, "buyers.csv")
BUSINESS_CSV = os.path.join(DATA_DIR, "business_emails.csv")
INDIVIDUAL_CSV = os.path.join(DATA_DIR, "individual_emails.csv")
SENT_LOG_CSV = os.path.join(DATA_DIR, "sent_log.csv")
SETTINGS_JSON = os.path.join(DATA_DIR, "settings.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Email configuration defaults
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Search keyword and other settings
SEARCH_KEYWORD = os.getenv("SEARCH_KEYWORD", "Singing Bowls")
DAILY_SEND_LIMIT = int(os.getenv("DAILY_SEND_LIMIT", "100"))
PRESENTATION_PATH = os.path.join(BASE_DIR, os.getenv("PRESENTATION_PATH", "assets/company_presentation.pdf"))

# Default email template settings
DEFAULT_SUBJECT = "Wholesale Singing Bowls Partnership Opportunity"
DEFAULT_BODY = """Dear {name},

{personalization}

We are a leading exporter of handcrafted Himalayan Singing Bowls. Based on our research, your business/profile shows a keen interest in high-quality wellness, meditation, and sound healing products.

We would love to partner with you to supply premium singing bowls directly from Kathmandu. We have attached our product presentation and catalog, detailing our craft, sizes, and pricing structures.

Please find our presentation attached. We look forward to hearing from you.

Best regards,
The Export Team
"""

# Send delay in seconds (to avoid spam blocking)
SEND_DELAY = 2.0
