from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from utils.database import get_db_connection
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, EmailStr

# Initialize the router
update_user_route = APIRouter()

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"
ACCESS_POINT_ALIAS = "first-kokomo-access-y1pahkde96c1mfspxs7cbiaro94hyaps2a-s3alias"

# Initialize S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

@update_user_route.put("/update/user/")
async def update_user(
    username: str = Form(...),
    first_name: str = Form(None),
    last_name: str = Form(None),
    phone_number: int = Form(None),
    member_address1: str = Form(None),
    member_address2: str = Form(None),
    member_city: str = Form(None),
    member_state: str = Form(None),
    member_zip: int = Form(None),    
    membership_type: str = Form(None),
    points: int = Form(None),
    file: UploadFile = File(None),
    # emergency_contact: int = Form(None),
    # emergency_email: EmailStr = Form(None),
    # emergency_relationship: str = Form(None),
    # emergency_name: str = Form(None),
    dl: str = Form(None),
    # spouse: str = Form(None),
    # spouse_email: EmailStr = Form(None),
    # spouse_phone: int = Form(None),
    company_name: str = Form(None),

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
    
    picture_s3_url = None
    if file:
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
            raise HTTPException(status_code=500, detail=f"S3 Upload error: {e.response['Error']['Message']}")

    try:
        with connection.cursor() as cursor:
            # Fetch existing user data
            cursor.execute(fetch_query, (username,))
            existing_data = cursor.fetchone()

            if not existing_data:
                raise HTTPException(status_code=404, detail="User not found.")
            
            cursor.execute(update_query, (
                first_name, last_name, phone_number, member_address1, member_address2, member_city, 
                member_state, member_zip, picture_s3_url, existing_data['referral_information'], company_name, points, membership_type, 
                dl, existing_data['email_id'], username
            ))
        
        connection.commit()
        return {"status": "success", "message": "User details updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        if connection:
            connection.close()