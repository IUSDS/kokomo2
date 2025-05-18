from fastapi import HTTPException
from utils.db_util import get_db_connection
import traceback
import re

def store_booking_to_db(payload: dict):
    connection = None
    cursor = None
    try:
        data = payload.get("data", {})
        member_id = data.get("member_id")
        # print(member_id)

        if not member_id:
            raise HTTPException(status_code=400, detail="member_id is required in the payload.")

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT 1 FROM Members WHERE member_id = %s", (member_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"member_id {member_id} does not exist in Members table.")

        insert_query = """
            INSERT INTO booking_fh (
                member_id, booking_id, dashboard_url, created_at, start_at, end_at, vessel_name, tour_type,
                pickup_point, invoice_price_display, amount_paid_display, receipt_subtotal_display, receipt_taxes_display,
                receipt_total_display, e_foil_count, sea_bob_count, other_add_ons, adult_beverages, catering_option,
                number_of_kids, number_of_adults
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (
            member_id,
            data.get("booking_id"),
            data.get("dashboard_url"),
            data.get("created_at"),
            data.get("start_at"),
            data.get("end_at"),
            data.get("vessel_name"),
            data.get("tour_type"),
            data.get("pickup_point"),
            data.get("invoice_price_display"),
            data.get("amount_paid_display"),
            data.get("receipt_subtotal_display"),
            data.get("receipt_taxes_display"),
            data.get("receipt_total_display"),
            data.get("e_foil_count"),
            data.get("sea_bob_count"),
            data.get("other_add_ons"),
            data.get("adult_beverages"),
            data.get("catering_option"),
            data.get("number_of_kids"),
            data.get("number_of_adults")
        ))

        connection.commit()
        return {"status": "success", "message": "Booking stored in database."}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving booking: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def extract_int(value, default=0):
    """
    Extracts the first integer from a string like "6 People" or returns the integer if already one.
    Returns the default if no valid number is found.
    """
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r'\d+', value)
        return int(match.group()) if match else default
    return default

def parse_booking_payload(booking: dict, member_id: int) -> dict:
    availability = booking.get("availability", {})
    custom_fields = booking.get("custom_field_values", [])

    def get_custom_value(name: str, default=None):
        for field in custom_fields:
            if field.get("name") == name:
                return field.get("display_value") or field.get("value") or default
        return default

    return {
        "member_id": member_id,
        "booking_id": booking.get("pk"),
        "dashboard_url": booking.get("dashboard_url"),
        "created_at": booking.get("created_at"),
        "start_at": availability.get("start_at"),
        "end_at": availability.get("end_at"),
        "vessel_name": booking.get("availability", {}).get("item", {}).get("name", "Unknown"),
        "tour_type": booking.get("availability", {}).get("headline", "Unknown"),
        "pickup_point": get_custom_value("Pick Up Locations - KYC", ""),
        "invoice_price_display": booking.get("invoice_price_display"),
        "amount_paid_display": booking.get("amount_paid_display"),
        "receipt_subtotal_display": booking.get("receipt_subtotal_display"),
        "receipt_taxes_display": booking.get("receipt_taxes_display"),
        "receipt_total_display": booking.get("receipt_total_display"),
        "other_add_ons": get_custom_value("Additional Add Ons - flowers, music, etc", "No"),
        "adult_beverages": get_custom_value("Adult Beverages", "No"),
        "catering_option": get_custom_value("Catering Option?", "No"),
        "number_of_adults": extract_int(get_custom_value("How many people are in your party? (no pricing)")),
        "number_of_kids": extract_int(get_custom_value("How many kids in your party are under 6?")),
        "e_foil_count": extract_int(get_custom_value("E-foil")),
        "sea_bob_count": extract_int(get_custom_value("Sea Bob")),
    }
