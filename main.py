from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.validate_user import validate_user_route
from routes.create_member import create_member_route
from routes.get_points import get_points_route
from routes.get_membership import get_membership_route
from routes.update_membership import update_membership_route
from routes.delete_user import delete_user_route
from routes.update_user import update_user_route
from routes.add_points import update_points_route
from routes.user_detail import user_details_route
from routes.webhooks_FH import webhook_route
from starlette.middleware.sessions import SessionMiddleware 

# Initialize FastAPI app
app = FastAPI()

# Load the secret key
SECRET_KEY = "3003d57aaae374611f2cd2897ec6b92345d195f7cce32a452ddcf59dfa5565fd"

# Add SessionMiddleware with customized cookie name
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="kokomo_session"  
)

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
app.include_router(create_member_route, prefix="/create-member", tags=["Create Member"])
app.include_router(get_points_route, prefix="/get", tags=["Points"])
app.include_router(update_points_route, prefix="/update", tags=["Update Points"])
app.include_router(get_membership_route, prefix="/get", tags=["Membership"])
app.include_router(update_membership_route, prefix="/update", tags=["Update Membership"])
app.include_router(update_user_route, prefix="/update", tags=["Update User"])
app.include_router(delete_user_route, prefix="/update", tags=["Delete User"])
app.include_router(user_details_route, prefix="/get", tags=["User detail"])
app.include_router(webhook_route, prefix="/webhook", tags=["Webhook"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():                                                                           
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Service is running normally"
    }
