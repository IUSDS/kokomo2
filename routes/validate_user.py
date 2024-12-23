from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db_connection
from models import User

validate_user_route = APIRouter()

@validate_user_route.post("/")
async def validate_user(user: User):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT pass, user_type FROM Members WHERE username = %s AND pass = %s"
            cursor.execute(query, (user.USER, user.password))
            result = cursor.fetchone()

            if not result:
                return {"status": "invalid username or password"}

            stored_password = result["pass"].strip()
            user_type = result["user_type"]

            if stored_password != user.password.strip():
                return {"status": "invalid password"}

            if user_type == "User":
                return {"status": "success", "user_type": "user"}
            elif user_type == "Admin":
                return {"status": "success", "user_type": "admin"}
            else:
                return {"status": "error", "message": "Invalid user_type in database"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        connection.close()
