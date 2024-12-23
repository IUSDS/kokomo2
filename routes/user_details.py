from fastapi import APIRouter, Query, HTTPException
from database import get_db_connection
from models import UserResponse
import pymysql

user_details_route = APIRouter()

@user_details_route.get("/", response_model=UserResponse)
async def get_user_details(username: str):
    query = """
        SELECT member_id, CONCAT(first_name, ' ', last_name) AS full_name, 
               membership_type, points, picture_url
        FROM Members
        WHERE username = %s AND is_deleted = "N"
        LIMIT 1
    """
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="User not found.")

            return {
                "member_id": result["member_id"],
                "full_name": result["full_name"],
                "membership_type": result["membership_type"],
                "points": result["points"],
                "picture_url": result["picture_url"],
            }

    except pymysql.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {e}")

    finally:
        connection.close()
