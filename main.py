from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.validate_user import validate_user_route
from routes.create_member import create_member_route  # Updated with session and S3 integration
from routes.get_points import get_points_route
from routes.get_membership import get_membership_route
from routes.update_membership import update_membership_route
from routes.delete_user import delete_user_route
from routes.update_user import update_user_route
from routes.add_points import update_points_route
from starlette_session import SessionMiddleware
import boto3

# Initialize FastAPI app
app = FastAPI()

# Load the secret key
SECRET_KEY = "# Load the secret key"

#SECRET_KEY FOR SESSION
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, cookie_name="kokomo_session",  # Session cookie name
                  )

# Add CORS and Session middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust origins as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(validate_user_route, prefix="/validate-user", tags=["Validate User"])
app.include_router(create_member_route, prefix="/create-member", tags=["Create Member"])  # Updated
app.include_router(get_points_route, prefix="/get", tags=["Points"])
app.include_router(get_membership_route, prefix="/get", tags=["Membership"])
app.include_router(update_membership_route, prefix="/update", tags=["Update Membership"])
app.include_router(delete_user_route, prefix="/update", tags=["Delete User"])
app.include_router(update_user_route, prefix="/update", tags=["Update User"])
app.include_router(update_points_route, prefix="/update", tags=["Update Points"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Service is running normally"
    }
