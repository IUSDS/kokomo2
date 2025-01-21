import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from fastapi import FastAPI, APIRouter, HTTPException
from sqlalchemy import event
from sqlalchemy.orm import Session
from database import get_db_connection

def send_email(sender_email, recipient_email, subject, body_text, body_html, aws_region="ap-southeast-2"):
    """
    Send an email using AWS SES.

    :param sender_email: Email address of the sender (must be verified in AWS SES).
    :param recipient_email: Email address of the recipient.
    :param subject: Subject of the email.
    :param body_text: Plain text version of the email body.
    :param body_html: HTML version of the email body.
    :param aws_region: AWS region where SES is set up 
    """
    try:
        # Create a new SES client
        ses_client = boto3.client('ses', region_name=aws_region)

        # Send email
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [recipient_email],
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': body_html,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )

        print("Email sent successfully! Message ID:", response['MessageId'])

    except NoCredentialsError:
        print("Error: AWS credentials not found.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials.")
    except Exception as e:
        print(f"Error: {e}")

adminEmail_route = APIRouter()

@adminEmail_route.post("/adminEmail/")
def trigger_email_on_new_visitor():
    """
    Route to manually trigger email for a new visitor entry.
    """
    sender = "info@kokomoyachtclub.vip"
    recipient = "nainika@iusdigitalsolutions.com"
    email_subject = "New Visitor Entry at Kokomo Yacht Club"
    email_body_text = "A new visitor entry has been added to the database."
    email_body_html = """
    <html>
    <head></head>
    <body>
      <h1>New Visitor Entry</h1>
      <p>A new visitor entry has been added to the database of <b>Kokomo Yacht Club</b>.</p>
    </body>
    </html>
    """

    send_email(sender, recipient, email_subject, email_body_text, email_body_html)
    return {"message": "Email triggered successfully."}

# Database event listener for Visitors table
def after_insert_listener():
    """
    Listener to trigger email when a new entry is added to the Visitors table.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM visitors ORDER BY email DESC LIMIT 1")
            latest_entry = cursor.fetchone()
            if latest_entry:
                sender = "info@kokomoyachtclub.vip"
                recipient = latest_entry['email']
                email_subject = "New Visitor Entry at Kokomo Yacht Club"
                email_body_text = f"A new visitor entry has been added:\n\nVisitor Name: {latest_entry['visitor_name']}\nPhone Number: {latest_entry['phone_no']}\nRequest Help: {latest_entry['req_help']}\nQuestions: {latest_entry['ques']}"
                email_body_html = f"""
                <html>
                <head></head>
                <body>
                  <h1>New Visitor Entry</h1>
                  <p>A new visitor entry has been added to the database of <b>Kokomo Yacht Club</b>:</p>
                  <ul>
                    <li><b>Visitor Name:</b> {latest_entry['visitor_name']}</li>
                    <li><b>Phone Number:</b> {latest_entry['phone_no']}</li>
                    <li><b>Request Help:</b> {latest_entry['req_help']}</li>
                    <li><b>Questions:</b> {latest_entry['ques']}</li>
                  </ul>
                </body>
                </html>
                """

                send_email(sender, recipient, email_subject, email_body_text, email_body_html)
    finally:
        connection.close()

@adminEmail_route.on_event("startup")
def setup_listener():
    """
    Setup the database trigger.
    """
    after_insert_listener()
