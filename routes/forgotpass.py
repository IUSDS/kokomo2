from fastapi import FastAPI, HTTPException, Depends, Form, APIRouter
from pydantic import BaseModel, EmailStr
from database import get_db_connection
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import secrets
import smtplib
from datetime import datetime, timedelta
import requests

forgot_password_route = APIRouter()

# Request schemas
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Send reset password email
def send_reset_email(email: str, token: str):
    reset_link = f"https://{kokomo-link}/{}route}?token={token}"

    subject = "Password Reset Request"
    body_text = f"""Dear User,

        We received a request to reset your password. To proceed, please click the link below:
        Reset Password: {reset_link}

        This link is valid for 30 minutes. If you didn’t request a password reset, please disregard this email.
        For assistance, feel free to reach out to our support team.
        
        Best regards,
        
        Kokomo Yacht Club Team
        """
    
    sender_email = "info@kokomoyachtclub.vip"
    smtp_host = "email-smtp.ap-southeast-2.amazonaws.com"
    smtp_port = 587  # port 587 for STARTTLS
    smtp_username = "AKIAXKPUZZCOOVVEAYFO"  
    smtp_password = ""  
    try:
        # Create the email content
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = email

        # Add plain text and HTML parts
        message.attach(MIMEText(body_text, "plain"))
        #message.attach(MIMEText(body_html, "html"))

        # Connect to SMTP server
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  # Upgrade to secure connection
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, email, message.as_string())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Endpoint to handle forgot password requests
@forgot_password_route.post("/forgot-password")
def forgot_password(email: str = Form(...)):
    # Generate a secure token
    token = secrets.token_hex(16)  # Generates a 32-character hexadecimal string
    expiry_time = datetime.utcnow() + timedelta(hours=0.5)  # Token valid for 30 mins
    # Check if the email exists in the database
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if email exists in the database
            cursor.execute("SELECT email_id FROM Members WHERE email_id = %s", (email,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="Email not found.")

            # Store the token in the database
            cursor.execute(
                "INSERT INTO password_reset_tokens (email, token, expiry_time) VALUES (%s, %s, %s)",
                (email, token, expiry_time),
            )
            connection.commit()
            # Send the reset email
            send_reset_email(email, token)

        return {"message": "Password reset email sent."}
    finally:
        connection.close()

# Endpoint to reset the password
@forgot_password_route.post("/reset-password")
def reset_password(request: ResetPasswordRequest):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Validate the token
            cursor.execute(
                "SELECT email, expiry_time FROM password_reset_tokens WHERE token = %s",
                (request.token,),
            )
            token_data = cursor.fetchone()
            if not token_data:
                raise HTTPException(status_code=404, detail="Invalid or expired token.")

            # Check token expiry
            if datetime.datetime() > token_data["expiry_time"]:
                raise HTTPException(status_code=400, detail="Token has expired.")

            # Update the user's password
            cursor.execute(
                "UPDATE Members SET pass = %s WHERE email_id = %s",
                (request.new_password, token_data["email"]),
            )
            connection.commit()

            # Delete the token after use
            cursor.execute("DELETE FROM password_reset_tokens WHERE token = %s", (request.token,))
            connection.commit()

        return {"message": "Password reset successfully."}
    finally:
        connection.close()
