from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from utils.db_util import get_db_connection
from emails.admin_visitor_update import send_admin_notification_visitor, send_admin_notification_email_request, send_admin_notification_yacht_visitor, send_admin_notification_rsvp

visitors_route = APIRouter()

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"

# Request schemas
class EmailRequest(BaseModel):
    email: EmailStr
    visitor_name: str 
    phone_no: int 

class EventRequest(BaseModel):
    email: EmailStr
    name: str 
    phone_no: int 
    event_name: str  

class VisitorRequest(BaseModel):
    email: EmailStr
    visitor_name: str 
    phone_no: int
    req_help: str = None
    ques: str = None
    email_consent: bool
    sms_consent: bool
    
class YachtVisitorRequest(BaseModel):
    visitor_first_name: str
    visitor_last_name: str
    visitor_email: EmailStr
    visitor_phone_number: str
    yacht_model: str
    yacht_manufacture_year: int
    yacht_size: int
    visitor_message: str = None

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
            INSERT INTO Visitors (email, visitor_name, phone_no, req_help, ques, email_consent, sms_consent)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                    visitor_name = VALUES(visitor_name),
                    phone_no = VALUES(phone_no),
                    req_help = VALUES(req_help),
                    ques = VALUES(ques),
                    email_consent = VALUES(email_consent),
                    sms_consent = VALUES(sms_consent);
                """
            cursor.execute(insert_query, (request.email, request.visitor_name, request.phone_no, request.req_help, request.ques, request.email_consent, request.sms_consent,))
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

# API to add yacht visitor details
@visitors_route.post("/add-yacht-visitor")
async def add_yacht_visitor(request: YachtVisitorRequest):
    """ Adds yacht visitor details to List_Yatch_Visitors table. """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            insert_query = """
            INSERT INTO List_Yatch_Visitors (visitor_first_name, visitor_last_name, visitor_email, visitor_phone_number, yacht_model, yacht_manufacture_year, yacht_size, visitor_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, (
                request.visitor_first_name, request.visitor_last_name, request.visitor_email,
                request.visitor_phone_number, request.yacht_model, request.yacht_manufacture_year,
                request.yacht_size, request.visitor_message))
            connection.commit()

            try:
                return send_admin_notification_yacht_visitor(request)  # Send email notification to Brian
            except Exception as email_error:
                print(f"Email notification failed: {email_error}")  
                return {"message": "Yacht visitor details added successfully, but email notification failed."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        connection.close()

# API to store event request in DB
@visitors_route.post("/add-event-details")
async def add_visitors_details(request: EventRequest):
    """ Adds info to the events table. """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            insert_query = """
                INSERT INTO events (email, name, phone_no, event_name) 
                VALUES (%s, %s, %s, %s) 
                ON DUPLICATE KEY UPDATE 
                    name = VALUES(name),
                    phone_no = VALUES(phone_no)
                """
            cursor.execute(insert_query, (request.email, request.name, request.phone_no, request.event_name))
            connection.commit()

            if request.email:
                try:
                    return send_admin_notification_rsvp(request)  
                except Exception as email_error:
                    print(f"Email notification failed: {email_error}")  
                    return {"message": "RSVP details added/updated successfully, but email notification failed."}

        return {"message": "Info added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()
        