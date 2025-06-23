import uuid
from datetime import datetime, timedelta
import pytz
import boto3
from icalendar import Calendar, Event, Alarm, vCalAddress, vText
from email.mime.application import MIMEApplication
from email.mime.multipart   import MIMEMultipart
from email.mime.text        import MIMEText
from dateutil.parser import isoparse
from utils.yacht_util import get_mapped_yacht_name_for_invite, get_yacht_id_for_invite
from utils.owner_util import get_owner_by_yacht_id

# SES client (region ap-southeast-2)
ses_client = boto3.client("ses", region_name="ap-southeast-2")

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

def send_invite(yacht_name: str, tour_type_name: str, start_at: str, end_at: str):
    if yacht_name and start_at and end_at:
        yacht_id_tmp = get_yacht_id_for_invite(yacht_name)
        owner = get_owner_by_yacht_id(yacht_id_tmp) if yacht_id_tmp else None
        print("Owner: ", owner)
        yatch_base_name = get_mapped_yacht_name_for_invite(yacht_name)
        if owner:
            try:
                owner_data = owner[0]
                owner_name = owner_data["owner_name"]
                owner_emails = owner_data["owner_emails"]

                for email in owner_emails:
                    print(f"INFO: Owner for yacht '{yacht_name}': {owner_name} <{email}>")

                    start_dt = isoparse(start_at)
                    end_dt   = isoparse(end_at)
                    eastern  = pytz.timezone("America/New_York")
                    start_local = start_dt.astimezone(eastern).strftime("%d %b %Y, %I:%M %p %Z")
                    end_local   = end_dt.astimezone(eastern).strftime("%d %b %Y, %I:%M %p %Z")

                    summary     = f"Kokomo Yachts: {yatch_base_name} Booked"
                    description = (
                        f"Hello {owner_name},\n\n"
                        f"Your yacht '{yatch_base_name}' was just booked.\n"
                        f"Start: {start_local}\n"
                        f"End:   {end_local}\n"
                        f"Tour Type: {tour_type_name or 'N/A'}\n\n"
                        "Thank you for partnering with Kokomo Yachts!\n"
                        "— Kokomo Crew"
                    )
                    ics_bytes = build_invite(
                        subject=summary,
                        description=description,
                        start_dt=start_dt,
                        end_dt=end_dt,
                        organizer_email="info@kokomoyachts.com",
                        organizer_name="Kokomo Crew"
                    )

                    body_text = (
                        f"Hi {owner_name},\n\n"
                        "Your yacht was just booked! Please open the attached .ics to add it to your calendar.\n\n"
                        f"Start: {start_local}\n"
                        f"End:   {end_local}\n\n"
                        "Best Regards,\n"
                        "Kokomo Crew\n"
                    )

                    send_calendar_invite(
                        sender="info@kokomoyachts.com",
                        recipient=email,
                        subject=summary,
                        body_text=body_text,
                        ics_content=ics_bytes,
                        ics_filename=f"Yacht_{yatch_base_name}_Booked.ics"
                    )

                    print(f"INFO: Sent early .ics invite to {email}")

            except Exception as e:
                print(f"ERROR: Failed to send early calendar invite: {e}")
        else:
            print(f"WARNING: No owner found for yacht '{yacht_name}'")
    else:
        print("WARNING: Missing yacht_name or start/end time; skipping early invite")
