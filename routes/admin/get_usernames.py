from fastapi import APIRouter, HTTPException
from utils.database import get_db_connection

# Initialize router
get_usernames_route = APIRouter()

@get_usernames_route.get("/usernames/")
async def get_usernames():
    """
    Retrieve all usernames from the Members table where is_deleted is 'N'.
    """
    query = """
        SELECT username
        FROM Members
        WHERE is_deleted = 'N'
    """
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

            if not result:
                raise HTTPException(status_code=404, detail="No active users found.")

            # Extract usernames from the result
            usernames = [user["username"] for user in result]
            # print(usernames)
            return {"usernames": usernames}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        connection.close()
