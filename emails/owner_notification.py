import uuid
from datetime import datetime, timedelta
import pytz
import boto3
from icalendar import Calendar, Event, Alarm, vCalAddress, vText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dateutil.parser import isoparse

from utils.yacht_util import get_yacht_basename, get_yacht_id_by_name
from utils.owner_util import get_owner_by_yacht_id

# SES client (region ap-southeast-2)
ses_client = boto3.client("ses", region_name="ap-southeast-2")

# BCC recipients for every invite
BCC_EMAILS = [
    "brian@kokomoyachtclub.vip",
    "info@iusdigitalsolutions.com"
]

# Verified sender address
SENDER_EMAIL = "info@kokomoyachts.com"

def build_invite(
    subject: str,
    description: str,
    start_dt: datetime,
    end_dt: datetime,
    organizer_email: str,
    organizer_name: str,
) -> bytes:
    """
    Returns ICS bytes for a single VEVENT. Forces America/New_York if naive;
    otherwise converts from whatever tz the datetime has into Eastern.
    """
    eastern = pytz.timezone("America/New_York")

    # Localize or convert to Eastern
    if start_dt.tzinfo is None:
        start_dt = eastern.localize(start_dt)
    else:
        start_dt = start_dt.astimezone(eastern)

    if end_dt.tzinfo is None:
        end_dt = eastern.localize(end_dt)
    else:
        end_dt = end_dt.astimezone(eastern)

    cal = Calendar()
    cal.add("prodid", "-//Kokomo Yacht Club//BookingInvite//EN")
    cal.add("version", "2.0")
    cal.add("method", "PUBLISH")

    event = Event()
    event.add("uid", f"{uuid.uuid4()}@kokomoyachtclub.vip")
    event.add("dtstamp", datetime.now(eastern))
    event.add("dtstart", start_dt)
    event.add("dtend", end_dt)
    event.add("summary", subject)
    event.add("description", description)

    # Organizer
    organizer = vCalAddress(f"MAILTO:{organizer_email}")
    organizer.params["cn"] = vText(organizer_name)
    event["organizer"] = organizer

    # Reminder alarm 30 minutes before
    alarm = Alarm()
    alarm.add("action", "DISPLAY")
    alarm.add("description", "Booking Reminder")
    alarm.add("trigger", timedelta(minutes=-30))
    event.add_component(alarm)

    cal.add_component(event)
    return cal.to_ical()


def send_calendar_invite(
    sender: str,
    recipient: str,
    subject: str,
    body_text: str,
    ics_content: bytes,
    ics_filename: str = "invite.ics",
    bcc_emails=None,
):
    """
    Sends a raw SES email with the ICS attached, including BCC recipients.
    """
    bcc_emails = bcc_emails or BCC_EMAILS

    # Build the multipart/mixed container
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg["Bcc"] = ", ".join(bcc_emails)

    # 1) Plain-text body
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(body_text, "plain"))
    msg.attach(alt)

    # 2) The ICS attachment
    ics_part = MIMEApplication(ics_content, _subtype="ics")
    ics_part.add_header(
        "Content-Disposition", f'attachment; filename="{ics_filename}"'
    )
    ics_part.add_header("Content-Class", "urn:content-classes:calendarmessage")
    ics_part.add_header("Method", "REQUEST")
    msg.attach(ics_part)

    # 3) SES send_raw_email (include BCC in Destinations)
    destinations = [recipient] + bcc_emails
    response = ses_client.send_raw_email(
        Source=sender,
        Destinations=destinations,
        RawMessage={"Data": msg.as_string()},
    )
    return response


def send_invite(yacht_name: str, tour_type_name: str, start_at: str, end_at: str, contact_email: str):
    """
    Look up yacht owner(s), build and send calendar invite with BCC.
    If contact_email is 'satya@iusdigitalsolutions.com', marks the booking as a test.
    """
    if not (yacht_name and start_at and end_at):
        print("WARNING: Missing yacht_name or start/end time; skipping invite")
        return

    yacht_id = get_yacht_id_by_name(yacht_name)
    owner = get_owner_by_yacht_id(yacht_id) if yacht_id else None

    if not owner:
        print(f"WARNING: No owner found for yacht '{yacht_name}'")
        return

    # Check if this is a test booking
    is_test_booking = contact_email and contact_email.lower() == "satya@iusdigitalsolutions.com"
    
    yatch_base_name = get_yacht_basename(yacht_name)
    for owner_data in owner:
        try:
            owner_name = owner_data["owner_name"]
            owner_emails = owner_data["owner_emails"]

            # Parse ISO strings
            start_dt = isoparse(start_at)
            end_dt = isoparse(end_at)
            eastern = pytz.timezone("America/New_York")
            start_local = start_dt.astimezone(eastern).strftime("%d %b %Y, %I:%M %p %Z")
            end_local = end_dt.astimezone(eastern).strftime("%d %b %Y, %I:%M %p %Z")

            # Adjust summary and description for test bookings
            if is_test_booking:
                summary = f"[TEST] Kokomo Yachts: {yatch_base_name} Booked - PLEASE IGNORE"
                description = (
                    f"Hello {owner_name},\n\n"
                    f"THIS IS A TEST BOOKING - PLEASE IGNORE \n\n"
                    f"Your yacht '{yatch_base_name}' received a test booking.\n"
                    f"Start: {start_local}\n"
                    f"End:   {end_local}\n"
                    f"Tour Type: {tour_type_name or 'N/A'}\n"
                    f"Contact Email: {contact_email}\n\n"
                    "This is a test booking for system verification purposes. "
                    "No action is required from you.\n\n"
                    "— Kokomo Crew"
                )
                body_text = (
                    f"Hi {owner_name},\n\n"
                    "THIS IS A TEST BOOKING - PLEASE IGNORE \n\n"
                    "Your yacht received a test booking for system verification. "
                    "No action is required from you.\n\n"
                    f"Start: {start_local}\n"
                    f"End:   {end_local}\n\n"
                    "Best Regards,\n"
                    "Kokomo Crew\n"
                )
                ics_filename = f"TEST_Yacht_{yatch_base_name}_Booked.ics"
            else:
                summary = f"Kokomo Yachts: {yatch_base_name} Booked"
                description = (
                    f"Hello {owner_name},\n\n"
                    f"Your yacht '{yatch_base_name}' was just booked.\n"
                    f"Start: {start_local}\n"
                    f"End:   {end_local}\n"
                    f"Tour Type: {tour_type_name or 'N/A'}\n"
                    f"Contact Email: {contact_email or 'N/A'}\n\n"
                    "Thank you for partnering with Kokomo Yachts!\n"
                    "— Kokomo Crew"
                )
                body_text = (
                    f"Hi {owner_name},\n\n"
                    "Your yacht was just booked! Please open the attached .ics to add it to your calendar.\n\n"
                    f"Start: {start_local}\n"
                    f"End:   {end_local}\n\n"
                    "Best Regards,\n"
                    "Kokomo Crew\n"
                )
                ics_filename = f"Yacht_{yatch_base_name}_Booked.ics"

            ics_bytes = build_invite(
                subject=summary,
                description=description,
                start_dt=start_dt,
                end_dt=end_dt,
                organizer_email=SENDER_EMAIL,
                organizer_name="Kokomo Crew"
            )
            
            test_email = "satya@iusdigitalsolutions.com"

            for email in owner_emails:
                log_message = f"INFO: Sending {'TEST' if is_test_booking else ''} invite to {owner_name} <{email}>"
                print(log_message)
                
                send_calendar_invite(
                    sender=SENDER_EMAIL,
                    recipient=test_email,
                    subject=summary,
                    body_text=body_text,
                    ics_content=ics_bytes,
                    ics_filename=ics_filename
                )
                print(f"INFO: Sent .ics {'test ' if is_test_booking else ''}invite to {test_email}")

        except Exception as e:
            print(f"ERROR: Failed to send calendar invite to {owner_name}: {e}")