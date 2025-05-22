from fastapi import APIRouter, HTTPException, Form, Query
from utils.db_util import get_db_connection

points_route = APIRouter()

# Endpoint to update points for a user
@points_route.put("/update-points/")
async def update_points(
    username: str      = Form(...),
    update_points: int = Form(...),
    description: str   = Form(...),
):
    """
    Update points for the given username and record the change with a custom description.
    """
    conn   = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1) Fetch member ID and current points
        cursor.execute(
            "SELECT member_id, points FROM Members WHERE username = %s AND is_deleted = 'N'",
            (username,),
        )
        row = cursor.fetchone()
        if not row:
            return {"status": "error", "message": "Username not found"}

        member_id      = row["member_id"]
        current_points = row["points"]
        new_points     = current_points + update_points

        # 2) Update Members table
        cursor.execute(
            "UPDATE Members SET points = %s WHERE member_id = %s",
            (new_points, member_id),
        )

        # 3) Insert into Point_Adjustment using the passed-in description
        points_added   = max(update_points, 0)
        points_removed = max(-update_points, 0)
        cursor.execute(
            """
            INSERT INTO Point_Adjustment
              (member_id, points_added, points_removed, description)
            VALUES (%s, %s, %s, %s)
            """,
            (member_id, points_added, points_removed, description),
        )

        # 4) Commit both operations
        conn.commit()

        return {
            "status": "success",
            "message": (
                f"Points for {username} updated: "
                f"{current_points} → {new_points}"
            ),
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    finally:
        cursor.close()
        conn.close()

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
        