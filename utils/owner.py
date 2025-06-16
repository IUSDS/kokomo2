import uuid
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event, Alarm, vCalAddress, vText
import boto3
from email.mime.application import MIMEApplication
from email.mime.multipart   import MIMEMultipart
from email.mime.text        import MIMEText

from utils.db_util import get_db_connection

# SES client (region ap-southeast-2)
ses_client = boto3.client("ses", region_name="ap-southeast-2")


def get_owner_by_yacht_id(yacht_id: str):
    """
    Fetches (owner_name, owner_email, owner_number) for a given yacht_id.
    Returns a dict or None if not found.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT owner_name, owner_email, owner_number "
            "FROM yacht_owners WHERE yacht_id = %s",
            (yacht_id,)   # ← make sure this is a 1-element tuple
        )
        row = cursor.fetchone()
        return row
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


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

    # 1) Localize or convert start_dt → Eastern
    if start_dt.tzinfo is None:
        start_dt = eastern.localize(start_dt)
    else:
        start_dt = start_dt.astimezone(eastern)

    # 2) Localize or convert end_dt → Eastern
    if end_dt.tzinfo is None:
        end_dt = eastern.localize(end_dt)
    else:
        end_dt = end_dt.astimezone(eastern)

    # 3) Build a Calendar + VEVENT
    cal = Calendar()
    cal.add("prodid", "-//Kokomo Yacht Club//BookingInvite//EN")
    cal.add("version", "2.0")

    event = Event()
    event.add("uid", f"{uuid.uuid4()}@kokomoyachtclub.vip")
    # dtstamp in Eastern
    event.add("dtstamp", datetime.now(eastern))
    event.add("dtstart", start_dt)
    event.add("dtend", end_dt)
    event.add("summary", subject)
    event.add("description", description)
    cal.add("method", 'PUBLISH') 

    # Organizer
    organizer = vCalAddress(f"MAILTO:{organizer_email}")
    organizer.params["cn"] = vText(organizer_name)
    event["organizer"] = organizer

    # 4) Add a VALARM subcomponent
    alarm = Alarm()
    alarm.add("action", "DISPLAY")
    alarm.add("description", "Booking Reminder")
    alarm.add("trigger", timedelta(minutes=-30))
    event.add_component(alarm)

    # 5) Attach the VEVENT to the Calendar
    cal.add_component(event)
    return cal.to_ical()  # ICS bytes


def send_calendar_invite(
    sender: str,
    recipient: str,
    subject: str,
    body_text: str,
    ics_content: bytes,
    ics_filename: str = "invite.ics",
):
    """
    Sends a raw SES email with the ICS attached.
    - sender: SES-verified “From” address (e.g. "brian@kokomoyachtclub.com")
    - recipient: owner's email
    - subject: email subject line
    - body_text: plain-text fallback
    - ics_content: raw ICS data as bytes (from build_invite)
    - ics_filename: filename to attach (e.g. "YachtBooked.ics")
    """
    # Build multipart/mixed container
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    # 1) Plain-text body
    alt = MIMEMultipart("alternative")
    text_part = MIMEText(body_text, "plain")
    alt.attach(text_part)
    msg.attach(alt)

    # 2) The ICS attachment
    ics_part = MIMEApplication(ics_content, _subtype="ics")
    ics_part.add_header(
        "Content-Disposition", f'attachment; filename="{ics_filename}"'
    )
    # These headers help Outlook/Gmail treat it as a calendar invite
    ics_part.add_header("Content-Class", "urn:content-classes:calendarmessage")
    ics_part.add_header("Method", "REQUEST")
    msg.attach(ics_part)

    # 3) SES send_raw_email
    response = ses_client.send_raw_email(
        Source=sender,
        Destinations=[recipient],
        RawMessage={"Data": msg.as_string()},
    )
    return response
