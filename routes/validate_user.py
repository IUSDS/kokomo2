from fastapi import APIRouter, HTTPException, Request, Response, Depends, Form
from pydantic import BaseModel
from utils.database import get_db_connection
from passlib.context import CryptContext
import pymysql
from pymysql.cursors import DictCursor
from typing import Optional
from starlette.middleware.sessions import SessionMiddleware  # Ensure correct import

# Initialize router
validate_user_route = APIRouter()

class UserResponse(BaseModel):
    member_id: int
    username: str
    password: str
    first_name: str
    last_name: str
    phone_number: int
    member_address1: str
    member_address2: Optional[str]
    member_city: str
    member_state: str
    member_zip: int
    #email_id: EmailStr
    membership_type: str
    points: int
    referral_information: Optional[str]
    picture_url: Optional[str]
    emergency_contact: Optional[int]
    emergency_relationship: Optional[str]
    emergency_name: Optional[str]
    dl: Optional[str]
    spouse: Optional[str]
    spouse_email: Optional[EmailStr]
    spouse_phone: Optional[int]
    company_name: Optional[str]

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

            # Save session details if validation is successful using SessionMiddleware
            # Setting session data for user, stored in request.session
            # Session expires in 30 minutes {expires= (datetime.utcnow() + timedelta(minutes=30)}
            response.set_cookie(key="kokomo_session", value=username, httponly=True, )
            
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

@validate_user_route.get("/current-user/", response_model=UserResponse)
async def current_user(request: Request):
    # Retrieve the session cookie
    kokomo_session = request.cookies.get("kokomo_session")
    if not kokomo_session:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
    
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(DictCursor)
        
        # Query to fetch member details based on the session (username)
        cursor.execute("""
            SELECT member_id, username, pass AS password, first_name, last_name, phone_number, 
                   member_address1, member_address2, member_city, member_state, member_zip, email_id, 
                   membership_type, points, referral_information, picture_url, dl, company_name
            FROM Members 
            WHERE LOWER(username) = LOWER(%s) AND is_deleted = 'N'
            LIMIT 1
        """, (kokomo_session,))
        member = cursor.fetchone()
        if not member:
            raise HTTPException(status_code=401, detail="Session expired or invalid.")
        
        # Query to fetch emergency details for the member
        cursor.execute("""
            SELECT ec_name AS emergency_name, ec_relationship AS emergency_relationship, 
                   ec_phone_number AS emergency_contact,
                   spouse, spouse_email, spouse_phone_number AS spouse_phone
            FROM Member_Emergency_Details 
            WHERE member_id = %s
        """, (member["member_id"],))
        emergency = cursor.fetchone() or {}
        
        # Merge member and emergency data into a single response
        response_data = {**member, **emergency}
        # Ensure all fields defined in the UserResponse model are present
        for key in UserResponse.__annotations__.keys():
            if key not in response_data:
                response_data[key] = None
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
@validate_user_route.post("/logout/")
async def logout(request: Request, response: Response):
    """
    Clears session data and logs the user out.
    """
    response.delete_cookie("kokomo_session")
    return {"status": "SUCCESS", "message": "Logged out successfully"}
