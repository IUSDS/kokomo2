from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Response, Depends
from pydantic import EmailStr
from fastapi.responses import JSONResponse
from botocore.exceptions import ClientError
from database import get_db_connection
import boto3

create_member_route = APIRouter()

router = APIRouter()

# AWS S3 Configuration
AWS_ACCESS_KEY = "your-aws-access-key"
AWS_SECRET_KEY = "your-aws-secret-key"
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"
ACCESS_POINT_ALIAS = "first-kokomo-access-y1pahkde96c1mfspxs7cbiaro94hyaps2a-s3alias"

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION,
)

def save_to_session(response: Response, key: str, value: str):
    response.set_cookie(key=key, value=value, httponly=True, max_age=3600)

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
    file: UploadFile = File(...),
    response: Response = Response(),
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check for existing username
        cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE username = %s", (username,))
        if cursor.fetchone()["count"] > 0:
            return {"status": "error", "message": "Username already exists"}

        # Check for existing email
        cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE email_id = %s", (email_id,))
        if cursor.fetchone()["count"] > 0:
            return {"status": "error", "message": "Email already exists"}

        # Upload file to S3
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

        # Save member to DB
        query = """
        INSERT INTO Members (username, pass, first_name, last_name, phone_number, address,
                             email_id, membership_type, points, picture_url, is_deleted)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "N")
        """
        cursor.execute(query, (username, password, first_name, last_name, phone_number, address,
                               email_id, membership_type, points, picture_url))
        connection.commit()

        # Save data to session
        save_to_session(response, "username", username)
        save_to_session(response, "email_id", email_id)
        save_to_session(response, "picture_url", picture_url)

        return {"status": "success", "message": "Member added successfully", "picture_url": picture_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
