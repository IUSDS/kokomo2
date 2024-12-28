from fastapi import APIRouter, HTTPException, Form, Request
from passlib.context import CryptContext
from database import get_db_connection
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Request
import boto3
from botocore.exceptions import ClientError

# Initialize router
update_user_route = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"
ACCESS_POINT_ALIAS = "first-kokomo-access-y1pahkde96c1mfspxs7cbiaro94hyaps2a-s3alias"

# Initialize S3 client (using EC2 IAM role or environment variables for credentials)
s3_client = boto3.client("s3", region_name=S3_REGION)

# Function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@update_user_route.put("/user/")
async def update_user(
    request: Request,  # Access session via Request
    username: str = Form(..., description="The username of the user to update"),
    password: str = Form(None, description="The new password"),
    first_name: str = Form(None, description="The new first name"),
    last_name: str = Form(None, description="The new last name"),
    phone_number: str = Form(None, description="The new phone number"),
    address: str = Form(None, description="The new address"),
    picture_url: str = None # Optional file upload
    file: UploadFile = Form(None, description="The new picture URL"),  
):
    """
    Update user details. Fields left blank will retain their previous values.
    """
    # SQL to fetch existing values
    fetch_query = """
        SELECT pass, first_name, last_name, phone_number, address, picture_url
        FROM Members
        WHERE username = %s AND is_deleted = "N"
    """

    # SQL to update values
    update_query = """
        UPDATE Members
        SET pass = %s, first_name = %s, last_name = %s, 
            phone_number = %s, address = %s, picture_url = %s
        WHERE username = %s AND is_deleted = "N"
    """

    connection = get_db_connection()
    
    # Upload the file to S3 if provided
    picture_s3_url = None
    if file:
        file_content = await file.read()
        object_name = f"profile_pictures/{username}/{file.filename}"
        try:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,  # Correct bucket name usage
                    Key=object_name,
                    Body=file_content,
                    ContentType=file.content_type,
                )
            picture_s3_url = f"https://{ACCESS_POINT_ALIAS}.s3.{S3_REGION}.amazonaws.com/{object_name}"
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"S3 Upload error: {e.response['Error']['Message']}")

        # Determine final picture URL
        picture_url = picture_s3_url if picture_s3_url else picture_url
    try:
        with connection.cursor() as cursor:
            # Fetch existing user data
            cursor.execute(fetch_query, (username,))
            existing_data = cursor.fetchone()

            if not existing_data:
                raise HTTPException(status_code=404, detail="User not found.")

            # Determine values to update
            updated_password = hash_password(password) if password else existing_data["pass"]
            updated_first_name = first_name or existing_data["first_name"]
            updated_last_name = last_name or existing_data["last_name"]
            updated_phone_number = phone_number or existing_data["phone_number"]
            updated_address = address or existing_data["address"]
            updated_picture_url = picture_url or existing_data["picture_url"]

            # Execute update query
            cursor.execute(
                update_query,
                (
                    updated_password,
                    updated_first_name,
                    updated_last_name,
                    updated_phone_number,
                    updated_address,
                    updated_picture_url,
                    username,
                ),
            )

            connection.commit()

            # Save updated fields in the session
            request.session["username"] = username
            request.session["first_name"] = updated_first_name
            request.session["last_name"] = updated_last_name
            request.session["picture_url"] = updated_picture_url

            return {
                "status": "success",
                "message": "User details updated successfully.",
                "updated_fields": {
                    "password": "Updated" if password else "Unchanged",
                    "first_name": updated_first_name,
                    "last_name": updated_last_name,
                    "phone_number": updated_phone_number,
                    "address": updated_address,
                    "picture_url": updated_picture_url,
                },
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        connection.close()
