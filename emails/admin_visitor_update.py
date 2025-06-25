from fastapi import HTTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, EmailStr
from utils.email_util import smtp_connection

# Define Request Models
class VisitorRequest(BaseModel):
    email: EmailStr
    visitor_name: str
    phone_no: int
    req_help: str = None
    ques: str = None

class EmailRequest(BaseModel):
    email: EmailStr
    visitor_name: str
    phone_no: int

class YachtVisitorRequest(BaseModel):
    visitor_first_name: str
    visitor_last_name: str
    visitor_email: EmailStr
    visitor_phone_number: str
    yacht_model: str
    yacht_manufacture_year: int
    yacht_size: int
    visitor_message: str = None
    
class EventRequest(BaseModel):
    email: EmailStr
    name: str 
    phone_no: int 
    event_name: str

# Admin Email Address and Recipients
ADMIN_EMAIL = "info@kokomoyachts.com"
RECIPIENTS = ["brian@kokomoyachtclub.com", "cynthia@kokomoyachtclub.vip"]

def _send_email(subject: str, body_text: str):
    try:
        server = smtp_connection()
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = ADMIN_EMAIL
        message["To"] = ", ".join(RECIPIENTS)
        message.attach(MIMEText(body_text, "plain"))

        server.sendmail(ADMIN_EMAIL, RECIPIENTS, message.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

def send_admin_notification_visitor(request: VisitorRequest):
    subject = "New Visitor Form Entry"
    body_text = f"""
        Hello Brian,

        A new visitor form has been submitted. Please find the details below:

        ----------------------------------------
        **Visitor Details**
        ----------------------------------------
        **Name:** {request.visitor_name or 'N/A'}
        **Email:** {request.email}
        **Phone Number:** {request.phone_no or 'N/A'}
        {f' **Requested Help:** {request.req_help}' if request.req_help else ''}
        {f' **Any Questions:** {request.ques}' if request.ques else ''}

        Best regards,  
        **Kokomo Yacht Club System**
    """
    _send_email(subject, body_text)
    print("called from visitor")
    return {"status": "success", "message": "Visitor notification email sent successfully"}

def send_admin_notification_email_request(request: EmailRequest):
    subject = "New Email Request Entry"
    body_text = f"""
        Hello Brian,

        A new email request has been submitted. Please find the details below:

        ----------------------------------------
        **Requester Details**
        ----------------------------------------
        **Name:** {request.visitor_name or 'N/A'}
        **Email:** {request.email}
        **Phone Number:** {request.phone_no or 'N/A'}

        Best regards,  
        **Kokomo Yacht Club System**
    """
    _send_email(subject, body_text)
    print("called from email request")
    return {"status": "success", "message": "Email request notification sent successfully"}

def send_admin_notification_yacht_visitor(request: YachtVisitorRequest):
    subject = "New Yacht Visitor Form Entry"
    body_text = f"""
        Hello Brian,

        A new yacht visitor form has been submitted. Please find the details below:

        ----------------------------------------
        **Visitor Details**
        ----------------------------------------
        **Name:** {request.visitor_first_name} {request.visitor_last_name}
        **Email:** {request.visitor_email}
        **Phone Number:** {request.visitor_phone_number}

        ----------------------------------------
        **Yacht Details**
        ----------------------------------------
        **Model:** {request.yacht_model}
        **Manufacture Year:** {request.yacht_manufacture_year}
        **Size:** {request.yacht_size} ft
        {f' **Message:** {request.visitor_message}' if request.visitor_message else ''}

        Best regards,  
        **Kokomo Yacht Club System**
    """
    _send_email(subject, body_text)
    return {"status": "success", "message": "Yacht visitor notification email sent successfully"}

def send_admin_notification_rsvp(request: EventRequest):
    subject = "Member RSVP Form Entry"
    body_text = f"""
        Hello Brian,

        A new RSVP form has been submitted. Please find the details below:

        ----------------------------------------
        **RSVP Details**
        ----------------------------------------
        **Name:** {request.name}
        **Email:** {request.email}
        **Phone Number:** {request.phone_no}
        **Event Name:** {request.event_name}

        Best regards,  
        **Kokomo Yacht Club System**
    """
    _send_email(subject, body_text)
    return {"status": "success", "message": "RSVP notification email sent successfully"}
