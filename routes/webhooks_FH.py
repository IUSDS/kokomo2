from fastapi import APIRouter, HTTPException, Request, FastAPI, Header
from pydantic import BaseModel
import hmac
import hashlib
from utils.secrets import SECRET_KEY

# Initialize router
webhook_route = APIRouter()

# Define a BaseModel for the payload
class WebhookPayload(BaseModel):
    event: str
    data: dict

@webhook_route.post("/webhook")
async def webhook_listener(request: Request):
    try:
        # Read the JSON payload from the request
        payload = await request.json()
        print("Received Payload:", payload)

        # Retrieve the raw body of the request for hash verification
        raw_body = await request.body()

        # Compute the HMAC-SHA256 hash using the secret key
        computed_signature = hmac.new(
            bytes.fromhex(SECRET_KEY),
            raw_body,
            hashlib.sha256
        ).hexdigest()

        # Log the computed signature (optional)
        print("Computed Signature:", computed_signature)

        # Process the payload
        event_type = payload.get("event")
        if event_type == "order_created":
            print("Order Created:", payload["data"])
        elif event_type == "order_cancelled":
            print("Order Cancelled:", payload["data"])
        else:
            print("Unhandled Event:", event_type)

        # Return a success response
        return {"status": "success", "message": "Webhook received"}
    except Exception as e:
        # Handle errors
        print("Error processing webhook:", e)
        raise HTTPException(status_code=400, detail=f"Error processing webhook: {e}")