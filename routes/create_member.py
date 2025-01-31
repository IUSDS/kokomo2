from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Request, Query
from pydantic import EmailStr
from botocore.exceptions import ClientError
from passlib.context import CryptContext
from utils.database import get_db_connection
import boto3
import traceback
from starlette.middleware.sessions import SessionMiddleware 
from fastapi import  Depends, HTTPException
from datetime import datetime
from typing import List

# Initialize router
create_member_route = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"
ACCESS_POINT_ALIAS = "first-kokomo-access-y1pahkde96c1mfspxs7cbiaro94hyaps2a-s3alias",

# Initialize S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

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
    emergency_email: EmailStr = Form(...),
    emergency_relationship: str = Form(...),
    emergency_name: str = Form(...),
    dl: str = Form(None),
    spouse: str = Form(None),
    spouse_email: EmailStr = Form(None),
    spouse_phone: int = Form(None),
    depository_name: str = Form(...),
    branch: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: int = Form(...),
    routing_no: int = Form(...),
    acc_no: int = Form(...),
    name_on_acc: str = Form(...),
    type_of_acc: str = Form(...),
    date_sub: str = Form(default=datetime.utcnow().strftime('%Y-%m-%d')),

    # Adding children details
    child_names: List[str] = Form([]),
    child_dobs: List[str] = Form([]),
    child_emails: List[str] = Form([]),
    child_phone_numbers: List[str] = Form([]),
):
    """
    Adds a new member to the database with optional profile picture upload and optional children's details.
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
        cursor.execute(query, (username, hashed_password, first_name, last_name, phone_number, member_address1, member_address2, member_city, member_state, member_zip, 
            email_id, membership_type, points, referral_information, picture_url, "User", "N", dl, company_name,))
        member_id = cursor.lastrowid
        if member_id is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve member_id after insertion.")
        
        # Insert emergency details
        cursor.execute("""
        INSERT INTO Member_Emergency_Details (member_id, ec_name, ec_relationship, ec_phone_number, ec_email, spouse, spouse_email, spouse_phone_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (member_id, emergency_name, emergency_relationship, emergency_contact, emergency_email, spouse or None, spouse_email or None, spouse_phone or None))

        # Insert bank details
        cursor.execute("""
        INSERT INTO Member_ACH_Details (member_id, depository, branch, city, state, zip, routing_no, acc_no, name_on_acc, type_of_acc, date_sub)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (member_id, depository_name, branch, city, state, zip_code, routing_no, acc_no, name_on_acc, type_of_acc, date_sub))

        # Insert children's details
        num_children = len(child_names)
        if num_children > 4:
            raise HTTPException(status_code=400, detail="Cannot add more than 4 children")
        
        for i in range(num_children):
            query = """
            INSERT INTO Member_Childern_Details (member_id, child_name, child_email, child_phone_number, child_dob)
            VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                member_id,
                child_names[i] if child_names[i] else None,
                child_emails[i] if child_emails[i] else None,
                child_phone_numbers[i] if child_phone_numbers[i] else None,
                child_dobs[i] if child_dobs[i] else None,
            )
            cursor.execute(query, values)

        connection.commit()

        return {"status": "success", "message": "Member added successfully", "member_id": member_id}
    
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
            