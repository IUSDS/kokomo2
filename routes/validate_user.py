from fastapi import APIRouter, HTTPException, Request, Response, Depends
from pydantic import BaseModel
from database import get_db_connection
import pymysql

# Define models
class User(BaseModel):
    USER: str
    password: str


class UserResponse(BaseModel):
    member_id: int
    full_name: str
    membership_type: str
    points: int
    picture_url: str
    phone_number: str
    email_id: str
    address: str


# Initialize router
validate_user_route = APIRouter()


@validate_user_route.post("/", tags=["Validate User"])
async def validate_user(user: User, request: Request, response: Response):
    """
    Validates the user credentials and saves session details via cookies.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Query to validate username
            query = "SELECT pass, user_type FROM Members WHERE LOWER(username) = LOWER(%s)"
            cursor.execute(query, (user.USER,))
            result = cursor.fetchone()

            if not result:
                return {"status": "USER NOT FOUND"}

            stored_password = result["pass"].strip()
            user_type = result["user_type"]

            # Verify password
            if stored_password != user.password.strip():
                return {"status": "INVALID PASSWORD"}

            # Save session details
            session = request.session
            session["username"] = user.USER
            session["user_type"] = user_type

            # Set session cookie
            response.set_cookie(key="kokomo_session", value=user.USER, httponly=True)

            # Return response based on user type
            if user_type == "User":
                return {"status": "SUCCESS", "user_type": "USER"}
            elif user_type == "Admin":
                return {"status": "SUCCESS", "user_type": "ADMIN"}
            else:
                return {"status": "ERROR", "message": "Invalid user_type in database"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        connection.close()


@validate_user_route.get("/", response_model=UserResponse, tags=["Validate User"])
async def get_user_details(request: Request):
    """
    Retrieves user details from session and database. This endpoint does not require parameters
    and relies on session data set during the POST request.
    """
    # Retrieve username from session
    session = request.session
    username = session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="SESSION EXPIRED OR INVALID.")

    query = """
        SELECT member_id, CONCAT(first_name, ' ', last_name) AS full_name, 
               membership_type, points, picture_url, phone_number, address, email_id, username
        FROM Members
        WHERE LOWER(username) = LOWER(%s) AND is_deleted = "N"
        LIMIT 1
    """
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="USER NOT FOUND.")

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
