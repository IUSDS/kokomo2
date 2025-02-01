from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from utils.database import get_db_connection
import boto3
from emails.admin_visitor_update import send_admin_notification_visitor, send_admin_notification_email_request

visitors_route = APIRouter()

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"

# Request schemas
class EmailRequest(BaseModel):
    email: EmailStr
    visitor_name: str 
    phone_no: int 

class VisitorRequest(BaseModel):
    email: EmailStr
    visitor_name: str 
    phone_no: int
    req_help: str = None
    ques: str = None

# API to add email only
@visitors_route.post("/add-visitors-details")
async def add_visitors_details(request: EmailRequest):
    """ Adds only email to the Visitors table. """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            insert_query = """
                INSERT INTO Visitors (email, visitor_name, phone_no) 
                VALUES (%s, %s, %s) 
                ON DUPLICATE KEY UPDATE 
                    visitor_name = VALUES(visitor_name),
                    phone_no = VALUES(phone_no);
                """
            cursor.execute(insert_query, (request.email, request.visitor_name, request.phone_no,))
            connection.commit()

            if request.email:
                try:
                    return send_admin_notification_email_request(request)  
                except Exception as email_error:
                    print(f"Email notification failed: {email_error}")  
                    return {"message": "Visitor details added/updated successfully, but email notification failed."}
        return {"message": "Info added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()

# API to add full visitor details
@visitors_route.post("/become-a-member")
async def become_a_member(request: VisitorRequest):
    """ Adds full visitor details including help requests and questions. """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            insert_query = """
            INSERT INTO Visitors (email, visitor_name, phone_no, req_help, ques)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                    visitor_name = VALUES(visitor_name),
                    phone_no = VALUES(phone_no),
                    req_help = VALUES(req_help),
                    ques = VALUES(ques);
                """
            cursor.execute(insert_query, (request.email, request.visitor_name, request.phone_no, request.req_help, request.ques))
            connection.commit()

            if request.email:
                try:
                    return send_admin_notification_visitor(request)  # Send email notification to Brian and return the response
                except Exception as email_error:
                    print(f"Email notification failed: {email_error}")  
                    return {"message": "Visitor details added/updated successfully, but email notification failed."}
        return {"message": "Visitor details added/updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()