from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from database import get_db_connection

# Initialize the router
user_details_route = APIRouter()

# Define the UserResponse model
class UserResponse(BaseModel):
    member_id: int
    full_name: str
    membership_type: str
    points: int
    picture_url: str
    phone_number: str
    email_id: str
    address: str

@user_details_route.get("/user-details/", response_model=UserResponse)
async def get_user_details(
    email: str = Query(None), 
    username: str = Query(None)
):
    """
    Fetch user details based on email or username.
    """
    # Ensure at least one parameter is provided
    if not email and not username:
        raise HTTPException(
            status_code=400, 
            detail="Provide at least 'email' or 'username' to fetch details."
        )

    # Establish database connection
    connection = get_db_connection()

    # Define the query
    query = """
        SELECT 
            member_id, 
            CONCAT(first_name, ' ', last_name) AS full_name, 
            membership_type, 
            points, 
            picture_url, 
            phone_number, 
            email_id, 
            address
        FROM 
            Members
        WHERE 
            (email_id = %s OR username = %s) 
            AND is_deleted = "N"
        LIMIT 1;
    """
    params = (email, username)

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchone()

        # Handle user not found
        if not result:
            raise HTTPException(status_code=404, detail="User not found.")

        # Return formatted user details
        return {
            "member_id": result["member_id"],
            "full_name": result["full_name"],
            "membership_type": result["membership_type"],
            "points": result["points"],
            "picture_url": result["picture_url"],
            "phone_number": result["phone_number"],
            "email_id": result["email_id"],
            "address": result["address"],
        }

    except Exception as e:
        # Handle database query errors
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        # Ensure resources are closed properly
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals():
            connection.close()