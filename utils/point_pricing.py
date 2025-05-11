from typing import Optional
from utils.database import get_db_connection

def get_point_cost(yacht_id: str, tour_type_id: str) -> Optional[int]:
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT point_cost 
            FROM yacht_tour_pricing 
            WHERE yacht_id = %s AND tour_type_id = %s 
            LIMIT 1
            """,
            (yacht_id, tour_type_id)
        )
        row = cursor.fetchone()
        return row['point_cost'] if row else None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
