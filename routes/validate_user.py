from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from database import get_db_connection
from models import User, UserResponse
import pymysql

validate_user_route = APIRouter()

@validate_user_route.post("/")
async def validate_user(user: User, request: Request, response: Response):
    """
    Validates the user credentials and manages session via cookies.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Query to validate username and password
            query = "SELECT pass, user_type FROM Members WHERE username = %s"
            cursor.execute(query, (user.USER,))
            result = cursor.fetchone()

            if not result:
                return {"status": "invalid username or password"}

            stored_password = result["pass"].strip()
            user_type = result["user_type"]

            # Verify password
            if stored_password != user.password.strip():
                return {"status": "invalid password"}

            # Save session details
            request.session["username"] = user.USER
            request.session["user_type"] = user_type

            # Set additional session cookies if needed
            response.set_cookie(key="username", value=user.USER, httponly=True)

            # Return response based on user type
            if user_type == "User":
                return {"status": "success", "user_type": "user"}
            elif user_type == "Admin":
                return {"status": "success", "user_type": "admin"}
            else:
                return {"status": "error", "message": "Invalid user_type in database"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        connection.close()


@validate_user_route.get("/", response_model=UserResponse)
async def get_user_details(username: str, request: Request):
    """
    Retrieves user details and checks session validity.
    """
    # Check session validity
    session_username = request.session.get("username")
    if not session_username:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")

    # Ensure the session username matches the requested username
    if session_username != username:
        raise HTTPException(status_code=403, detail="Unauthorized access.")

    query = """
        SELECT member_id, CONCAT(first_name, ' ', last_name) AS full_name, 
               membership_type, points, picture_url, phone_number, address, email_id, username
        FROM Members
        WHERE username = %s AND is_deleted = "N"
        LIMIT 1
    """
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="User not found.")

            return {
                "member_id": result["member_id"],
                "full_name": result["full_name"],
                "membership_type": result["membership_type"],
                "points": result["points"],
                "picture_url": result["picture_url"],
                "phone_number": result["phone_number"],
                "email_id": result["email_id"],
                "address": result["address"],
            }

    except pymysql.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {e}")

    finally:
        connection.close()
