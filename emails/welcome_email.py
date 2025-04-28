import random
import string
from utils.smtp import smtp_connection
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException

SENDER_EMAIL = "brian@kokomoyachtclub.vip"
Login_URL = "https://kokomoyachtclub.vip/login"
CC_EMAIL = "ali@iusdigitalsolutions.com"

def generate_temp_password(length=10):
    """Generate a random temporary password."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

#when we start sending to the emails to user directly 
#def send_welcome_email(to_email: str, first_name: str, last_name: str, member_id: int, temp_password: str,username: str):
def send_welcome_email(to_email: str, first_name: str, last_name: str, member_id: int, temp_password: str, username: str):
    """Sends a welcome email with temporary password and password update link."""
    try:
        server = smtp_connection()

        subject = "Welcome to Kokomo Yacht Club!"
        body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    background: #ffffff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }}
                h2 {{
                    color: #003366;
                }}
                p {{
                    font-size: 16px;
                    color: #333333;
                }}
                .highlight {{
                    font-weight: bold;
                    color: #003366;
                }}
                .button {{
                    display: inline-block;
                    background-color: #007BFF;
                    color: #ffffff !important;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    border: none;
                    text-align: center;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #666666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Welcome to Kokomo Yacht Club, {first_name}!</h2>
                <p>We're thrilled to have you on board. Your account has been successfully created!</p>
                
                <p><span class="highlight">Username:</span> {username}</p>
                <p><span class="highlight">Temporary Password:</span> {temp_password}</p>
                
                <p>Use the above mentioned information for logging in!</p>
                
                <a class="button" href="{Login_URL}">LOGIN</a>
                
                <p class="footer">If you have any questions or need assistance, feel free to contact our support team.</p>
                
                <p class="footer">Best Regards,<br><strong>Kokomo Yacht Club Team</strong></p>
            </div>
        </body>
    </html>
    """


        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Cc"] = CC_EMAIL 
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return {"status": "success", "message": "Email sent successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
