from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
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
    full_name: str
    membership_type: str
    points: int
    picture_url: str
    phone_number: int
    email_id: str
    address: str
    emergency_contact: int
    Emergency_Contact_Relationship: str
    Emergency_Contact_Name: str 
    DL: str
    spouse: str 

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

        # Debugging: Print raw result
        print("Query Result:", result)

        # Ensure correct data types and prevent possible None values
        try:
            result["member_id"] = int(result["member_id"])
            result["points"] = int(result["points"])
            result["emergency_contact"] = int(result["emergency_contact"])
            result["phone_number"] = int(result["phone_number"])

            # Handling CHAR fields as string explicitly
            result["Emergency_Contact_Relationship"] = str(result.get("Emergency_Contact_Relationship", ""))
            result["Emergency_Contact_Name"] = str(result.get("Emergency_Contact_Name", ""))
            result["DL"] = str(result.get("DL", ""))
            result["spouse"] = str(result.get("spouse", ""))

            # Generate the picture URL
            picture_url = result.get("picture_url")
            if picture_url:
                image_name = picture_url.split("/")[-1]  # Extract image filename from URL
                result["picture_url"] = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/profile_pictures/{username}/{image_name}"

        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Data type error for 'member_id' or 'points': {str(e)}"
            )

        return {
            "member_id": result["member_id"],
            "full_name": result["full_name"],
            "membership_type": result["membership_type"],
            "points": result["points"],
            "picture_url": result["picture_url"],
            "phone_number": result["phone_number"],
            "email_id": result["email_id"],
            "address": result["address"],
            "emergency_contact": result["emergency_contact"],
            "Emergency_Contact_Relationship": result["Emergency_Contact_Relationship"],
            "Emergency_Contact_Name": result["Emergency_Contact_Name"],
            "DL": result["DL"],
            "spouse": result["spouse"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()