from fastapi import APIRouter, HTTPException, Query
from utils.db_util import get_db_connection

# Initialize router
get_membership_route = APIRouter()

@get_membership_route.get("/membership/")
async def get_membership_type(username: str = Query(..., description="The username to retrieve membership type for")):
    """
    Retrieve membership type for the given username.
    """
    query = """
        SELECT membership_type
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

            return {"username": username, "membership_type": result["membership_type"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        connection.close()