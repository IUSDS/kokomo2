from fastapi import APIRouter, HTTPException, Request
from utils.secrets_util import SECRET_KEY
from utils.booking_util import parse_booking_payload, store_booking_to_db, if_booking_exists, charter_booking_exists, determine_source
from utils.session_util import get_logged_in_member_id_from_email
from utils.yacht_util import get_yacht_id_by_name
from utils.tour_util import get_tour_id_by_name
from utils.member_util import get_member_name
from utils.point_pricing_util import get_point_cost, deduct_member_points, get_curr_points
from utils.json_sanitizer import parse_clean_json
from routes.websocket import active_connections
from emails.owner_notification import send_invite
from emails.low_points import low_points_notification

webhook_route = APIRouter()

@webhook_route.post("/webhook")
async def webhook_listener(request: Request):
    try:
        raw_body = await request.body()
        # print("Raw request body:", raw_body.decode("utf-8"))
        
        payload = await parse_clean_json(request)
        print("Cleaned payload:", payload)
    except Exception as e:
        print(f"JSON parse error: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    booking_data = payload.get("booking")
    if not isinstance(booking_data, dict):
        raise HTTPException(status_code=400, detail="Missing 'booking' object")
    # 3. Extract booking PK / UUID 
    booking_pk = booking_data.get("pk")
    booking_uuid = booking_data.get("uuid")
    print(f"INFO: Booking received: pk={booking_pk}, uuid={booking_uuid}")

    # 4. Contact info
    contact       = booking_data.get("contact", {}) or {}
    contact_name  = contact.get("name")
    contact_email = contact.get("email")
    contact_phone = contact.get("phone")
    print(f"INFO: Contact: name={contact_name}, email={contact_email}, phone={contact_phone}")

    # 5. Availability
    availability    = booking_data.get("availability", {}) or {}
    yacht_item      = availability.get("item", {}) or {}
    yacht_name      = yacht_item.get("name")
    tour_type_name  = availability.get("headline")
    start_at        = availability.get("start_at")
    end_at          = availability.get("end_at")
    print(f"INFO: Availability: yacht_name={yacht_name}, tour_type={tour_type_name}, start_at={start_at}, end_at={end_at}")
    
    # Determine webhook source and handle accordingly
    webhook_source = determine_source(yacht_name)
    print("INFO: This webhook originates from", webhook_source)
    
    if webhook_source.upper() == "CHARTERS":
        # Handle CHARTERS bookings - only send owner notification
        if charter_booking_exists(booking_pk):
            print("WARNING: Charter booking already exists!")
            raise HTTPException(status_code=409, detail="Charter booking already exists")
        
        # Send calendar invite to owner for charter bookings
        send_invite(yacht_name, tour_type_name, start_at, end_at, contact_email)
        print("INFO: Charter owners notified")
        
        return {"booking_status": "charter_notification_sent"}
    
    else:
        # Handle KYC bookings - full processing
        if if_booking_exists(booking_pk):
            print("WARNING: KYC booking already exists!")
            raise HTTPException(status_code=409, detail="KYC booking already exists")

        # 6. Send calendar invite
        send_invite(yacht_name, tour_type_name, start_at, end_at, contact_email)
        print("KYC Owners Notified")
        
        # 7. Lookup member_id
        member_id = None
        if contact_email:
            member_id = get_logged_in_member_id_from_email(contact_email)
            if member_id:
                print(f"INFO: Member ID found: {member_id}")
            else:
                print(f"WARNING: No member found for {contact_email}")
        else:
            print("WARNING: No email provided; skipping member lookup")

        # 8. Lookup yacht_id / tour_type_id
        yacht_id = get_yacht_id_by_name(yacht_name) if yacht_name else None
        if not yacht_id:
            print("WARNING: Yacht ID not found!")
            raise HTTPException(status_code=400, detail=f"Yacht '{yacht_name}' not found")
        print(f"INFO: Yacht ID: {yacht_id}")

        tour_type_id = get_tour_id_by_name(tour_type_name, start_at) if tour_type_name else None
        if tour_type_name and tour_type_id is None:
            print(f"WARNING: Tour type not found: {tour_type_name}")
        print(f"INFO: Tour Type ID: {tour_type_id}")

        # 9. Calculate point cost
        point_cost = get_point_cost(yacht_id, tour_type_id)
        print(f"INFO: Point cost: {point_cost}")

        # 10. Check for low points
        curr_points = get_curr_points(member_id) if member_id else None
        if point_cost >= curr_points:
            name       = get_member_name(member_id)
            first_name = name.get("first_name")
            last_name  = name.get("last_name")
            low_points_notification(first_name, last_name, curr_points, point_cost)

        # 11. Store booking
        try:
            parsed_data = parse_booking_payload(booking_data, int(member_id) if member_id else 0, point_cost)
            store_booking_to_db({"data": parsed_data})
            print(f"INFO: Booking stored: pk={booking_pk}")
        except Exception as e:
            print(f"EXCEPTION: Failed to store booking: {e}")
            raise HTTPException(status_code=500, detail="Failed to save booking")

        # 12. Deduct points
        if member_id:
            success = deduct_member_points(member_id, booking_pk, point_cost)
            if success:
                print(f"INFO: Deducted {point_cost} points from member {member_id}")
            else:
                print(f"WARNING: Could not deduct points for member {member_id}")
        else:
            print("INFO: Skipping point deduction (no member)")

        # 13. Send WebSocket notification
        curr_points = get_curr_points(member_id) if member_id else None
        ws_payload = {
            "event": "booking_success",
            "point_used": point_cost,
            "yacht_name": yacht_name,
            "current_points": curr_points
        }
        if member_id and member_id in active_connections:
            try:
                await active_connections[member_id].send_json(ws_payload)
                print(f"INFO: WebSocket notification sent to {member_id}")
            except Exception as e:
                print(f"EXCEPTION: Failed WebSocket send: {e}")

        return {"booking_status": "successful"}