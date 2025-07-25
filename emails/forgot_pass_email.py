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
    """Send simple yet elegant yacht club password reset email"""
    
    reset_link = f"https://kokomoyachtclub.vip/new_password?token={token}"

    subject = "Password Reset • Kokomo Yacht Club"
    
    # Clean plain text version
    body_text = f"""
KOKOMO YACHT CLUB

Dear Member,

We received a request to reset your password.

Reset your password: {reset_link}

This link expires in 30 minutes.

If you didn't request this, please ignore this email.

Best regards,
Kokomo Yacht Club Team

---
kokomoyachtclub.vip
    """

    # Simple yet elegant HTML design
    body_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset • Kokomo Yacht Club</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color: #f8f9fa; color: #2c3e50;">
        
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f8f9fa; padding: 40px 20px;">
            <tr>
                <td align="center">
                    
                    <!-- Main Container -->
                    <table cellpadding="0" cellspacing="0" border="0" width="500" style="background-color: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                        
                        <!-- Header -->
                        <tr>
                            <td style="background-color: #033e8b; padding: 40px 30px; text-align: center;">
                                <img src="https://kokomoyachtclub.vip/images/logo.png" 
                                     alt="Kokomo Yacht Club Logo" 
                                     style="max-height: 60px; width: auto; margin-bottom: 20px; display: block; margin-left: auto; margin-right: auto;"
                                     onerror="this.style.display='none';">
                                <h1 style="color: #ffffff; font-size: 24px; font-weight: 300; margin: 0; letter-spacing: 2px;">
                                    KOKOMO YACHT CLUB
                                </h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                
                                <h2 style="color: #033e8b; font-size: 20px; font-weight: 400; margin: 0 0 30px 0;">
                                    Password Reset
                                </h2>
                                
                                <p style="color: #2c3e50; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    Dear Member,
                                </p>
                                
                                <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                    We received a request to reset your password for your Kokomo Yacht Club account.
                                </p>
                                
                                <!-- Reset Button -->
                                <div style="text-align: center; margin: 30px 0;">
                                    <a href="{reset_link}" 
                                       style="background-color: #033e8b; 
                                              color: #ffffff; 
                                              padding: 14px 30px; 
                                              text-decoration: none; 
                                              font-size: 16px; 
                                              display: inline-block;
                                              border-radius: 4px;">
                                        Reset Password
                                    </a>
                                </div>
                                
                                <!-- Security Notice -->
                                <div style="border-left: 3px solid #033e8b; padding: 15px 20px; background-color: #f8f9ff; margin: 30px 0;">
                                    <p style="color: #033e8b; font-size: 14px; margin: 0;">
                                        <strong>Note:</strong> This link expires in 30 minutes. If you didn't request this reset, please ignore this email.
                                    </p>
                                </div>
                                
                                <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 30px 0 0 0;">
                                    Best regards,<br>
                                    <strong style="color: #033e8b;">Kokomo Yacht Club Team</strong>
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e9ecef;">
                                <p style="color: #6c757d; font-size: 12px; margin: 0;">
                                    Kokomo Yacht Club<br>
                                    <a href="https://kokomoyachtclub.vip" style="color: #033e8b; text-decoration: none;">kokomoyachtclub.vip</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                    
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    try:
        logging.info(f"Sending simple elegant password reset email to {email}")
        
        # Create the email content
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"Kokomo Yacht Club <{ADMIN_EMAIL}>"
        message["To"] = email
        message["Reply-To"] = ADMIN_EMAIL
        
        recipients = [email] + BCC_EMAILS
        
        # Attach both versions
        message.attach(MIMEText(body_text, "plain"))
        message.attach(MIMEText(body_html, "html"))
        
        # Send the email
        server = smtp_connection()
        server.sendmail(ADMIN_EMAIL, recipients, message.as_string())
        server.quit()
        
        logging.info(f"Simple elegant password reset email sent successfully to {email}")

    except Exception as e:
        logging.error(f"Failed to send password reset email to {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")