from fastapi import APIRouter, Form, UploadFile, File, Request
from pydantic import EmailStr
from botocore.exceptions import ClientError
from utils.password_util import hash_password
from utils.db_util import get_db_connection
from utils.secrets_util import Access_Point_ALIAS
import boto3
import traceback
from fastapi import HTTPException
from datetime import datetime
from typing import List,  Optional, Union
from emails.welcome_email import send_welcome_email, generate_temp_password
from pydantic import conint

# Initialize router
create_member_route = APIRouter()

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"
ACCESS_POINT_ALIAS = Access_Point_ALIAS

# Initialize S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

@create_member_route.post("/add-member/") 
async def add_member(
    request: Request,
    username: str = Form(...),
    #password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: int = Form(...),
    member_address1: str = Form(...),
    member_address2: str = Form(""),
    member_city: str = Form(...),
    member_state: str = Form(...),
    member_zip: int = Form(...),    
    email_id: EmailStr = Form(...),
    membership_type: str = Form(...),
    points: int = Form(...),
    referral_information: str = Form(None),
    company_name: str = Form(None),
    file: Optional[UploadFile] = File(None),
    emergency_contact: int = Form(...),
    #emergency_email: EmailStr = Form(...),
    emergency_relationship: str = Form(...),
    emergency_name: str = Form(...),
    dl: str = Form(""),
    spouse: str = Form(""),
    spouse_email: str = Form(""),
    spouse_phone: str = Form(""),
    depository_name: str = Form(None),
    branch: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    zip_code: int = Form(0),
    routing_no: int = Form(0),
    acc_no: int = Form(0),
    name_on_acc: str = Form(None),
    type_of_acc: str = Form(None),
    date_sub: str = Form(default=datetime.utcnow().strftime('%Y-%m-%d')),
    #existing_membership_id: Union[int, None] = Form(None),  # New field to allow linking to an existing membership
    # Adding children details
    child_names: List[str] = Form([]),
    child_dobs: List[str] = Form([]),
    child_emails: List[str] = Form([]),
    child_phone_numbers: List[str] = Form([]),
    # NEW FIELDS
    is_primary: conint(ge=0, le=1) = Form(0),      # only 0 or 1
    opening_balance: int = Form(...),       
    primary_member_id: Optional[str] = Form(None),  # can be null
):
    """
    Adds a new member to the database with optional profile picture upload and optional children's details.
    """
    connection = None
    cursor = None
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
        # Assign Membership ID (either existing or new)
        #if existing_membership_id:
            #membership_id = existing_membership_id
        #else:
            #cursor.execute("SELECT COALESCE(MAX(membership_id) + 1, 1) FROM Members")
            #membership_id = cursor.fetchone()[0]
        
        temp_password = generate_temp_password()
        hashed_password = hash_password(temp_password)

        # Process profile picture upload or assign default photo
        if file and isinstance(file, UploadFile):
            if file.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")
                
            file_content = await file.read()
            object_name = f"profile_pictures/{username}/{file.filename}"
            
            try:
                s3_client.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=object_name,
                    Body=file_content,
                    ContentType=file.content_type,
                )
                picture_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{object_name}"
            except ClientError as e:
                raise HTTPException(status_code=500, detail=f"S3 Upload error: {e.response['Error']['Message']}")
        else:
            # Either file was not provided or an empty string was sent
            picture_url = "https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/profile_pictures/default.png"
        
        # check:
        # Browsers can send "" for empty inputs; normalize to None
        if isinstance(primary_member_id, str) and primary_member_id.strip() == "":
            primary_member_id = None

        if is_primary == 1:
        # primary members MUST have NULL primary_member_id
            if primary_member_id is not None:
                raise HTTPException(
                    status_code=422,
                    detail="primary_member_id must be NULL when is_primary=1 (primary)."
                )
            primary_member_id = None  # force it

        else:                 
            if primary_member_id is None:   # secondary members MUST have a non-null primary_member_id (and ideally > 0)
                raise HTTPException(
                    status_code=422,
                    detail="primary_member_id is required when is_primary=0 (secondary)."
                )
            if int(primary_member_id) <= 0:
                raise HTTPException(
                    status_code=422,
                    detail="primary_member_id must be a positive integer."
                )
        
        # Insert member data
        query = """
            INSERT INTO Members (username, pass, first_name, last_name, phone_number, member_address1, member_address2, member_city, member_state, member_zip,
                                email_id, membership_type, points, referral_information, picture_url, user_type, is_deleted, dl, company_name,
                                is_primary, opening_balance, primary_member_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (username, hashed_password, first_name, last_name, phone_number, member_address1, member_address2, member_city, member_state, member_zip, 
            email_id, membership_type, points, referral_information, picture_url, "User", "N", dl, company_name,
            is_primary, opening_balance, primary_member_id))
        member_id = cursor.lastrowid
        if member_id is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve member_id after insertion.")
        
        email_response = send_welcome_email(
            to_email=email_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            temp_password=temp_password
        )
        
        # Insert emergency details
        cursor.execute("""
        INSERT INTO Member_Emergency_Details (member_id, ec_name, ec_relationship, ec_phone_number, spouse, spouse_email, spouse_phone_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (member_id, emergency_name, emergency_relationship, emergency_contact, spouse or None, spouse_email or None, spouse_phone or None))
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
        return {"status": "success", "message": "Member added successfully", "member_id": member_id, "email_status": email_response}
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@create_member_route.get("/validate-member/")
async def validate_member(username: str = None, email_id: str = None):
    """
    Validates if a username or email is already registered.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
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
