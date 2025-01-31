from fastapi import APIRouter, HTTPException, Request, Response, Depends, Form
from pydantic import BaseModel
from utils.database import get_db_connection
from passlib.context import CryptContext

# Initialize router
validate_user_route = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt"""
    return pwd_context.hash(password)

@validate_user_route.post("/validate-user/")
async def validate_user(response: Response, username: str = Form(...), password: str = Form(...)):
    """
    Validates the user credentials against the database.
    """
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Query to fetch user credentials
            query = """
                SELECT pass, user_type 
                FROM Members 
                WHERE LOWER(username) = LOWER(%s) 
                AND is_deleted = "N"
            """
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            # Check if the user exists
            if not result:
                raise HTTPException(status_code=404, detail="User not found.")

            # Verify the hashed password
            if not pwd_context.verify(password, result["pass"]):
                raise HTTPException(status_code=401, detail="Invalid username or password.")

            return {
                "status": "SUCCESS",
                "user_type": result["user_type"],
                "message": "User authenticated successfully.",
            }

    except pymysql.MySQLError as e:
        print("Database error:", str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        connection.close()

@validate_user_route.post("/logout/")
async def logout(request: Request, response: Response):
    """
    Clears session data and logs the user out.
    """
    response.delete_cookie("kokomo_session")
    return {"status": "SUCCESS", "message": "Logged out successfully"}
