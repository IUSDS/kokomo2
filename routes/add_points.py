from fastapi import APIRouter, HTTPException, Form
from database import get_db_connection

update_points_route = APIRouter()

# Endpoint to update points for a user
@update_points_route.put("/update-points/")
async def update_points(username: str = Form(...), update_points: int = Form(...)):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

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
