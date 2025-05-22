from typing import Optional
from utils.db_util import get_db_connection

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
            
def get_curr_points(member_id: str):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT points FROM Members
            WHERE member_id = %s
            """,
            (member_id)
        )
        row = cursor.fetchone()
        return row['points'] if row else None
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
def get_opening_balance(member_id: str):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT opening_balance FROM Members
            WHERE member_id = %s
            """,
            (member_id)
        )
        row = cursor.fetchone()
        return row['opening_balance'] if row else 0
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
