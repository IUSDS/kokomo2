import random
import string
from utils.email_util import smtp_connection
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException

# Configuration
# SENDER_EMAIL = "info@kokomoyachts.com"
LOGIN_URL = "https://kokomoyachtclub.vip/login"
RESET_PASS_URL = "https://kokomoyachtclub.vip/forgot_password"
USER_MANUAL_URL = (
    "https://image-bucket-kokomo-yacht-club.s3.ap-southeast-2.amazonaws.com/"
    "kyc_member_portal_user_manual.pdf"
)
# BCC_EMAILS = [
#     "brian@kokomoyachtclub.vip",
#     "info@iusdigitalsolutions.com"
# ]


SENDER_EMAIL = "satya@kokomoyachtclub.vip"
BCC_EMAILS = [
    "aishwarya@iusdigitalsolutions.com"
]

def generate_temp_password(length: int = 10) -> str:
    """Generate a random temporary password."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))


def send_welcome_email(
    to_email: str,
    first_name: str,
    last_name: str,
    username: str,
    temp_password: str
) -> dict:
    """Sends a formal welcome email with a reset password link and a link to the user manual."""
    try:
        server = smtp_connection()

        # Create the message container
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = "Welcome to Kokomo Yacht Club"
        msg["Bcc"] = ", ".join(BCC_EMAILS)

        # HTML body with link to S3-hosted PDF
        body = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome to Kokomo Yacht Club • Kokomo Yacht Club</title>
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
                                        
                                        <p style="color: #2c3e50; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                            Greetings,
                                        </p>
                                        
                                        <h2 style="color: #033e8b; font-size: 20px; font-weight: 400; margin: 0 0 30px 0;">
                                            Dear {first_name} {last_name},
                                        </h2>
                                        
                                        <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                            Welcome to the Kokomo Yacht Club! Your membership account has been successfully created.
                                        </p>
                                        
                                        <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                            Please find below your login credentials:
                                        </p>
                                        
                                        <p style="color: #2c3e50; font-size: 16px; line-height: 1.6; margin: 0 0 10px 0;">
                                            <strong style="color: #033e8b;">Username:</strong> {username}
                                        </p>
                                        <p style="color: #2c3e50; font-size: 16px; line-height: 1.6; margin: 0 0 10px 0;">
                                            <strong style="color: #033e8b;">Temporary Password:</strong> {temp_password}
                                        </p>
                                        <p style="color: #2c3e50; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                            <strong style="color: #033e8b;">Registered Email:</strong> {to_email}
                                        </p>
                                        
                                        <!-- Login Button -->
                                        <div style="text-align: center; margin: 30px 0;">
                                            <a href="{LOGIN_URL}" 
                                            style="background-color: #033e8b; 
                                                    color: #ffffff; 
                                                    padding: 14px 30px; 
                                                    text-decoration: none; 
                                                    font-size: 16px; 
                                                    display: inline-block;
                                                    border-radius: 4px;">
                                                Click here to login
                                            </a>
                                        </div>
                                        
                                        <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                            For security reasons, please set a new password at your earliest convenience by clicking the button below:
                                        </p>
                                        
                                        <!-- Reset Button -->
                                        <div style="text-align: center; margin: 30px 0;">
                                            <a href="{RESET_PASS_URL}" 
                                            style="background-color: #033e8b; 
                                                    color: #ffffff; 
                                                    padding: 14px 30px; 
                                                    text-decoration: none; 
                                                    font-size: 16px; 
                                                    display: inline-block;
                                                    border-radius: 4px;">
                                                Reset Your Password
                                            </a>
                                        </div>
                                        
                                        <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                            To help you get started, you can download the <a href="{USER_MANUAL_URL}" style="color: #033e8b; text-decoration: none; font-weight: bold;">KYC Member Portal User Manual</a>.
                                        </p>
                                        
                                        <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 30px 0 0 0;">
                                            If you have any questions or require assistance, please do not hesitate to reach out to our support team.
                                        </p>
                                        
                                        <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 30px 0 0 0;">
                                            Sincerely,<br>
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
        
        msg.attach(MIMEText(body, "html"))

        # Send the message
        recipients = [to_email] + BCC_EMAILS
        server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
        server.quit()
        
        print("Email sent")

        return {"status": "success", "message": "Welcome email sent successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")
