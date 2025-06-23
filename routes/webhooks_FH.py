from fastapi import APIRouter, HTTPException, Request
from utils.secrets_util import SECRET_KEY
import hmac
import hashlib
from utils.booking_utils import store_booking_to_db, parse_booking_payload
from utils.session_util import get_logged_in_member_id_from_email
from utils.yacht_util import get_yacht_id_by_name
from utils.tour_util import get_tour_id_by_name
from utils.point_pricing_util import get_point_cost, deduct_member_points, get_curr_points
from routes.websocket import active_connections

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
        
        # Retrives Yacht ID from DB
        yacht = booking_data.get('availability', {}).get('item', {}).get('name')
        print("Yacht:", yacht)
        yacht_id = get_yacht_id_by_name(yacht)
        if not yacht_id:
            raise ValueError(f"Yacht '{yacht}' not found")
        print("Yacht id: ", yacht_id)
        
        # We need Start time in case of Half Day reservation(tour_type) to know if the booking is morning or afternoon
        start_at = booking_data.get('availability', {}).get('start_at')
        print("Starting time: ", start_at)
        
        # Retrives tour_type id
        tour_type = booking_data.get('availability', {}).get('headline')
        print("TourType:", tour_type)
        tour_type_id = get_tour_id_by_name(tour_type, start_at)
        print("Tour type id: ", tour_type_id)
        
        # Retrives points cost using yacht_id and tour_type_id
        point_cost = get_point_cost(yacht_id, tour_type_id)
        print("Point cost: ", point_cost)

        # Parse & store booking data
        parsed_data = parse_booking_payload(booking_data, int(member_id), point_cost)
        # print(parsed_data)
        
        store_booking_to_db({"data": parsed_data})
        
        # Deducts points from Members table
        booking_id = booking_data.get('pk')
        print(booking_id)
        success = deduct_member_points(member_id, booking_id, point_cost)
        if success:
            print("Points updated.")
        else:
            print("No matching member found or points not updated.")
        
        curr_points = get_curr_points(member_id)

        # websocket payload
        payload = {
            "event": "booking_success",
            "point_used": point_cost,
            "yacht_name": yacht,   
            "current_points": curr_points
        }

        if member_id in active_connections:
            await active_connections[member_id].send_json(payload)
        return {
            "booking_status": "successful"
        }

    except Exception as e:
        print("Webhook Error:", e)
        raise HTTPException(status_code=400, detail=f"Webhook failed: {e}")