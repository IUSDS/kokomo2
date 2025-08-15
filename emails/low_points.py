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

# ADMIN_EMAIL = "satya@kokomoyachtclub.vip"
# TO_EMAIL = "aishwarya@iusdigitalsolutions.com"

# BCC_EMAILS = [
#     "aishwarya@iusdigitalsolutions.com"
# ]



def low_points_notification(first_name: str, last_name: str, curr_points: int, point_cost: int):
    """
    Sends an email notification via Amazon SES when a member has insufficient points.
    """
    subject = f"Low Points for Member: {first_name} {last_name}"

    body_text = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Points Alert • Kokomo Yacht Club</title>
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
                                        Hello Brian,
                                    </p>
                                    
                                    <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                        Member: {first_name} {last_name} has only {curr_points} points left. They just made a booking for {point_cost} points.
                                    </p>
                                    
                                    <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 0;">
                                        Best regards,<br>
                                        <strong style="color: #033e8b;">KYC Development Team</strong>
                                    </p>
                                    
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e9ecef;">
                                    <p style="color: #6c757d; font-size: 12px; margin: 0;">
                                        Kokomo Yacht Club<br>
                                        <a href="https://kokomoyachtclub.vip" style="color: #033e8b; text-decoration: none;">
                                            kokomoyachtclub.vip
                                        </a>
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
        server = smtp_connection()

        # Build the message
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = ADMIN_EMAIL
        message["To"] = TO_EMAIL
        message["Bcc"] = ", ".join(BCC_EMAILS)
        message.attach(MIMEText(body_text, "html"))

        # Send to PRIMARY + BCC recipients
        recipients = [TO_EMAIL] + BCC_EMAILS
        server.sendmail(ADMIN_EMAIL, recipients, message.as_string())
        server.quit()

        print("Email sent: low points notification")
        return {"status": "success", "message": "low points notification email sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send low points notification email: {str(e)}")
