from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
from utils.database import get_db_connection
from pymysql.cursors import DictCursor
from typing import Optional

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
    member_address2: Optional[str]
    member_city: str
    member_state: str
    member_zip: int
    email_id: EmailStr
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
                   ec_phone_number AS emergency_contact, 
                   spouse, spouse_email, spouse_phone_number AS spouse_phone
            FROM Member_Emergency_Details WHERE member_id = %s
        """, (member["member_id"],))
        emergency = cursor.fetchone() or {}
       
        # Merge all data into a single response
        response_data = {**member, **emergency}
        
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
