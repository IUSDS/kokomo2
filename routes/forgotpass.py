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
    reset_link = f"https://api.kokomoyachtclub.vip/reset-password?token={token}"

    subject = "Password Reset Request"
    body_text = f"""Dear User,

        You have requested to reset your password. Click the link below to reset your password:
        {reset_link}

        If you didn't request this, please ignore this email.

        Best regards,
        Kokomo Yacht Club Team
        """
    print(body_text)
    body_html = f"""
    <html>
    <body>
        <p>Dear User,</p>
        <p>You have requested to reset your password. Click the link below to reset your password:</p>
        <a href="{reset_link}">{reset_link}</a>
        <p>If you didn't request this, please ignore this email.</p>
        <p>Best regards,<br>Kokomo Yacht Club Team</p>
    </body>
    </html>
    """
    print(body_html)

    # SMTP configuration
    sender_email = "info@kokomoyachtclub.vip"
    smtp_host = "email-smtp.ap-southeast-2.amazonaws.com"
    smtp_port = 587  # Use port 587 for STARTTLS
    smtp_username = "AKIAXKPUZZCOOVVEAYFO"  # Replace with your SMTP username
    smtp_password = "BHKOxcPTOlHVjTYDBOTOsVN5wRN7fNiTHanieVM4a5i1"  # Replace with your SMTP password
    print("Parsed")
    try:
        # Create the email content
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = email

        # Add plain text and HTML parts
        message.attach(MIMEText(body_text, "plain"))
        message.attach(MIMEText(body_html, "html"))

        # Connect to SMTP server
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  # Upgrade to secure connection
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, email, message.as_string())

        print(f"Password reset email sent to {email}.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Endpoint to handle forgot password requests
@forgot_password_route.post("/forgot-password")
def forgot_password(email: str = Form(...)):
    # Generate a secure token
    token = secrets.token_hex(16)  # Generates a 32-character hexadecimal string
    expiry_time = datetime.utcnow() + timedelta(hours=0.5)  # Token valid for 30 mins
    print("Right before DB")
    # Check if the email exists in the database
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if email exists in the database
            cursor.execute("SELECT email_id FROM Members WHERE email_id = %s", (email,))
            user = cursor.fetchone()
            print(user)
            if not user:
                raise HTTPException(status_code=404, detail="Email not found.")

            # Store the token in the database
            cursor.execute(
                "INSERT INTO password_reset_tokens (email, token, expiry_time) VALUES (%s, %s, %s)",
                (email, token, expiry_time),
            )
            connection.commit()
            print("Right after DB")
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
            if datetime.utcnow() > token_data["expiry_time"]:
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
