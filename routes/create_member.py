from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Response
from pydantic import EmailStr
from database import get_db_connection
from botocore.exceptions import ClientError
import boto3

create_member_route = APIRouter()

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"
ACCESS_POINT_ALIAS = "first-kokomo-access-y1pahkde96c1mfspxs7cbiaro94hyaps2a-s3alias"

# Initialize S3 client (assume EC2 instance role or environment variables for credentials)
s3_client = boto3.client("s3", region_name=S3_REGION)

def save_to_session(response: Response, key: str, value: str):
    """Save data into secure cookies for session management."""
    response.set_cookie(key=key, value=value, httponly=True, max_age=3600)  # 1 hour validity


# Endpoint to validate username and email
@create_member_route.get("/validate-member/")
async def validate_member(username: str = None, email_id: str = None):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if username exists
        if username:
            cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE username = %s", (username,))
            if cursor.fetchone()["count"] > 0:
                return {"status": "error", "message": "Username already exists, try something else"}

        # Check if email exists
        if email_id:
            cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE email_id = %s", (email_id,))
            if cursor.fetchone()["count"] > 0:
                return {"status": "error", "message": "Account already exists for this email, try logging in"}

        return {"status": "success", "message": "Username and email are available"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


# Endpoint to add a new member
@create_member_route.post("/add-member/")
async def add_member(
    username: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(...),
    address: str = Form(...),
    email_id: EmailStr = Form(...),
    membership_type: str = Form(...),
    points: int = Form(...),
    file: UploadFile = File(...),  # Added file upload for S3
    response: Response = Response(),
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the username already exists
        cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE username = %s", (username,))
        username_exists = cursor.fetchone()["count"]

        if username_exists > 0:
            return {"status": "error", "message": "Username already exists, try something else"}

        # Check if the email_id already exists
        cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE email_id = %s", (email_id,))
        email_exists = cursor.fetchone()["count"]

        if email_exists > 0:
            return {"status": "error", "message": "Account already exists for this email, try logging in"}

        # Upload the profile picture to S3
        file_content = await file.read()
        object_name = f"profile_pictures/{username}/{file.filename}"
        try:
            s3_client.put_object(
                Bucket=ACCESS_POINT_ALIAS,
                Key=object_name,
                Body=file_content,
                ContentType=file.content_type,
            )
            picture_url = f"https://{ACCESS_POINT_ALIAS}.s3.{S3_REGION}.amazonaws.com/{object_name}"
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"S3 Upload error: {e.response['Error']['Message']}")

        # If both username and email_id are unique, insert the new member
        query = """
        INSERT INTO Members (username, pass, first_name, last_name, phone_number, address,
                             email_id, membership_type, points, picture_url, is_deleted)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "N")
        """
        cursor.execute(
            query,
            (
                username,
                password,
                first_name,
                last_name,
                phone_number,
                address,
                email_id,
                membership_type,
                points,
                picture_url,  # Use picture URL generated from S3 upload
            ),
        )
        connection.commit()

        # Save session data in secure cookies
        save_to_session(response, "username", username)
        save_to_session(response, "email_id", email_id)
        save_to_session(response, "picture_url", picture_url)

        return {"status": "success", "message": "Member added successfully", "picture_url": picture_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
