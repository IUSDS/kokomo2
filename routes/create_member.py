from fastapi import APIRouter, HTTPException, Form, Query
from passlib.context import CryptContext
from pydantic import EmailStr
from database import get_db_connection

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize router
create_member_route = APIRouter()

# Function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@create_member_route.get("/validate-member/")
async def validate_member(
    username: str = Query(None),
    email_id: str = Query(None)
):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            if username:
                cursor.execute("SELECT COUNT(*) FROM Members WHERE username = %s", (username,))
                if cursor.fetchone()[0] > 0:
                    return {"status": "error", "message": "Username already exists, try something else"}

            if email_id:
                cursor.execute("SELECT COUNT(*) FROM Members WHERE email_id = %s", (email_id,))
                if cursor.fetchone()[0] > 0:
                    return {"status": "error", "message": "Account already exists for this email, try logging in"}

            return {"status": "success", "message": "Available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()

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
    is_deleted: bool = Form(default=False),
):
    try:
        # Hash the password before storing it
        hashed_password = hash_password(password)
        
        # Establish a database connection
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Check if the username already exists
            cursor.execute("SELECT COUNT(*) FROM Members WHERE username = %s", (username,))
            if cursor.fetchone()[0] > 0:
                return {"message": "Username already exists, try something else"}

            # Check if the email already exists
            cursor.execute("SELECT COUNT(*) FROM Members WHERE email_id = %s", (email_id,))
            if cursor.fetchone()[0] > 0:
                return {"message": "Account already exists for this email, try logging in"}

            # Insert the form data into the database
            query = """
            INSERT INTO Members (
                username, pass, first_name, last_name, phone_number, address,
                email_id, membership_type, points, picture_url, is_deleted
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    username,
                    hashed_password,
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
            return {"message": "Member added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        connection.close()