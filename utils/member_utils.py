from fastapi import Request, HTTPException
from utils.db_util import get_db_connection
from pymysql.cursors import DictCursor
from utils.session_util import get_logged_in_username

def get_if_primary_or_secondary(member_id: int) -> bool:
    try:
        connection = get_db_connection()
        cursor = connection.cursor(DictCursor)
        
        cursor.execute("""
            SELECT is_primary
            FROM Members 
            WHERE member_id = %s AND is_deleted = 'N'
            LIMIT 1
        """, (member_id,))
        
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        print(result)

        return result["is_primary"] == 1

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
def get_primary_for_secondary(member_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(DictCursor)
        
        cursor.execute("""
            SELECT primary_member_id
            FROM Members 
            WHERE member_id = %s AND is_deleted = 'N'
            LIMIT 1
        """, (member_id,))
        
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result["primary_member_id"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
