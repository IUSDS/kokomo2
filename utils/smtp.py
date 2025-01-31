import smtplib
from utils.secrets import SMTP_USER, SMTP_PASS
from fastapi import HTTPException

# SMTP Connection Function
def smtp_connection():
    smtp_host = "email-smtp.ap-southeast-2.amazonaws.com"
    smtp_port = 587
    smtp_username = SMTP_USER
    smtp_password = SMTP_PASS

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        return server
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMTP Connection Error: {str(e)}")