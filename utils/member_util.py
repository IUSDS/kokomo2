from fastapi import Request, HTTPException
from utils.db_util import get_db_connection
from pymysql.cursors import DictCursor
from utils.session_util import get_logged_in_username

def get_if_primary_or_secondary(member_id: int) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor(DictCursor)
        
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
        if conn:
            conn.close()
            
def get_primary_for_secondary(member_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(DictCursor)
        
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
        if conn:
            conn.close()
            
def get_member_name(member_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(DictCursor)
        
        cursor.execute("""
            SELECT username, first_name, last_name 
            FROM Members 
            WHERE member_id = %s;
        """, (member_id,))
        
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "username": result["username"],
            "first_name": result["first_name"],
            "last_name": result["last_name"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()