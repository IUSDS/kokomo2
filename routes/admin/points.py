from fastapi import APIRouter, HTTPException, Form, Query
from utils.database import get_db_connection

points_route = APIRouter()

# Endpoint to update points for a user
@points_route.put("/update-points/")
async def update_points(username: str = Form(...), update_points: int = Form(...)):
    """
        Update points for the given username.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if the username exists
        cursor.execute("SELECT points FROM Members WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result is None:
            return {"status": "error", "message": "Username not found"}

        # Update the points column
        current_points = result["points"]
        new_points = current_points + update_points

        cursor.execute("UPDATE Members SET points = %s WHERE username = %s", (new_points, username))
        connection.commit()

        return {
            "status": "success",
            "message": f"Points updated successfully. Total points for {username}: {new_points}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@points_route.get("/points/")
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