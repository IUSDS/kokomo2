from fastapi import FastAPI, HTTPException, Depends, Form, APIRouter
from pydantic import BaseModel, EmailStr
from database import get_db_connection
from datetime import datetime, timedelta
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
    reset_link = f"http://127.0.0.1:8000/reset-password?token={token}"
    
    subject = "Password Reset Request"
    body = f"""Dear User,

    You have requested to reset your password. Click the link below to reset your password:
    {reset_link}

    If you didn't request this, please ignore this email.

    Best regards,
    Kokomo Yacht Club Team
    """
    message = f"Subject: {subject}\n\n{body}"

    # Replace these with your email configuration
    sender_email = "kokomocharters@icloud.com"
    sender_password = "your-email-password"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message)
            print(f"Password reset email sent to {email}.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Endpoint to handle forgot password requests
@forgot_password_route.post("/forgot-password")
def forgot_password(email: str = Form(...)):
    # Generate a secure token
    token = secrets.token_hex(16)  # Generates a 32-character hexadecimal string
    expiry_time = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour

    # Check if the email exists in the database
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if email exists in the database
            cursor.execute("SELECT email FROM visitors WHERE email = %s", (request.email,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="Email not found.")

            # Generate a secure token
            token = secrets.token_hex(16)
            expiry_time = datetime.utcnow() + timedelta(hours=1)

            # Store the token in the database
            cursor.execute(
                "INSERT INTO password_reset_tokens (email, token, expiry_time) VALUES (%s, %s, %s)",
                (request.email, token, expiry_time),
            )
            connection.commit()

            # Send the reset email
            send_reset_email(request.email, token)

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
                "UPDATE visitors SET password = %s WHERE email = %s",
                (request.new_password, token_data["email"]),
            )
            connection.commit()

            # Delete the token after use
            cursor.execute("DELETE FROM password_reset_tokens WHERE token = %s", (request.token,))
            connection.commit()

        return {"message": "Password reset successfully."}
    finally:
        connection.close()
