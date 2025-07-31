from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from utils.db_util import get_db_connection
from utils.point_pricing_util import get_opening_balance
from pydantic import BaseModel
from typing import List,Optional,Union
from datetime import datetime
from utils.member_util import get_if_primary_or_secondary, get_primary_for_secondary
import pandas as pd

class BookingOut(BaseModel):
    member_id: int
    item: Optional[str] = None
    booking_id: Optional[str] = None
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    tour_type: Optional[str] = None
    points_cost: Optional[Union[int, str]] = None
    status: Optional[str] = None
    balance_after_booking: Optional[Union[int, str]] = None
    # Fields from Point_Adjustment
    points: Optional[str] = None
    balance: Optional[Union[int, str]] = None
    description: Optional[str] = None
    date: Optional[str] = None
    source: Optional[str] = None
    

class BookingResponse(BaseModel):
    member_id: int
    opening_balance: float
    data: List[BookingOut]


booking_route = APIRouter()

# 1. ALL BOOKINGS
@booking_route.get(
    "/admin/",
    response_model=List[Dict[str, Any]],
    summary="Admin: return booking fields for a specific user"
)
async def get_booking_fh_for_user(username: str):
    """
    Retrieve for the given username:
      • S no.
      • username
      • booking_id
      • dashboard_url (as modify_view)
      • vessel_name
      • tour_type
      • points_used
      • booking_status
    """
    sql = """
        SELECT
          bf.id                AS `S no.`,
          m.username           AS username,
          bf.booking_id        AS booking_id,
          bf.dashboard_url     AS modify_view,
          bf.vessel_name       AS vessel_name,
          bf.tour_type         AS tour_type,
          bf.points_cost       AS points_used,
          bf.booking_status    AS booking_status
        FROM booking_fh bf
        JOIN Members m ON bf.member_id = m.member_id
        WHERE m.username = %s
        ORDER BY bf.id;
    """

    # -- simple debug print before you execute --
    print("DEBUG SQL:", sql.replace("\n", " "), "| PARAMS:", username)

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (username,))
            rows = cursor.fetchall()
            if not rows:
                raise HTTPException(404, f"No bookings for '{username}'")
            return rows

    except Exception as e:
        # you’ll now see exactly the SQL and params in your console above
        raise HTTPException(status_code=500, detail=f"Database query error: {e}")
    finally:
        conn.close()


# 2. BOOKINGS FOR A SINGLE MEMBER
@booking_route.get(
    "/member/{member_id}",
    response_model=BookingResponse,
    summary="Return bookings for one member"
)
async def get_bookings_with_adjustments_by_member(member_id: str):
    is_primary = get_if_primary_or_secondary(member_id)
    if not is_primary:
        member_id = get_primary_for_secondary(member_id)

    # 🔹 Step 1: SQL for transactions (without opening_balance in each row)
    sql = """
    SELECT * FROM (
        SELECT 
            b.member_id,
            b.vessel_name AS item,
            b.booking_id,
            b.start_at,
            b.end_at,
            b.tour_type,
            b.points_cost,
            b.booking_status AS status,
            b.balance_after_booking,
            NULL AS points,
            NULL AS balance,
            NULL AS description,
            NULL AS date,
            'Booking' AS source
        FROM booking_fh b
        WHERE b.member_id = %s

        UNION ALL

        SELECT 
            p.member_id,
            NULL AS item,
            NULL AS booking_id,
            NULL AS start_at,
            NULL AS end_at,
            NULL AS tour_type,
            NULL AS points_cost,
            NULL AS status,
            NULL AS balance_after_booking,
            CASE
                WHEN p.points_added != 0 THEN CONCAT('+', p.points_added)
                WHEN p.points_removed != 0 THEN CONCAT('-', p.points_removed)
                ELSE NULL
            END AS points,
            p.Balance AS balance,
            p.description AS description,
            p.created_at AS date,
            'Point Adjustment' AS source
        FROM Point_Adjustment p
        WHERE p.member_id = %s
    ) combined_data
    ORDER BY 
        CASE WHEN date IS NULL THEN 1 ELSE 0 END,
        date ASC;
    """

    # 🔹 Step 2: SQL for opening_balance
    opening_balance_query = """
        SELECT opening_balance FROM Members WHERE member_id = %s
    """

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:

            # 🔸 Step 3: Fetch opening_balance separately
            cursor.execute(opening_balance_query, (member_id,))
            opening_balance_result = cursor.fetchone()
            if not opening_balance_result:
                raise HTTPException(status_code=404, detail="Member not found")
            opening_balance = opening_balance_result.get("opening_balance", 0)

            # 🔸 Step 4: Fetch transaction records
            cursor.execute(sql, (member_id, member_id))
            rows = cursor.fetchall()

            # 🔸 Step 5: Process and format rows
            processed_rows = []
            for row in rows:
                if row.get('date') and isinstance(row['date'], datetime):
                    row['date'] = row['date'].strftime('%Y-%m-%d %H:%M:%S')
                if row.get('member_id'):
                    row['member_id'] = int(row['member_id'])
                processed_rows.append(row)

            # 🔸 Step 6: Validate using BookingOut
            validated_rows = []
            for row in processed_rows:
                try:
                    validated_rows.append(BookingOut(**row))
                except Exception as e:
                    print("Validation error on row:", row)
                    print("Error:", e)
                    raise HTTPException(status_code=500, detail="Data format mismatch.")

            # 🔸 Step 7: Return structured response with separate opening_balance
            return {
                "member_id": member_id,
                "opening_balance": opening_balance,
                "data": validated_rows
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {e}")
    finally:
        conn.close()
