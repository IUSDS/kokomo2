from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from utils.db_util import get_db_connection

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
    response_model=List[Dict[str, Any]],
    summary="Return bookings for one member"
)
async def get_bookings_by_member(member_id: str):
    """
    Retrieve availability, booking_id, item, contact, debit, credit, total_points
    for one member
    """
    sql = """
        SELECT
          CONCAT(b.start_at, ' – ', b.end_at) AS availability,
          b.booking_id,
          b.tour_type      AS item,
          m.phone_number   AS contact,
          b.receipt_total_display AS debit,
          NULL                   AS credit,
          NULL                   AS total_points
        FROM booking_fh b
        LEFT JOIN Members m ON m.member_id = b.member_id
        WHERE b.member_id = %s
        ORDER BY b.start_at;
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (member_id,))
            rows = cursor.fetchall()
            if not rows:
                raise HTTPException(status_code=404, detail=f"No bookings found for member_id {member_id}")
            return rows
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {e}")
    finally:
        conn.close()
