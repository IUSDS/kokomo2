from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
from utils.database import get_db_connection
from pymysql.cursors import DictCursor

# Initialize the router
user_details_route = APIRouter()

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"

# Define the UserResponse model
class UserResponse(BaseModel):
    member_id: int
    full_name: str
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
    company_name: str | None

@user_details_route.get("/user-details/", response_model=UserResponse)
async def get_user_details(
    email: str = Query(None), 
    username: str = Query(None)
):
    if not email and not username:
        raise HTTPException(
            status_code=400, 
            detail="Provide at least 'email' or 'username' to fetch details."
        )

    connection = None
    cursor = None

    query = """
        SELECT 
            member_id, 
            CONCAT(first_name, ' ', last_name) AS full_name, 
            membership_type, 
            points, 
            picture_url, 
            phone_number, 
            email_id, 
            address,
            emergency_contact,
            Emergency_Contact_Relationship,
            Emergency_Contact_Name,
            DL,
            spouse
        FROM 
            Members
        WHERE 
            (email_id = %s OR username = %s) 
            AND is_deleted = "N"
        LIMIT 1;
    """
    params = (email, username)

    try:
        connection = get_db_connection()
        cursor = connection.cursor(DictCursor)
        cursor.execute(query, params)
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="User not found.")
        
        # Fetch Emergency details
        cursor.execute("""
            SELECT ec_name AS emergency_name, ec_relationship AS emergency_relationship, 
                   ec_phone_number AS emergency_contact, ec_email AS emergency_email, 
                   spouse, spouse_email, spouse_phone_number AS spouse_phone
            FROM Member_Emergency_Details WHERE member_id = %s
        """, (member["member_id"],))
        emergency = cursor.fetchone() or {}
                        
        # Merge all data into a single response
        response_data = {**member, **emergency, }
        
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