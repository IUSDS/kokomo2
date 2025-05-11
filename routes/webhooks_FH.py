from fastapi import APIRouter, HTTPException, Request
from utils.secrets import SECRET_KEY
import hmac
import hashlib
from utils.booking_parser import parse_booking_payload
from utils.booking_db import store_booking_to_db
from utils.session import get_logged_in_member_id_from_email
from utils.yacht_id import get_yacht_id_by_name
from utils.tour_type_id import get_tour_id_by_name
from utils.point_pricing import get_point_cost
from utils.update_points import deduct_member_points

# Initialize router
webhook_route = APIRouter()

@webhook_route.post("/webhook")
async def webhook_listener(request: Request):
    try:
        payload = await request.json()
        raw_body = await request.body()

        # Compute signature (optional but recommended for security)
        computed_signature = hmac.new(
            bytes.fromhex(SECRET_KEY),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        print("Computed Signature:", computed_signature)

        # Check if the 'booking' data exists in the payload
        booking_data = payload.get("booking")
        if not booking_data:
            raise HTTPException(status_code=400, detail="Invalid payload: 'booking' key missing")
        
        print(booking_data)

        # Extract email from booking data safely
        email = booking_data.get('contact', {}).get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Email missing in booking data")

        print("Processing Booking")
        
        # Retrieve member ID based on the email
        member_id = get_logged_in_member_id_from_email(email)
        print("MemberID:", member_id)
        
        yacht = booking_data.get('availability', {}).get('item', {}).get('name')
        print("Yacht:", yacht)
        yacht_id = get_yacht_id_by_name(yacht)
        if not yacht_id:
            raise ValueError(f"Yacht '{yacht}' not found")
        print("Yacht id: ", yacht_id)
        
        start_at = booking_data.get('availability', {}).get('start_at')
        print("Starting time: ", start_at)
        
        tour_type = booking_data.get('availability', {}).get('headline')
        print("TourType:", tour_type)
        tour_type_id = get_tour_id_by_name(tour_type, start_at)
        print("Tour typr id: ", tour_type_id)
        
        point_cost = get_point_cost(yacht_id, tour_type_id)
        print("Point cost: ", point_cost)
        
        success = deduct_member_points(member_id, point_cost)
        if success:
            print("Points updated.")
        else:
            print("No matching member found or points not updated.")

        # Parse & store booking data
        parsed_data = parse_booking_payload(booking_data, member_id)
        # print(parsed_data)
        store_booking_to_db({"data": parsed_data})

        return {"status": "success", "message": "Booking processed"}

    except Exception as e:
        print("Webhook Error:", e)
        raise HTTPException(status_code=400, detail=f"Webhook failed: {e}")
    try:
        # Read and verify request
        payload = await request.json()
        raw_body = await request.body()

        computed_signature = hmac.new(
            bytes.fromhex(SECRET_KEY),
            raw_body,
            hashlib.sha256
        ).hexdigest()

        print("Computed Signature:", computed_signature)

        # Extract booking payload
        event_type = payload.get("event")
        booking_data = payload

        if event_type == "order_created":
            print("Processing Order Created")

            # TEMP: Hardcode or dynamically assign member_id
            member_id = 1053  # Replace with real logic if available

            # Parse booking data
            parsed_data = parse_booking_payload(booking_data, member_id)
            print(parsed_data)

            # Store to DB
            store_booking_to_db({"data": parsed_data})

        elif event_type == "order_cancelled":
            print("Order Cancelled — no DB action taken.")
        else:
            print("Unhandled Event:", event_type)

        return {"status": "success", "message": "Webhook processed"}

    except Exception as e:
        print("Webhook Error:", e)
        raise HTTPException(status_code=400, detail=f"Webhook failed: {e}")
