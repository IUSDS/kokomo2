from typing import List
from fastapi import APIRouter, HTTPException
from utils.database import get_db_connection

booking_route = APIRouter()

# 1. ALL BOOKINGS
@booking_route.get(
    "/bookings/",
    response_model=List[dict],
    summary="Return all booking records"
)
async def get_all_bookings():
    sql = """
        SELECT
            CONCAT(b.start_at, ' – ', b.end_at) AS availability,
            b.booking_id,
            b.tour_type      AS item,
            CONCAT(m.first_name, ' ', m.last_name) AS contact,
            b.receipt_total_display AS debit,
            NULL                   AS credit,
            NULL                   AS total_points
        FROM booking_fh b
        LEFT JOIN Members m ON m.member_id = b.member_id
        ORDER BY b.start_at;
    """

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    except Exception as e:
        raise HTTPException(500, f"DB error: {e}")
    finally:
        conn.close()


# 2. BOOKINGS FOR A SINGLE MEMBER
@booking_route.get(
    "/bookings/{member_id}",
    response_model=List[dict],
    summary="Return bookings for one member"
)
async def get_bookings_by_member(member_id: str):
    sql = """
        SELECT
            CONCAT(b.start_at, ' – ', b.end_at) AS availability,
            b.booking_id,
            b.tour_type      AS item,
            m.phone_number AS contact,
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
        with conn.cursor() as cur:
            cur.execute(sql, (member_id,))
            rows = cur.fetchall()
            if not rows:
                raise HTTPException(404, f"No bookings found for member_id {member_id}")
            return rows
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"DB error: {e}")
    finally:
        conn.close()
