from fastapi import APIRouter, HTTPException, Query, Form
from utils.database import get_db_connection
from pydantic import BaseModel

# Initialize router
update_membership_route = APIRouter()

# Allowed membership types
ALLOWED_MEMBERSHIP_TYPES = ["Silver", "Gold", "Platinum", "Premium"]

class UpdateMembershipRequest(BaseModel):
    username: str
    membership_type: str

@update_membership_route.put("/membership/")
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