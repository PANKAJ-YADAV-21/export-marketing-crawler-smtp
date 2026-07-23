import os
from email.mime.base import MIMEBase
from email import encoders

def load_attachment(file_path):
    """
    Load a file from file_path and return it as a MIMEBase object.
    Returns None if the file is missing or cannot be loaded.
    """
    if not os.path.exists(file_path):
        print(f"Attachment file not found: {file_path}")
        return None
        
    try:
        filename = os.path.basename(file_path)
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{filename}"',
            )
            return part
    except Exception as e:
        print(f"Error loading attachment {file_path}: {e}")
        return None
