from fastapi import APIRouter, HTTPException, Form
from utils.db_util import get_db_connection

# Initialize router
delete_user_route = APIRouter()

@delete_user_route.put("/delete/")
async def delete_user(
    username: str = Form(..., description="The username of the user to delete")
):
    """
    Mark a user as deleted by updating the is_deleted column to "Y".
    """
    query = """
        UPDATE Members
        SET is_deleted = "Y"
        WHERE username = %s AND is_deleted = "N"
    """
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (username,))
            connection.commit()

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="User not found."
                )

            return {"status": "success", "message": f"User '{username}' as been removed."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        connection.close()