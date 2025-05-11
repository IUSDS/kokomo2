from fastapi import Request, HTTPException
from utils.db_util import get_db_connection
from pymysql.cursors import DictCursor

def get_logged_in_username(request: Request) -> str:
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Session expired or unauthorized")
    return username

def get_logged_in_member_id(request: Request) -> str:
    username = get_logged_in_username(request)
    try:
        connection = get_db_connection()
        cursor = connection.cursor(DictCursor)
        
        # Query to fetch member details based on the session (username)
        cursor.execute("""
            SELECT member_id
            FROM Members 
            WHERE LOWER(username) = LOWER(%s) AND is_deleted = 'N'
            LIMIT 1
        """, (username,))
        member = cursor.fetchone()
        
        if not member:
            raise HTTPException(status_code=404, detail="User not found.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
    return member["member_id"]

def get_logged_in_member_id_from_email(email) -> str:
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(DictCursor)
        
        # Query to fetch member details based on the session (email)
        cursor.execute("""
            SELECT member_id
            FROM Members 
            WHERE LOWER(email_id) = LOWER(%s) AND is_deleted = 'N'
            LIMIT 1
        """, (email,))
        member = cursor.fetchone()
        
        if not member:
            raise HTTPException(status_code=404, detail="User not found.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
    return member["member_id"]