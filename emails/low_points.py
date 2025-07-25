from fastapi import HTTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, EmailStr
from utils.email_util import smtp_connection

# Admin Email Address
ADMIN_EMAIL = "info@kokomoyachts.com"
TO_EMAIL = "brian@kokomoyachtclub.vip"

# BCC recipients for every invite
BCC_EMAILS = [
    "info@iusdigitalsolutions.com"
]

def low_points_notification(first_name: str, last_name: str, curr_points: int, point_cost: int):
    """
    Sends an email notification via Amazon SES when a member has insufficient points.
    """
    subject = f"Low Points for Member: {first_name} {last_name}"
    body_text = f"""
    Hello Brian,

    Member: {first_name} {last_name} has only {curr_points} points left. They just made a booking for {point_cost} points.

    Best regards,
    KYC Development Team
    """

    try:
        server = smtp_connection()

        # Build the message
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = ADMIN_EMAIL
        message["To"] = TO_EMAIL
        message["Bcc"] = ", ".join(BCC_EMAILS)
        message.attach(MIMEText(body_text, "plain"))

        # Send to PRIMARY + BCC recipients
        recipients = [TO_EMAIL] + BCC_EMAILS
        server.sendmail(ADMIN_EMAIL, recipients, message.as_string())
        server.quit()

        print("Email sent: low points notification")
        return {"status": "success", "message": "low points notification email sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send low points notification email: {str(e)}")
