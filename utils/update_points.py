from utils.database import get_db_connection

def deduct_member_points(member_id: str, point_cost: int) -> bool:
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE Members 
            SET points = points - %s 
            WHERE member_id = %s
            """,
            (point_cost, member_id)
        )
        conn.commit()
        return cursor.rowcount > 0  # returns True if a row was updated

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
