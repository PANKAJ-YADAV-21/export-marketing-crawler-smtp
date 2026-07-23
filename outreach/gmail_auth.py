import smtplib

def verify_smtp_credentials(email, app_password):
    """
    Connect to smtp.gmail.com:587 and login to verify if credentials are correct.
    Returns (success_boolean, message_string).
    """
    if not email or not app_password:
        return False, "Email or App Password is empty."
        
    try:
        # Establish connection
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(email, app_password)
        server.quit()
        return True, "Authentication Successful."
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication Failed. Invalid Gmail address or App Password."
    except Exception as e:
        return False, f"Connection Failed: {str(e)}"
