from fastapi import APIRouter, HTTPException, Request
from utils.secrets import SECRET_KEY
import hmac
import hashlib
from utils.booking_parser import parse_booking_payload
from utils.booking_db import store_booking_to_db

# Initialize router
webhook_route = APIRouter()

@webhook_route.post("/webhook")
async def webhook_listener(request: Request):
    try:
        payload = await request.json()
        raw_body = await request.body()

        # Compute signature (optional for now)
        computed_signature = hmac.new(
            bytes.fromhex(SECRET_KEY),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        print("Computed Signature:", computed_signature)

        # Since there's no "event" or "data", just use payload directly
        booking_data = payload.get("booking")
        if not booking_data:
            raise HTTPException(status_code=400, detail="Invalid payload: 'booking' key missing")

        print("Processing Booking")
        member_id = 1053  # Use dynamic value if needed

        # Parse & store booking
        parsed_data = parse_booking_payload(booking_data, member_id)
        print(parsed_data)
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
