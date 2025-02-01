from fastapi import APIRouter, HTTPException, Query
from utils.database import get_db_connection

# Initialize router
get_points_route = APIRouter()

@get_points_route.get("/points/")
async def get_points(username: str = Query(..., description="The username to retrieve points for")):
    """
    Retrieve points for the given username.
    """
    query = """
        SELECT points
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

            return {"username": username, "points": result["points"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        connection.close()
