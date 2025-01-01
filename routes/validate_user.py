from fastapi import APIRouter, HTTPException, Request, Response, Depends
from pydantic import BaseModel
import pymysql
from database import get_db_connection
from starlette.middleware.sessions import SessionMiddleware  # Ensure correct import

# Define models
class User(BaseModel):
    username: str
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

@validate_user_route.post("/validate-user/")
async def validate_user(username: str, password: str, response: Response):
    """
    Validates the user credentials against the database.
    """
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Prepare the query to fetch user credentials
            query = """
                SELECT pass, user_type 
                FROM Members WHERE LOWER(username) = LOWER(%s) 
                AND is_deleted = "N"
            """
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            # Debugging logs
            print("Query executed:", query)
            print("Query parameters:", username)
            print("Result fetched:", result)

            # Check if the user exists
            if not result:
                raise HTTPException(status_code=404, detail="User not found.")

            # Check if the provided password matches
            if result["pass"] != password:
                raise HTTPException(status_code=401, detail="Invalid username or password.")

            # Save session details if validation is successful using SessionMiddleware
            # Setting session data for user, stored in request.session
            response.set_cookie(key="kokomo_session", value=username, httponly=True)

            return {
                "status": "SUCCESS",
                "user_type": result["user_type"],
                "message": "User authenticated successfully.",
            }

    except pymysql.MySQLError as e:
        # Catch and log any database-related errors
        print("Database error:", str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        # Ensure the database connection is closed
        connection.close()


@validate_user_route.get("/current-user/")
async def current_user(request: Request):
    """
    Retrieves the current user based on session.
    """
    kokomo_session = request.cookies.get("kokomo_session")
    if not kokomo_session:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
    
    print("Received kokomo_session:", kokomo_session)  # Debugging log

    # Query database for user details based on kokomo_session
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT member_id, CONCAT(first_name, ' ', last_name) AS full_name,
                       membership_type, points, picture_url, phone_number, address, email_id
                FROM Members
                WHERE LOWER(username) = LOWER(%s) AND is_deleted = "N"
                LIMIT 1
            """
            cursor.execute(query, (kokomo_session,))
            result = cursor.fetchone()
            
            # Log for debugging purpose
            print(f"Query result: {result}")
        
            if not result:
                raise HTTPException(status_code=401, detail="Session expired or invalid.")

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
    
    except pymysql.MySQLError as e:
        print("Database error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")
    
    finally:
        connection.close()

@validate_user_route.post("/logout/")
async def logout(request: Request, response: Response):
    """
    Clears session data and logs the user out.
    """
    response.delete_cookie("kokomo_session")
    return {"status": "SUCCESS", "message": "Logged out successfully"}
