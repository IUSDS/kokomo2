from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from utils.database import get_db_connection
import boto3
from botocore.exceptions import ClientError

# Initialize router
update_user_route = APIRouter()

# Password hashing context
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"
ACCESS_POINT_ALIAS = "first-kokomo-access-y1pahkde96c1mfspxs7cbiaro94hyaps2a-s3alias"

# Initialize S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

# Function to hash passwords
#def hash_password(password: str) -> str:
    #return pwd_context.hash(password)

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
    fetch_query = """
        SELECT pass, first_name, last_name, phone_number, address, picture_url, emergency_contact, Emergency_Contact_Relationship, Emergency_Contact_Name, DL, spouse
        FROM Members
        WHERE username = %s AND is_deleted = "N"
    """

    update_query = """
        UPDATE Members
        SET pass = %s, first_name = %s, last_name = %s, 
            phone_number = %s, address = %s, picture_url = %s, emergency_contact = %s, 
            Emergency_Contact_Relationship = %s, Emergency_Contact_Name = %s, DL= %s, spouse = %s
        WHERE username = %s AND is_deleted = "N"
    """
    # Upload the file to S3 if provided
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

            # Determine values to update
            updated_password = password or existing_data["pass"]
            updated_first_name = first_name or existing_data["first_name"]
            updated_last_name = last_name or existing_data["last_name"]
            updated_phone_number = phone_number or existing_data["phone_number"]
            updated_address = address or existing_data["address"]
            updated_picture_url = picture_s3_url or existing_data["picture_url"]
            updated_ec = emergency_contact or existing_data["emergency_contact"]
            updated_ec_relationship = Emergency_Contact_Relationship or existing_data["Emergency_Contact_Relationship"]
            updated_ec_name = Emergency_Contact_Name or existing_data["Emergency_Contact_Name"]
            updated_dl = DL or existing_data["DL"]
            updated_spouse = spouse or existing_data["spouse"]

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
                    updated_ec,
                    updated_ec_relationship,
                    updated_ec_name,
                    updated_dl,
                    updated_spouse,
                    username,  # Username to target the correct user
                ),
            )

            connection.commit()

            return {
                "status": "success",
                "message": "User details updated successfully.",
                "updated_fields": {
                    "password": "Updated" if password else "Not updated",
                    "first_name": updated_first_name,
                    "last_name": updated_last_name,
                    "phone_number": updated_phone_number,
                    "address": updated_address,
                    "picture_url": updated_picture_url,
                    "emergency_contact": updated_ec,
                    "Emergency_Contact_Relationship": updated_ec_relationship,
                    "Emergency_Contact_Name": updated_ec_name,
                    "DL": updated_dl,
                    "spouse": updated_spouse,
                },
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        connection.close()
