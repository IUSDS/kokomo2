from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, EmailStr
from utils.smtp import smtp_connection
from fastapi import HTTPException

# Define Visitor Request Model
class VisitorRequest(BaseModel):
    email: EmailStr
    visitor_name: str 
    phone_no: int
    req_help: str = None
    ques: str = None

# Define Email Request Model
class EmailRequest(BaseModel):
    email: EmailStr
    visitor_name: str 
    phone_no: int 

# Function to Send Email Notification for VisitorRequest
def send_admin_notification_visitor(request: VisitorRequest):
    sender_email = "brian@kokomoyachtclub.vip"
    recipient_email = "brian@kokomoyachtclub.vip"

    subject = "New Visitor Form Entry"
    body_text = f"""
    Hello Brian,

    A new visitor form has been submitted. Please find the details below:

    ----------------------------------------
    **Visitor Details**
    ----------------------------------------
    **Name:** {request.visitor_name if request.visitor_name else 'N/A'}
    **Email:** {request.email}
    **Phone Number:** {request.phone_no if request.phone_no else 'N/A'}
    {f'**Requested Help:** {request.req_help}' if request.req_help else ''}
    {f'**Any Questions:** {request.ques}' if request.ques else ''}

    Best regards,  
    **Kokomo Yacht Club System**
    """

    # Create email message
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email
    message.attach(MIMEText(body_text, "plain"))

    # Send email
    try:
        server = smtp_connection()
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Function to Send Email Notification for EmailRequest
def send_admin_notification_email_request(request: EmailRequest):
    sender_email = "brian@kokomoyachtclub.vip"
    recipient_email = "brian@kokomoyachtclub.vip"

    subject = "New Email Form Entry"
    body_text = f"""
    Hello Brian,

    A new email form has been submitted. Please find the details below:

    ----------------------------------------
    **Email Request Details**
    ----------------------------------------
    **Name:** {request.visitor_name if request.visitor_name else 'N/A'}
    **Email:** {request.email}
    **Phone Number:** {request.phone_no if request.phone_no else 'N/A'}

    Best regards,  
    **Kokomo Yacht Club System**
    """

    # Create email message
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email
    message.attach(MIMEText(body_text, "plain"))

    # Send email
    try:
        server = smtp_connection()
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
