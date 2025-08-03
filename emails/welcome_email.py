import random
import string
from utils.email_util import smtp_connection
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException

# Configuration
SENDER_EMAIL = "info@kokomoyachts.com"
LOGIN_URL = "https://kokomoyachtclub.vip/login"
RESET_PASS_URL = "https://kokomoyachtclub.vip/forgot_password"
USER_MANUAL_URL = (
    "https://image-bucket-kokomo-yacht-club.s3.ap-southeast-2.amazonaws.com/"
    "kyc_member_portal_user_manual.pdf"
)
BCC_EMAILS = [
    "brian@kokomoyachtclub.vip",
    "info@iusdigitalsolutions.com"
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
                <html>
                    <head>
                        <style>
                        body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px; }}
                        .container {{ max-width: 600px; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                        h2 {{ color: #002147; margin-bottom: 20px; }}
                        p {{ font-size: 16px; color: #333333; line-height: 1.5; }}
                        .highlight {{ font-weight: bold; color: #002147; }}
                        .button {{ display: inline-block; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                        .footer {{ margin-top: 30px; font-size: 14px; color: #777777; }}
                        .link {{ color: #004080; font-weight: bold; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                        <p>Greetings,</p>
                        <h2>Dear {first_name} {last_name},</h2>
                        <p>Welcome to the Kokomo Yacht Club! Your membership account has been successfully created.</p>
                        <p>Please find below your login credentials:</p>
                        <p><span class="highlight">Username:</span> {username}</p>
                        <p><span class="highlight">Temporary Password:</span> {temp_password}</p>
                        <p><span class="highlight">Registered Email:</span> {to_email}</p>
                        <p><a href="{LOGIN_URL}" class="button" style="background-color:#004080;color:#ffffff;">Click here to login</a></p>
                        <p>For security reasons, please set a new password at your earliest convenience by clicking the button below:</p>
                        <p><a href="{RESET_PASS_URL}" class="button" style="background-color:#004080;color:#ffffff;">Reset Your Password</a></p>
                        <p>To help you get started, you can download the <a href="{USER_MANUAL_URL}" class="link">KYC Member Portal User Manual</a>.</p>
                        <p>If you have any questions or require assistance, please do not hesitate to reach out to our support team.</p>
                        <p class="footer">Sincerely,<br><strong>Kokomo Yacht Club Team</strong></p>
                        </div>
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