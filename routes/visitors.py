from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel, EmailStr
from database import get_db_connection
import boto3

visitors_route = APIRouter()

# Request schemas
class EmailRequest(BaseModel):
    email: EmailStr
    visitor_name: str = None
    phone_no: str = None

class VisitorRequest(BaseModel):
    email: EmailStr
    visitor_name: str = None
    phone_no: str = None
    req_help: str = None
    ques: str = None

# API to add email only
@visitors_route.post("/add-email")
async def add_email(request: EmailRequest):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            insert_query = """
                INSERT INTO Visitors (email, visitor_name, phone_no) 
                VALUES (%s, %s, %s) 
                ON DUPLICATE KEY UPDATE 
                    visitor_name = VALUES(visitor_name),
                    phone_no = VALUES(phone_no);
                """
            cursor.execute(insert_query, (request.email, request.visitor_name, request.phone_no,))
            connection.commit()
        return {"message": "info added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

# API to add full visitor details
@visitors_route.post("/add-visitor")
async def add_visitor(request: VisitorRequest):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            insert_query = """
            INSERT INTO Visitors (email, visitor_name, phone_no, req_help, ques)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                visitor_name = VALUES(visitor_name),
                phone_no = VALUES(phone_no),
                req_help = VALUES(req_help),
                ques = VALUES(ques);
            """
            cursor.execute(insert_query, (request.email, request.visitor_name, request.phone_no, request.req_help, request.ques))
            connection.commit()
        return {"message": "Visitor details added/updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()
    
# API to generate pre-signed url for pdf
@visitors_route.get("/get-pdf")
async def get_pdf():
    s3_client = boto3.client('s3', region_name='ap-southeast-2')
    bucket_name = "image-bucket-kokomo-yacht-club"
    object_key = "pdfs/KokomoYachtClubBrochure8-24_compressed.pdf"

    try:
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key
            },
            ExpiresIn=3600
        )
        return {"url": presigned_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
