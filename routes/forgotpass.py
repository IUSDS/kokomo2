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
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if email exists
            query = "SELECT member_id FROM Members WHERE email_id = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(
                    status_code=400, 
                    detail={
                        "message": "Email not found in our records",
                        "start_timer": False
                    }
                )
            
            member_id = user['member_id']
            
            # Check for recent requests using created_at
            recent_request_query = """
                SELECT created_at FROM Password_Reset_Tokens 
                WHERE member_id = %s AND expiry_time > NOW()
                ORDER BY created_at DESC 
                LIMIT 1
            """
            cursor.execute(recent_request_query, (member_id,))
            recent_request = cursor.fetchone()
            
            if recent_request:
                time_since_request = datetime.now() - recent_request['created_at']
                seconds_elapsed = int(time_since_request.total_seconds())
                
                if seconds_elapsed < 60:
                    remaining_time = 60 - seconds_elapsed
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "message": f"Please wait {remaining_time} seconds before requesting another reset",
                            "start_timer": True,
                            "remaining_time": remaining_time * 1000
                        }
                    )
            
            # Step 3: Clean up old tokens and create new one
            delete_old_tokens = "DELETE FROM Password_Reset_Tokens WHERE member_id = %s"
            cursor.execute(delete_old_tokens, (member_id,))
            
            token = secrets.token_hex(16)
            expiry_time = datetime.now() + timedelta(minutes=30)
            current_time = datetime.now()
            
            insert_query = """
                INSERT INTO Password_Reset_Tokens (member_id, email, token, expiry_time, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (member_id, email, token, expiry_time, current_time))
            connection.commit()
            
            send_reset_email(email, token)
            
            return {
                "message": "Password reset email sent successfully",
                "start_timer": True,
                "remaining_time": 60000
            }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in forgot_password: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "message": "Internal server error",
            "start_timer": False
        })
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