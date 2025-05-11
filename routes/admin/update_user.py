from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from utils.db_util import get_db_connection
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, EmailStr
from typing import Optional, Union

# Initialize the router
update_user_route = APIRouter()

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"
ACCESS_POINT_ALIAS = "first-kokomo-access-y1pahkde96c1mfspxs7cbiaro94hyaps2a-s3alias"

# Initialize S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

DEFAULT_PICTURE_URL = (
    "https://image-bucket-kokomo-yacht-club.s3.ap-southeast-2.amazonaws.com/"
    "profile_pictures/default.png"
)

@update_user_route.put("/update/user/")
async def update_user(
    username: str = Form(...),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    phone_number: Optional[int] = Form(None),
    member_address1: Optional[str] = Form(None),
    member_address2: Optional[str] = Form(None),
    member_city: Optional[str] = Form(None),
    member_state: Optional[str] = Form(None),
    member_zip: Optional[int] = Form(None),    
    membership_type: Optional[str] = Form(None),
    points: Optional[int] = Form(None),
    file: Optional[Union[UploadFile, str]] = File(None),
    # emergency_contact: int = Form(None),
    # emergency_email: EmailStr = Form(None),
    # emergency_relationship: str = Form(None),
    # emergency_name: str = Form(None),
    dl: Optional[str] = Form(None),
    # spouse: str = Form(None),
    # spouse_email: EmailStr = Form(None),
    # spouse_phone: int = Form(None),
    company_name: Optional[str] = Form(None),
    ):
    """
    Update user details. Fields left blank will retain their previous values.
    """
    connection = get_db_connection()
    
    fetch_query ="""
            SELECT first_name, last_name, phone_number, member_address1, member_address2, member_city, 
                   member_state, member_zip, email_id, membership_type, points, referral_information, company_name, 
                   picture_url, dl FROM Members WHERE username = %s AND is_deleted = 'N' LIMIT 1;
        """

    update_query = """
        UPDATE Members
        SET first_name = COALESCE(%s, first_name), last_name = COALESCE(%s, last_name), phone_number = COALESCE(%s, phone_number), 
            member_address1 = COALESCE(%s, member_address1), member_address2 = COALESCE(%s, member_address2), member_city = COALESCE(%s, member_city), 
            member_state = COALESCE(%s, member_state), member_zip = COALESCE(%s, member_zip), picture_url = COALESCE(%s, picture_url), 
            referral_information = COALESCE(%s, referral_information), company_name = COALESCE(%s, company_name), points = COALESCE(%s, points), membership_type = COALESCE(%s, membership_type), 
            dl = COALESCE(%s, dl), email_id = COALESCE(%s, email_id)
        WHERE username = %s AND is_deleted = 'N'
    """
    
    # Determine the picture_url update value
    picture_s3_url = None
    if file is None:
        # File not provided: leave picture_url unchanged (pass None so COALESCE uses existing value)
        picture_s3_url = None
    elif isinstance(file, UploadFile):
        # A file was provided; attempt to upload it to S3
        file_content = await file.read()
        object_name = f"profile_pictures/{username}/{file.filename}"
        try:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=object_name,
                Body=file_content,
                ContentType=file.content_type,
            )
            picture_s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{object_name}"
        except ClientError as e:
            raise HTTPException(
                status_code=500, 
                detail=f"S3 Upload error: {e.response['Error']['Message']}"
            )
    elif isinstance(file, str) and file == "":
        # An empty string was sent for file; update with default picture URL.
        picture_s3_url = DEFAULT_PICTURE_URL

    try:
        with connection.cursor() as cursor:
            # Fetch existing user data
            cursor.execute(fetch_query, (username,))
            existing_data = cursor.fetchone()

            if not existing_data:
                raise HTTPException(status_code=404, detail="User not found.")

            # Ensure fields don't default to "string" or 0 but retain None
            first_name = None if first_name == "string" else first_name
            last_name = None if last_name == "string" else last_name
            phone_number = None if phone_number == 0 else phone_number
            member_address1 = None if member_address1 == "string" else member_address1
            member_address2 = None if member_address2 == "string" else member_address2
            member_city = None if member_city == "string" else member_city
            member_state = None if member_state == "string" else member_state
            membership_type = None if membership_type == "string" else membership_type
            company_name = None if company_name == "string" else company_name
            dl = None if dl == "string" else dl
            
            cursor.execute(update_query, (
                first_name, last_name, phone_number, member_address1, member_address2, member_city, 
                member_state, member_zip, picture_s3_url, existing_data['referral_information'], 
                company_name, points, membership_type, dl, existing_data['email_id'], username
            ))
        
        connection.commit()
        return {"status": "success", "message": "User details updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        if connection:
            connection.close()