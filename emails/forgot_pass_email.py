from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from utils.email_util import smtp_connection
import logging
import re

BCC_EMAILS = [
    "brian@kokomoyachtclub.vip",
    "info@iusdigitalsolutions.com"
]

ADMIN_EMAIL = "info@kokomoyachts.com"

def send_reset_email(email: str, token: str):
    """Send password reset email with proper BCC handling"""
    
    reset_link = f"https://kokomoyachtclub.vip/new_password?token={token}"

    subject = "Password Reset Request"
    
    # Plain text version
    body_text = f"""Dear User,

    We received a request to reset your password. To proceed, please click the link below:

    Reset Password: {reset_link}

    This link is valid for 30 minutes. If you didn't request a password reset, please disregard this email.

    For assistance, feel free to reach out to our support team.

    Best regards,

    Kokomo Yacht Club Team
    """

    # HTML version for better presentation
    body_html = f"""
    <html>
      <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #2c3e50;">Password Reset Request</h2>
          
          <p>Dear User,</p>
          
          <p>We received a request to reset your password. To proceed, please click the button below:</p>
          
          <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" 
               style="background-color: #3498db; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; font-weight: bold; 
                      display: inline-block;">
              Reset Password
            </a>
          </div>
          
          <p>Alternatively, you can copy and paste this link into your browser:</p>
          <p style="background-color: #f8f9fa; padding: 10px; border-left: 4px solid #3498db; 
                    word-break: break-all; font-family: monospace; font-size: 12px;">
            {reset_link}
          </p>
          
          <p><strong>Important:</strong> This link is valid for 30 minutes only.</p>
          
          <p>If you didn't request a password reset, please disregard this email and your password will remain unchanged.</p>
          
          <p>For assistance, feel free to reach out to our support team.</p>
          
          <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
          
          <p style="color: #7f8c8d;">
            Best regards,<br>
            <strong>Kokomo Yacht Club Team</strong>
          </p>
        </div>
      </body>
    </html>
    """

    try:
        print(f"Sending password reset email to {email}")
        
        # Create the email content
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = ADMIN_EMAIL
        message["To"] = email
        recipients = [email] + BCC_EMAILS
        message.attach(MIMEText(body_text, "plain"))
        message.attach(MIMEText(body_html, "html"))
        server = smtp_connection()
        server.sendmail(ADMIN_EMAIL, recipients, message.as_string())
        server.quit()
        
        print(f"Password reset email sent successfully to {email}")

    except Exception as e:
        print(f"Failed to send password reset email to {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")