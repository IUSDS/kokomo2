from fastapi import APIRouter, HTTPException, Request, Response
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

@validate_user_route.get("/", response_model=UserResponse)
async def get_user_details(username: str, request: Request):
    """
    Retrieves user details and checks session validity using the `kokomo_session` cookie.
    """
    # Debugging: Log the received username
    print(f"Received username: {username}")

    # Check session validity
    session = request.session
    session_username = session.get("username")
    if not session_username:
        raise HTTPException(status_code=401, detail="SESSION EXPIRED OR INVALID.")

    # Debugging: Log the session username
    print(f"Session username: {session_username}")

    if session_username != username:
        raise HTTPException(status_code=403, detail="UNAUTHORIZED ACCESS.")

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

            # Debugging: Log the query result
            print(f"Query result: {result}")

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
        

@validate_user_route.get("/", response_model=UserResponse)
async def get_user_details(username: str, request: Request):
    """
    Retrieves user details and checks session validity using the `kokomo_session` cookie.
    """
    # Check session validity
    session = request.session  # Explicitly use session variable
    session_username = session.get("username")
    if not session_username:
        raise HTTPException(status_code=401, detail="SESSION EXPIRED OR INVALID.")

    # Ensure the session username matches the requested username
    if session_username != username:
        raise HTTPException(status_code=403, detail="UNAUTHORIZED ACCESS.")

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
