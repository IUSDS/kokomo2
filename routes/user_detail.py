from fastapi import APIRouter, HTTPException, Query, Depends
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
    phone_number: str
    email_id: str
    address: str

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
            address
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

        # Ensure correct data types
        try:
            result["member_id"] = int(result["member_id"])
            result["points"] = int(result["points"])

            # Get the image name from the DB
            picture_url = result["picture_url"]
            image_name = picture_url.split("/")[-1]

            result["picture_url"] = "https://" + S3_BUCKET_NAME + ".s3." + S3_REGION + ".amazonaws.com/profile_pictures/" + username + "/" + image_name
            print("Processed Picture URL:", result["picture_url"])

        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Data type error for 'member_id' or 'points': {str(e)}"
            )

        # You can also call the list_s3_objects function to list all objects from the S3 bucket
        s3_objects = list_s3_objects()
        print("S3 Objects:", s3_objects)

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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()