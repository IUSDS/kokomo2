from fastapi import APIRouter, HTTPException, Form
from pydantic import EmailStr
from database import get_db_connection

create_member_route = APIRouter()

# Endpoint to validate username and email
@create_member_route.get("/validate-member/")
async def validate_member(username: str = None, email_id: str = None):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if username exists
        if username:
            cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE username = %s", (username,))
            if cursor.fetchone()["count"] > 0:
                return {"status": "error", "message": "Username already exists, try something else"}

        # Check if email exists
        if email_id:
            cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE email_id = %s", (email_id,))
            if cursor.fetchone()["count"] > 0:
                return {"status": "error", "message": "Account already exists for this email, try logging in"}

        return {"status": "success", "message": "Username and email are available"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


# Endpoint to add a new member
@create_member_route.post("/add-member/")
async def add_member(
    username: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(...),
    address: str = Form(...),
    email_id: EmailStr = Form(...),
    membership_type: str = Form(...),
    points: int = Form(...),
    picture_url: str = Form(...),
    is_deleted: bool = Form(default="N"),
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the username already exists
        cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE username = %s", (username,))
        username_exists = cursor.fetchone()["count"]

        if username_exists > 0:
            return {"status": "error", "message": "Username already exists, try something else"}

        # Check if the email_id already exists
        cursor.execute("SELECT COUNT(*) AS count FROM Members WHERE email_id = %s", (email_id,))
        email_exists = cursor.fetchone()["count"]

        if email_exists > 0:
            return {"status": "error", "message": "Account already exists for this email, try logging in"}

        # If both username and email_id are unique, insert the new member
        query = """
        INSERT INTO Members (username, pass, first_name, last_name, phone_number, address,
                             email_id, membership_type, points, picture_url, is_deleted)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "N")
        """
        cursor.execute(
            query,
            (
                username,
                password,
                first_name,
                last_name,
                phone_number,
                address,
                email_id,
                membership_type,
                points,
                picture_url,
                is_deleted,
            ),
        )
        connection.commit()

        return {"status": "success", "message": "Member added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
