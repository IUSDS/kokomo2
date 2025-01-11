from fastapi import APIRouter, HTTPException, Request, Response, UploadFile, Depends
from pydantic import BaseModel
import boto3
import pymysql
from database import get_db_connection

# AWS S3 Configuration
S3_BUCKET_NAME = "image-bucket-kokomo-yacht-club"
S3_REGION = "ap-southeast-2"
AGREEMENT_PATH = "agreement_filled/"
ACH_PATH = "ach_filled/"

s3_client = boto3.client("s3")

# Define router
user_agreement_route = APIRouter()

@user_agreement_route.post("/upload-documents/")
async def upload_documents(
    request: Request,
    agreement_filled: UploadFile = None,
    ach_filled: UploadFile = None
):
    """
    Uploads agreement_filled and ach_filled to S3 and updates the database columns accordingly.
    """
    kokomo_session = request.cookies.get("kokomo_session")
    if not kokomo_session:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")

    connection = get_db_connection()
    agreement_status = "N"
    ach_status = "N"

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Verify user exists
            query = """
                SELECT member_id
                FROM Members
                WHERE LOWER(username) = LOWER(%s) AND is_deleted = "N"
                LIMIT 1
            """
            cursor.execute(query, (kokomo_session,))
            result = cursor.fetchone()

            if not result:
               raise HTTPException(status_code=401, detail="Session expired or invalid.")

            member_id = result["member_id"]
            print(member_id)

            # Upload agreement_filled to S3
            if agreement_filled:
                agreement_k = AGREEMENT_PATH + agreement_filled.filename
                agreement_key = str(agreement_k)
                print(agreement_key)
                print(type(agreement_key))
                try:
                    s3_client.upload_fileobj(
                        agreement_filled.file,
                        S3_BUCKET_NAME,
                        agreement_key,
                        ExtraArgs={"ContentType": agreement_filled.content_type}
                    )
                    agreement_status = "Y"
                    print("agreement_status")
                except Exception as e:
                    print(f"Error uploading agreement_filled: {str(e)}")
            else:
                print("FU")
            # Upload ach_filled to S3
            if ach_filled:
                ach_key = ACH_PATH + ach_filled.filename
                try:
                    s3_client.upload_fileobj(
                        ach_filled.file,
                        S3_BUCKET_NAME,
                        ach_key,
                        ExtraArgs={"ContentType": ach_filled.content_type}
                    )
                    ach_status = "Y"
                    print(ach_status)
                except Exception as e:
                    print(f"Error uploading ach_filled: {str(e)}")
            else:
                print("FU")
            # Update database
            update_query = """
                UPDATE Members
                SET agreement_filled = %s, ach_filled = %s
                WHERE member_id = %s
            """
            cursor.execute(update_query, (agreement_status, ach_status, member_id))
            connection.commit()

            return {
                "status": "SUCCESS",
                "message": "Documents uploaded successfully.",
                "agreement_filled_status": agreement_status,
                "ach_filled_status": ach_status
            }

    except pymysql.MySQLError as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    finally:
        connection.close()
        
# Health check endpoint
@user_agreement_route.get("/re", tags=["re"])
async def re():                                                                           
    """Health check endpoint"""
    return {
        "new": "wow",
    }