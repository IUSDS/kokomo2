from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.validate_user import validate_user_route
from routes.user_details import user_details_route
from routes.create_member import create_member_route
from routes.get_points import get_points_route
from routes.get_membership import get_membership_route
from routes.update_membership import update_membership_route
from routes.delete_user import delete_user_route
from routes.update_user import update_user_route
from routes.add_points import add_points_route

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(validate_user_route, prefix="/validate-user", tags=["Validate User"])
app.include_router(user_details_route, prefix="/user-details", tags=["User Details"])
app.include_router(create_member_route, prefix="/create-member", tags=["Create Member"])
app.include_router(get_points_route, prefix="/get", tags=["Points"])
app.include_router(get_membership_route, prefix="/get", tags=["Membership"])
app.include_router(update_membership_route, prefix="/update", tags=["Update Membership"])
app.include_router(delete_user_route, prefix="/update", tags=["Delete User"])
app.include_router(update_user_route, prefix="/update", tags=["Update User"])
app.include_router(add_points_route, prefix="/update", tags=["Update Points"])

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Service is running normally"
    }
