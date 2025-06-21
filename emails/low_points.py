from fastapi import HTTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, EmailStr
from utils.email_util import smtp_connection

# Admin Email Address
ADMIN_EMAIL = "info@kokomoyachts.com"
TO_EMAIL = "satya@iusdigitalsolutions.com"

# Function to Send Email Notification for insufficient point balance
def low_points_notification(first_name: str, last_name: str, curr_points: int, point_cost: int):
    """
    Sends an email notification via Amazon SES when a member has insufficient points.

    Args:
        username: The username of the member.
        first_name: The first_name of the member.
        last_name: The last_name of the member.
        curr_points: Current points balance.
        point_cost: Cost in points for the requested action.
    Raises:
        ClientError: If sending the email fails.
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
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = ADMIN_EMAIL
        message["To"] = "brian@kokomoyachtclub.com"
        message.attach(MIMEText(body_text, "plain"))

        server.sendmail(ADMIN_EMAIL, TO_EMAIL, message.as_string())
        server.quit()
        print("Email sent to low points notification")
        return {"status": "success", "message": "low points notification email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send low points notification email: {str(e)}")
