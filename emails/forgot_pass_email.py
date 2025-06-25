from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from utils.email_util import smtp_connection


def send_reset_email(email: str, token: str):
    reset_link = f"https://kokomoyachtclub.vip/new_password?token={token}"

    subject = "Password Reset Request"
    body_text = f"""Dear User,

        We received a request to reset your password. To proceed, please click the link below:
        Reset Password: {reset_link}

        This link is valid for 30 minutes. If you didn’t request a password reset, please disregard this email.
        For assistance, feel free to reach out to our support team.

        Best regards,

        Kokomo Yacht Club Team
        """

    sender_email = "info@kokomoyachts.com"

    try:
        # Create the email content
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = email

        # Add plain text and HTML parts
        message.attach(MIMEText(body_text, "plain"))

        # Use the SMTP connection from utils.email_util.py
        server = smtp_connection()
        server.sendmail(sender_email, email, message.as_string())
        server.quit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
