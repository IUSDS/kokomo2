from utils.point_pricing_util import get_opening_balance
from utils.member_util import get_if_primary_or_secondary, get_primary_for_secondary
from fastapi import APIRouter, HTTPException
from utils.db_util import get_db_connection


async def get_bookings_with_adjustments_by_member(member_id: str):
    is_primary = get_if_primary_or_secondary(member_id)
    if not is_primary:
        member_id = get_primary_for_secondary(member_id)

    sql = """
        SELECT 
            b.vessel_name As Item,
            b.booking_id As Booking_ID ,
            b.member_id,
            b.id AS booking_record_id,
            b.booking_status as Status,
            p.id AS adjustment_id,
            CASE
                WHEN p.points_added != 0 THEN CONCAT('+', p.points_added)
                WHEN p.points_removed != 0 THEN CONCAT('-', p.points_removed)
                ELSE NULL
                END AS Points
            p.description As Description,
            p.created_at As Date
        FROM bookings_fh b
        JOIN Point_Adjustment p ON b.member_id = p.member_id
        WHERE b.member_id = %s
        ORDER BY p.created_at DESC;
    """

    conn = get_db_connection()
    # try:
    #     with conn.cursor() as cursor:
    #         cursor.execute(sql, (member_id,))
    #         rows = cursor.fetchall()
    #         return {
    #             "member_id": member_id,
    #             "data": rows
    #         }

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (member_id,))
            columns = [desc[0] for desc in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return {
                "member_id": member_id,
                "data": rows
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {e}")
    finally:
        conn.close()