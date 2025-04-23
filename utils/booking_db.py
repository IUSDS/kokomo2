from fastapi import HTTPException
from utils.database import get_db_connection
import traceback

def store_booking_to_db(payload: dict):
    connection = None
    cursor = None
    try:
        data = payload.get("data", {})
        member_id = data.get("member_id")
        print(member_id)

        if not member_id:
            raise HTTPException(status_code=400, detail="member_id is required in the payload.")

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT 1 FROM Members WHERE member_id = %s", (member_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"member_id {member_id} does not exist in Members table.")

        insert_query = """
            INSERT INTO Bookings (
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
