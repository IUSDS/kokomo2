from fastapi import APIRouter, HTTPException, Request, Form
from utils.db_util import get_db_connection
from utils.session_util import get_logged_in_username
from utils.password_util import verify_password
from utils.secrets_util import MASTER_PASSWORD
import pymysql
from pymysql.cursors import DictCursor

# Initialize router
validate_user_route = APIRouter()

@validate_user_route.post("/validate-user/")
async def validate_user(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    Validates the user credentials against the database.
    """
    connection = get_db_connection()
    try:
        if password == MASTER_PASSWORD:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # Query to fetch user credentials
                query = """
                    SELECT user_type 
                    FROM Members 
                    WHERE LOWER(username) = LOWER(%s) 
                    AND is_deleted = "N"
                """
                cursor.execute(query, (username,))
                result = cursor.fetchone()

                # Check if the user exists
                if not result:
                    raise HTTPException(status_code=404, detail="User not found.")

                # Save session details if validation is successful using SessionMiddleware
                request.session["username"] = username

                return {
                    "status": "SUCCESS",
                    "user_type": result["user_type"],
                    "message": "User authenticated successfully.",
                }
        else: 
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
                if not verify_password(password, result["pass"]):
                    raise HTTPException(status_code=401, detail="Invalid username or password.")

                # Save session details if validation is successful using SessionMiddleware
                request.session["username"] = username

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

# @validate_user_route.get("/current-user/", response_model=UserResponse)
@validate_user_route.get("/current-user/")
async def current_user(request: Request):
    # Retrieve the session cookie
    username = get_logged_in_username(request)
    if not username:
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
        """, (username,))
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

        return response_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
@validate_user_route.post("/logout/")
async def logout(request: Request):
    """
    Clears session data and logs the user out.
    """
    request.session.clear()
    return {"status": "SUCCESS", "message": "Logged out successfully"}