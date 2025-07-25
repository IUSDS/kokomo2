from fastapi import HTTPException, Depends, Form, APIRouter
from pydantic import BaseModel, EmailStr
from utils.db_util import get_db_connection
import secrets
from datetime import datetime, timedelta
from pymysql.err import IntegrityError
from emails.forgot_pass_email import send_reset_email
from utils.password_util import hash_password

forgot_password_route = APIRouter()

# Request schemas
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Endpoint to handle forgot password requests
@forgot_password_route.post("/forgot-password")
def forgot_password(email: str = Form(...)):
    # Generate a secure token
    token = secrets.token_hex(16)  # Generates a 32-character hexadecimal string
    expiry_time = datetime.now() + timedelta(minutes=30)  # Token valid for 30 mins

    # Check if the email exists in the database
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if email exists in the database
            query = "SELECT member_id FROM Members WHERE email_id = %s"

            cursor.execute(query, (email,))
            user = cursor.fetchone()
            member_id = user['member_id']

            # Store the token in the database
            insert_query = (
                """
                INSERT INTO Password_Reset_Tokens (member_id, email, token, expiry_time)
                VALUES (%s, %s, %s, %s)
                """
            )
            cursor.execute(insert_query, (member_id, email, token, expiry_time))
            connection.commit()

            send_reset_email(email, token)
        return {"message": "Password reset email sent successfully."}

    except IntegrityError as e:
        print(f"IntegrityError during password reset: {str(e)}")
        raise HTTPException(status_code=400, detail="A unique constraint was violated. Please try again.")

    except HTTPException as e:
        # Re-raise explicit HTTPExceptions (like the 404 for "Email not found")
        raise e

    except Exception as e:
        print(f"An unexpected error occurred in forgot_password: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error occurred during password reset request.")

    finally:
        if connection:
            connection.close()


# Endpoint to reset the password
@forgot_password_route.post("/reset-password")
def reset_password(request: ResetPasswordRequest):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Validate the token
            cursor.execute(
                "SELECT email, expiry_time FROM Password_Reset_Tokens WHERE token = %s",
                (request.token,),
            )
            token_data = cursor.fetchone()
            if not token_data:
                raise HTTPException(status_code=404, detail="Invalid or expired token.")

            # Check token expiry
            if datetime.now() > token_data["expiry_time"]:
                raise HTTPException(status_code=400, detail="Token has expired.")

            # Hash the new password before updating it in the database
            hashed_password = hash_password(request.new_password)

            # Update the user's password
            cursor.execute(
                "UPDATE Members SET pass = %s WHERE email_id = %s",
                (hashed_password, token_data["email"]),
            )
            connection.commit()

            # Delete the token after use
            cursor.execute("DELETE FROM Password_Reset_Tokens WHERE token = %s", (request.token,))
            connection.commit()

        return {"message": "Password reset successfully."}
    finally:
        connection.close()