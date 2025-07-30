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
        if not member_id:
            raise HTTPException(status_code=400, detail="member_id is required in the payload.")

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM Members WHERE member_id = %s", (member_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"member_id {member_id} does not exist in Members table.")

        insert_query = """
            INSERT INTO booking_fh (
                member_id, booking_id, dashboard_url, created_at, start_at, end_at,
                vessel_name, tour_type, pickup_point,
                invoice_price_display, amount_paid_display,
                receipt_subtotal_display, receipt_taxes_display, receipt_total_display,
                other_add_ons, adult_beverages, catering_option,
                number_of_kids, number_of_adults,
                e_foil_count, sea_bob_count, tubing,
                other_cost, other_cost_desc, staff_gratuity,
                booking_status, amount_due, booking_fee,
                created_by, points_cost
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s
            )
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
            data.get("other_add_ons"),
            data.get("adult_beverages"),
            data.get("catering_option"),
            data.get("number_of_kids"),
            data.get("number_of_adults"),
            data.get("e_foil_count"),
            data.get("sea_bob_count"),
            data.get("tubing"),
            data.get("other_cost"),
            data.get("other_cost_desc"),
            data.get("staff_gratuity"),
            data.get("booking_status"),
            data.get("amount_due"),
            data.get("booking_fee"),
            data.get("created_by"),
            data.get("point_cost"),
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

def parse_booking_payload(
    booking: dict,
    member_id: int,
    point_cost: int,
    booking_fee: float = 0.0
) -> dict:
    availability = booking.get("availability", {})
    custom_fields = booking.get("custom_field_values", [])
    
    print("Parse_booking_util:")
    print(point_cost, member_id)

    def get_custom_value(name: str, default=None):
        for field in custom_fields:
            if field.get("name") == name:
                return field.get("display_value") or field.get("value") or default
        return default

    # yes/no fields come through as "Yes"/"No" or True/False
    def yn(name: str):
        val = get_custom_value(name, "No")
        return "yes" if str(val).lower() in ("yes", "true") else "no"

    # compute amount still due
    receipt_total = booking.get("receipt_total_display", 0)
    amount_paid = booking.get("amount_paid_display", 0)
    amount_due = float(receipt_total) - float(amount_paid)
    print("Receipt Total: ", receipt_total)
    print("Amount Paid: ", amount_paid)
    print("Amount Due: ", amount_due)

    return {
        "member_id": member_id,
        "booking_id": booking.get("pk"),
        "dashboard_url": booking.get("dashboard_url"),
        "created_at": booking.get("created_at"),
        "start_at":        availability.get("start_at"),
        "end_at":          availability.get("end_at"),
        "vessel_name":     availability.get("item", {}).get("name", "Unknown"),
        "tour_type":       availability.get("headline", "Unknown"),
        "pickup_point":    get_custom_value("Pick Up Locations - KYC", ""),
        "invoice_price_display": booking.get("invoice_price_display"),
        "amount_paid_display":   booking.get("amount_paid_display"),
        "receipt_subtotal_display": booking.get("receipt_subtotal_display"),
        "receipt_taxes_display":    booking.get("receipt_taxes_display"),
        "receipt_total_display":    booking.get("receipt_total_display"),
        "other_add_ons":   get_custom_value("Add ons", "No"),
        "adult_beverages": yn("Adult Beverages"),
        "catering_option": yn("Catering Option?"),
        "number_of_adults": extract_int(get_custom_value(
            "How many people are in your party? (no pricing)", 0)),
        "number_of_kids":   extract_int(get_custom_value(
            "How many kids in your party are under 6?", 0)),
        "e_foil_count":     extract_int(get_custom_value("E-foil", 0)),
        "sea_bob_count":    extract_int(get_custom_value("Sea Bob", 0)),
        # the three fields you don’t have in payload yet:
        "other_cost":       0.00,
        "other_cost_desc":  "",
        "staff_gratuity":   0.00,
        "tubing":           yn("Tubing"),
        # fixed/status fields:
        "booking_status":   "scheduled",
        "amount_due":       amount_due,
        "booking_fee":      booking_fee,
        "created_by":       member_id,
        "point_cost":       point_cost,
    }

def if_booking_exists(booking_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(booking_id)
            FROM booking_fh
            WHERE booking_id = %s;
        """, (booking_id,))
       
        result = cursor.fetchone()

        print('>>>>>>> result', result)
        count = result['COUNT(booking_id)']
        if count == 0:
            return False
        else:
            return True
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_points_cost_from_booking_fh(booking_id:str):
    try:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("""
            SELECT points_cost,member_id
            FROM booking_fh
            WHERE booking_id = %s;
            """,(booking_id,))
        result=cursor.fetchone()
        print('>>>>>>> result', result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_points_from_members(member_id:int):
    try:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("""
            SELECT points
            FROM Members
            WHERE member_id = %s;
            """,(member_id,))
        result=cursor.fetchone()
        print('<<<<result',result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def new_record_in_point_adjustment(member_id:int,points_added:int,Balance:int,description:str):     ### After cancellation points adjustments
    try:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("""
            INSERT INTO Point_Adjustment(member_id,points_added,Balance,description)
            Values(%s,%s,%s,%s);
            """,(member_id, points_added, Balance, description))
        conn.commit()

        # Fetch the most recent matching record
        cursor.execute("""
            SELECT * FROM Point_Adjustment
            WHERE member_id = %s AND points_added = %s AND Balance = %s AND description = %s
            ORDER BY created_at DESC
            LIMIT 1;
        """, (member_id, points_added, Balance, description))
        inserted_record = cursor.fetchone()
        return inserted_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()







# def if_booking_exists(booking_id: str, status: str):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         cursor.execute("""
#             SELECT COUNT(booking_id)
#             FROM booking_fh
#             WHERE booking_id = %s;
#         """, (booking_id,))
       
#         result = cursor.fetchone()

#         print('>>>>>>> result', result)
#         count = result['COUNT(booking_id)']
#         if count == 0:
#             return False
#         else:
#             return True
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()