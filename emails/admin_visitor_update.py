from fastapi import HTTPException
from email.mime.text import MIMEText
from typing import Optional
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, EmailStr
from utils.email_util import smtp_connection
import os
import smtplib
from email.message import EmailMessage

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
    attendees: int

# Admin Email Address and Recipients
ADMIN_EMAIL = "info@kokomoyachts.com"
RECIPIENTS = ["brian@kokomoyachtclub.vip", "cynthia@kokomoyachtclub.vip", "info@iusdigitalsolutions.com"]

# ADMIN_EMAIL = "satya@iusdigitalsolutions.com"
# RECIPIENTS = ["aishwarya@iusdigitalsolutions.com"]


def _send_email(subject: str, body_text: str):
    try:
        server = smtp_connection()
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = ADMIN_EMAIL
        message["To"] = ", ".join(RECIPIENTS)
        message.attach(MIMEText(body_text, "html"))

        server.sendmail(ADMIN_EMAIL, RECIPIENTS, message.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

def send_admin_notification_visitor(request: VisitorRequest):
    subject = "New Contact Us Form"
    
    body_text = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Contact Us Submission • Kokomo Yacht Club</title>
        </head>
        <body style="margin:0; padding:0; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color:#f8f9fa; color:#2c3e50;">

            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f8f9fa; padding:40px 20px;">
                <tr>
                    <td align="center">

                        <!-- Main Container -->
                        <table cellpadding="0" cellspacing="0" border="0" width="500" style="background-color:#ffffff; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                            
                            <!-- Header -->
                            <tr>
                                <td style="background-color:#033e8b; padding:40px 30px; text-align:center;">
                                    <img src="https://kokomoyachtclub.vip/images/logo.png"
                                        alt="Kokomo Yacht Club Logo"
                                        style="max-height:60px; width:auto; display:block; margin:0 auto 20px;"
                                        onerror="this.style.display='none';">
                                    <h1 style="color:#ffffff; font-size:24px; font-weight:300; margin:0; letter-spacing:2px;">
                                        KOKOMO YACHT CLUB
                                    </h1>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding:40px 30px;">

                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        Hello Brian,
                                    </p>

                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        A new Contact Us Form has been submitted. Please find the details below:
                                    </p>

                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 10px 0;">
                                        ----------------------------------------
                                    </p>
                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 10px 0;">
                                        Visitor Details
                                    </p>
                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        ----------------------------------------
                                    </p>

                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:0 0 30px 0;">
                                        Name: {request.visitor_name or 'N/A'}<br>
                                        Email: {request.email}<br>
                                        Phone Number: {request.phone_no or 'N/A'}<br>
                                        {f"Requested Help: {request.req_help}<br>" if request.req_help else ""}
                                        {f"Any Questions: {request.ques}" if request.ques else ""}
                                    </p>

                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:30px 0 0 0;">
                                        Best regards,<br>
                                        <strong style="color:#033e8b;">Kokomo Yacht Club System</strong>
                                    </p>
                                    
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color:#f8f9fa; padding:20px 30px; text-align:center; border-top:1px solid #e9ecef;">
                                    <p style="color:#6c757d; font-size:12px; margin:0;">
                                        Kokomo Yacht Club<br>
                                        <a href="https://kokomoyachtclub.vip" style="color:#033e8b; text-decoration:none;">
                                            kokomoyachtclub.vip
                                        </a>
                                    </p>
                                </td>
                            </tr>

                        </table>

                    </td>
                </tr>
            </table>

        </body>
        </html>
        """
    _send_email(subject, body_text)
    return {"status": "success", "message": "Visitor notification email sent successfully"}

def send_admin_notification_email_request(request: EmailRequest):
    subject = "New Membership Brochure Form"
    
    body_text = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Membership Brochure Submission • Kokomo Yacht Club</title>
        </head>
        <body style="margin:0; padding:0; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color:#f8f9fa; color:#2c3e50;">

            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f8f9fa; padding:40px 20px;">
                <tr>
                    <td align="center">

                        <!-- Main Container -->
                        <table cellpadding="0" cellspacing="0" border="0" width="500" style="background-color:#ffffff; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                            
                            <!-- Header -->
                            <tr>
                                <td style="background-color:#033e8b; padding:40px 30px; text-align:center;">
                                    <img src="https://kokomoyachtclub.vip/images/logo.png"
                                        alt="Kokomo Yacht Club Logo"
                                        style="max-height:60px; width:auto; display:block; margin:0 auto 20px;"
                                        onerror="this.style.display='none';">
                                    <h1 style="color:#ffffff; font-size:24px; font-weight:300; margin:0; letter-spacing:2px;">
                                        KOKOMO YACHT CLUB
                                    </h1>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding:40px 30px;">

                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        Hello Brian,
                                    </p>

                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        A new Membership Brochure Form has been submitted. Please find the details below:
                                    </p>

                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 10px 0;">
                                        ----------------------------------------
                                    </p>
                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 10px 0;">
                                        Requester Details
                                    </p>
                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        ----------------------------------------
                                    </p>

                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:0 0 30px 0;">
                                        Name: {request.visitor_name or 'N/A'}<br>
                                        Email: {request.email}<br>
                                        Phone Number: {request.phone_no or 'N/A'}
                                    </p>

                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:30px 0 0 0;">
                                        Best regards,<br>
                                        <strong style="color:#033e8b;">Kokomo Yacht Club System</strong>
                                    </p>
                                    
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color:#f8f9fa; padding:20px 30px; text-align:center; border-top:1px solid #e9ecef;">
                                    <p style="color:#6c757d; font-size:12px; margin:0;">
                                        Kokomo Yacht Club<br>
                                        <a href="https://kokomoyachtclub.vip" style="color:#033e8b; text-decoration:none;">
                                            kokomoyachtclub.vip
                                        </a>
                                    </p>
                                </td>
                            </tr>

                        </table>

                    </td>
                </tr>
            </table>

        </body>
        </html>
        """
    _send_email(subject, body_text)
    return {"status": "success", "message": "Email request notification sent successfully"}

def send_admin_notification_yacht_visitor(request: YachtVisitorRequest):
    subject = "New List Your Yacht Form"
    
    body_text = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>List Your Yacht Submission • Kokomo Yacht Club</title>
        </head>
        <body style="margin:0; padding:0; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color:#f8f9fa; color:#2c3e50;">

            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f8f9fa; padding:40px 20px;">
                <tr>
                    <td align="center">

                        <!-- Main Container -->
                        <table cellpadding="0" cellspacing="0" border="0" width="500" style="background-color:#ffffff; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                            
                            <!-- Header -->
                            <tr>
                                <td style="background-color:#033e8b; padding:40px 30px; text-align:center;">
                                    <img src="https://kokomoyachtclub.vip/images/logo.png"
                                        alt="Kokomo Yacht Club Logo"
                                        style="max-height:60px; width:auto; display:block; margin:0 auto 20px;"
                                        onerror="this.style.display='none';">
                                    <h1 style="color:#ffffff; font-size:24px; font-weight:300; margin:0; letter-spacing:2px;">
                                        KOKOMO YACHT CLUB
                                    </h1>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding:40px 30px;">

                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        Hello Brian,
                                    </p>

                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        A new List Your Yacht form has been submitted. Please find the details below:
                                    </p>

                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 10px 0;">
                                        ----------------------------------------
                                    </p>
                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        Visitor Details
                                    </p>
                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 10px 0;">
                                        ----------------------------------------
                                    </p>
                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:0 0 30px 0;">
                                        Name: {request.visitor_first_name} {request.visitor_last_name}<br>
                                        Email: {request.visitor_email}<br>
                                        Phone Number: {request.visitor_phone_number}
                                    </p>

                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 10px 0;">
                                        ----------------------------------------
                                    </p>
                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        Yacht Details
                                    </p>
                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 10px 0;">
                                        ----------------------------------------
                                    </p>
                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:0 0 30px 0;">
                                        Model: {request.yacht_model}<br>
                                        Manufacture Year: {request.yacht_manufacture_year}<br>
                                        Size: {request.yacht_size} ft<br>
                                        {f'Message: {request.visitor_message}' if request.visitor_message else ''}
                                    </p>

                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:30px 0 0 0;">
                                        Best regards,<br>
                                        <strong style="color:#033e8b;">Kokomo Yacht Club System</strong>
                                    </p>
                                    
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color:#f8f9fa; padding:20px 30px; text-align:center; border-top:1px solid #e9ecef;">
                                    <p style="color:#6c757d; font-size:12px; margin:0;">
                                        Kokomo Yacht Club<br>
                                        <a href="https://kokomoyachtclub.vip" style="color:#033e8b; text-decoration:none;">
                                            kokomoyachtclub.vip
                                        </a>
                                    </p>
                                </td>
                            </tr>

                        </table>

                    </td>
                </tr>
            </table>

        </body>
        </html>
        """

    _send_email(subject, body_text)
    return {"status": "success", "message": "Yacht visitor notification email sent successfully"}

def send_admin_notification_rsvp(request: EventRequest):
    subject = f"New Entry for {request.event_name}"
    body_text = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Form Submission • Kokomo Yacht Club</title>
        </head>
        <body style="margin:0; padding:0; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color:#f8f9fa; color:#2c3e50;">

            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f8f9fa; padding:40px 20px;">
                <tr>
                    <td align="center">

                        <!-- Main Container -->
                        <table cellpadding="0" cellspacing="0" border="0" width="500" style="background-color:#ffffff; box-shadow:0 4px 12px rgba(0,0,0,0.1);">

                            <!-- Header -->
                            <tr>
                                <td style="background-color:#033e8b; padding:40px 30px; text-align:center;">
                                    <img src="https://kokomoyachtclub.vip/images/logo.png"
                                        alt="Kokomo Yacht Club Logo"
                                        style="max-height:60px; width:auto; display:block; margin:0 auto 20px;"
                                        onerror="this.style.display='none';">
                                    <h1 style="color:#ffffff; font-size:24px; font-weight:300; margin:0; letter-spacing:2px;">
                                        KOKOMO YACHT CLUB
                                    </h1>
                                </td>
                            </tr>

                            <!-- Content -->
                            <tr>
                                <td style="padding:40px 30px;">

                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        Hello Brian,
                                    </p>

                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        A new form has been submitted. Please find the details below:
                                    </p>
                                    <!-- Styled details block -->
                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 10px 0;">
                                        ----------------------------------------
                                    </p>
                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 20px 0;">
                                        Details
                                    </p>
                                    <p style="color:#5a6c7d; font-size:16px; line-height:1.6; margin:0 0 10px 0;">
                                        ----------------------------------------
                                    </p>
                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:0 0 30px 0;">
                                        Name: {request.name}<br>
                                        Email: {request.email}<br>
                                        Phone Number: {request.phone_no}<br>
                                        Event Name: {request.event_name}
                                    </p>

                                    <p style="color:#2c3e50; font-size:16px; line-height:1.6; margin:30px 0 0 0;">
                                        Best regards,<br>
                                        Kokomo Yacht Club System
                                    </p>
                                    
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="background-color:#f8f9fa; padding:20px 30px; text-align:center; border-top:1px solid #e9ecef;">
                                    <p style="color:#6c757d; font-size:12px; margin:0;">
                                        Kokomo Yacht Club<br>
                                        <a href="https://kokomoyachtclub.vip" style="color:#033e8b; text-decoration:none;">
                                            kokomoyachtclub.vip
                                        </a>
                                    </p>
                                </td>
                            </tr>

                        </table>

                    </td>
                </tr>
            </table>

        </body>
        </html>
        """
    
    _send_email(subject, body_text)
    return {"status": "success", "message": "RSVP notification email sent successfully"}

