from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
from database import get_db_connection
from pymysql.cursors import DictCursor

# Initialize the router
user_details_route = APIRouter()

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"

# Define the UserResponse model
class UserResponse(BaseModel):
    member_id: int
    username: str
    password: str
    first_name: str
    last_name: str
    phone_number: int
    member_address1: str
    member_address2: str | None
    member_city: str
    member_state: str
    member_zip: int
    email_id: EmailStr
    membership_type: str
    points: int
    referral_information: str | None
    picture_url: str | None
    emergency_contact: int | None
    emergency_email: EmailStr | None
    emergency_relationship: str | None
    emergency_name: str | None
    dl: str | None
    spouse: str | None
    spouse_email: EmailStr | None
    spouse_phone: int | None
    child_name: str | None
    child_dob: str | None
    child_email: EmailStr | None
    child_phone: int | None
    company_name: str | None

@user_details_route.get("/user-details/", response_model=UserResponse)
async def get_user_details(username: str = Query(...)):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(DictCursor)
        
        # Fetch Member details
        cursor.execute("""
            SELECT member_id, username, pass AS password, first_name, last_name, phone_number, 
                   member_address1, member_address2, member_city, member_state, member_zip, email_id, 
                   membership_type, points, referral_information, picture_url, dl, company_name
            FROM Members WHERE username = %s AND is_deleted = 'N'
        """, (username,))
        member = cursor.fetchone()
        if not member:
            raise HTTPException(status_code=404, detail="User not found.")
        
        # Fetch Emergency details
        cursor.execute("""
            SELECT ec_name AS emergency_name, ec_relationship AS emergency_relationship, 
                   ec_phone_number AS emergency_contact, ec_email AS emergency_email, 
                   spouse, spouse_email, spouse_phone_number AS spouse_phone
            FROM Member_Emergency_Details WHERE member_id = %s
        """, (member["member_id"],))
        emergency = cursor.fetchone() or {}
        
        # Fetch Children details
        cursor.execute("""
            SELECT child_name, child_dob, child_email, child_phone_number AS child_phone
            FROM Member_Childern_Details WHERE member_id = %s
        """, (member["member_id"],))
        children = cursor.fetchone() or {}
        
        # Convert date fields to string safely
        if "child_dob" in children and children["child_dob"]:
            children["child_dob"] = str(children["child_dob"])
        
        # Merge all data into a single response
        response_data = {**member, **emergency, **children}
        
        # Ensure None values for missing fields
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