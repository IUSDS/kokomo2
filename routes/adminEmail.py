import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from fastapi import FastAPI, APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection  # Adjust based on your DB setup

# Helper function to send email using AWS SES
def send_email(sender_email, recipient_email, subject, body_text, body_html, aws_region="ap-southeast-2"):
    try:
        ses_client = boto3.client('ses', region_name=aws_region)
        response = ses_client.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'},
                    'Html': {'Data': body_html, 'Charset': 'UTF-8'}
                }
            }
        )
        print("Email sent successfully! Message ID:", response['MessageId'])
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Error sending email: {e}")
    except Exception as e:
        print(f"Error: {e}")

# APIRouter for admin email functionality
adminEmail_route = APIRouter()

# Callback request route (similar to Node.js callbackReq function)
@adminEmail_route.post("/callbackReq/")
async def callback_req(request: Request, db: Session = Depends(get_db_connection)):
    data = await request.json()
    name, number, email = data.get("name"), data.get("number"), data.get("email")

    if not name or not number or not email:
        raise HTTPException(status_code=400, detail="All fields are required: name, number, email")

    # Save to the database (callback requests)
    try:
        callback = UserCall(name=name, number=number, email=email)
        db.add(callback)
        db.commit()
        db.refresh(callback)
        print("Callback request saved to DB:", callback)

        # Send email notification
        sender = "info@kokomoyachtclub.vip"
        recipient = "admin@kokomoyachtclub.vip"
        subject = "New Callback Request"
        body_text = f"You have a new callback request from {name}, phone: {number}, email: {email}"
        body_html = f"<html><body><p>You have a new callback request from <b>{name}</b>, phone: <b>{number}</b>, email: <b>{email}</b>.</p></body></html>"

        send_email(sender, recipient, subject, body_text, body_html)

        return {"message": "Callback request submitted successfully."}
    except Exception as e:
        print(f"Error saving callback request: {e}")
        raise HTTPException(status_code=500, detail="Error saving callback request")

# Visit request route (similar to Node.js visitReq function)
@adminEmail_route.post("/visitReq/")
async def visit_req(request: Request, db: Session = Depends(get_db_connection)):
    data = await request.json()
    name, number, date = data.get("name"), data.get("number"), data.get("date")

    if not name or not number or not date:
        raise HTTPException(status_code=400, detail="All fields are required: name, number, date")

    # Save to the database (visit requests)
    try:
        visit = UserVisit(name=name, number=number, date=date)
        db.add(visit)
        db.commit()
        db.refresh(visit)
        print("Visit request saved to DB:", visit)

        # Send email notification
        sender = "info@kokomoyachtclub.vip"
        recipient = "admin@kokomoyachtclub.vip"
        subject = "New Visit Request"
        body_text = f"You have a new visit request from {name}, phone: {number}, requested date: {date}"
        body_html = f"<html><body><p>You have a new visit request from <b>{name}</b>, phone: <b>{number}</b>, requested date: <b>{date}</b>.</p></body></html>"

        send_email(sender, recipient, subject, body_text, body_html)

        return {"message": "Visit request submitted successfully."}
    except Exception as e:
        print(f"Error saving visit request: {e}")
        raise HTTPException(status_code=500, detail="Error saving visit request")
