from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Request
from pydantic import EmailStr
from botocore.exceptions import ClientError
#from passlib.context import CryptContext
from database import get_db_connection
import boto3

# Initialize router
create_member_route = APIRouter()

# Password hashing context
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"
ACCESS_POINT_ALIAS = "first-kokomo-access-y1pahkde96c1mfspxs7cbiaro94hyaps2a-s3alias",

# Initialize S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

@create_member_route.post("/add-member/")
async def add_member(
    request: Request,  # Correctly importing and using the Request object
    username: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: int = Form(...),
    address: str = Form(...),
    email_id: EmailStr = Form(...),
    membership_type: str = Form(...),
    points: int = Form(...),
    file: UploadFile = File(...),  # Correctly set as a File parameter
    emergency_contact: int = Form(...),
    Emergency_Contact_Relationship: str = Form(...),
    Emergency_Contact_Name: str = Form(...),
    DL: str = Form(...),
    spouse: str = Form(...),
    ):
    """
    Adds a new member to the database with optional profile picture upload.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Validate username and email
        cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE username = %s", (username,))
        if cursor.fetchone()["count"] > 0:
            raise HTTPException(status_code=400, detail="Username already exists, try another one.")

        cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE email_id = %s", (email_id,))
        if cursor.fetchone()["count"] > 0:
            raise HTTPException(status_code=400, detail="Account already exists for this email, try logging in.")

        picture_url = None
        if file:
            if file.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")
            file_content = await file.read()
            object_name = f"profile_pictures/{username}/{file.filename}"
            print(object_name)
            try:
                s3_client.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=object_name,
                    Body=file_content,
                    ContentType=file.content_type,
                )
                picture_url = f"https://{ACCESS_POINT_ALIAS}.s3.{S3_REGION}.amazonaws.com/{object_name}"
            except ClientError as e:
                raise HTTPException(status_code=500, detail=f"S3 Upload error: {e.response['Error']['Message']}")

        # Insert the member into the database
        query = """
        INSERT INTO Members (username, pass, first_name, last_name, phone_number, address,
                             email_id, membership_type, points, picture_url, user_type, is_deleted, emergency_contact, Emergency_Contact_Relationship, Emergency_Contact_Name, DL, spouse)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "User", "N", %s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (username, password, first_name, last_name, phone_number, address, email_id, membership_type, points, picture_url, emergency_contact, Emergency_Contact_Relationship, Emergency_Contact_Name, DL, spouse),
        )
        connection.commit()

        # Save user data to the session
        session = request.session
        session["username"] = username
        session["email_id"] = email_id
        session["picture_url"] = picture_url

        return {"status": "success", "message": "Member added successfully", "picture_url": picture_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals():
            connection.close()

@create_member_route.get("/validate-member/")
async def validate_member(username: str = None, email_id: str = None):
    """
    Validates if a username or email is already registered.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if username:
            cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE username = %s", (username,))
            if cursor.fetchone()["count"] > 0:
                raise HTTPException(status_code=400, detail="Username already exists.")

        if email_id:
            cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE email_id = %s", (email_id,))
            if cursor.fetchone()["count"] > 0:
                raise HTTPException(status_code=400, detail="Email is already registered.")

        return {"status": "success", "message": "Username and email are available"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals():
            connection.close()
