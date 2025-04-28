from fastapi import APIRouter, HTTPException, Query, Form
from utils.database import get_db_connection
from pydantic import BaseModel

# Initialize router
membership_route = APIRouter()

# Allowed membership types
ALLOWED_MEMBERSHIP_TYPES = ["Silver", "Gold", "Platinum", "Premium"]

class UpdateMembershipRequest(BaseModel):
    username: str
    membership_type: str

@membership_route.put("/update-membership/")
async def update_membership_type(
    username: str = Form(..., description="The username to update membership type for"),
    membership_type: str = Form(..., description="The new membership type")
):
    """
    Update membership type for the given username.
    """
    if membership_type not in ALLOWED_MEMBERSHIP_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid membership type. Allowed values are {ALLOWED_MEMBERSHIP_TYPES}"
        )

    query = """
        UPDATE Members
        SET membership_type = %s
        WHERE username = %s AND is_deleted = "N"
    """
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (membership_type, username))
            connection.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found or already deleted.")

            return {"status": "success", "message": f"Membership type updated to {membership_type} for {username}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        connection.close()


@membership_route.get("/get-membership/")
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