from fastapi import FastAPI, Depends, HTTPException
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
from routes.visitors import visitors_route
from routes.forgotpass import forgot_password_route

from utils.secrets import SECRET_KEY, SESSION_COOKIES, JWT_SECRET
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Initialize FastAPI app
app = FastAPI()

# Define security scheme (Basic Auth)
security = HTTPBasic()

# Add SessionMiddleware with customized cookie name
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie= SESSION_COOKIES
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Define your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A simple function to verify the credentials (this could be more complex in production)
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "Admin"
    correct_password = JWT_SECRET

    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    return credentials.username

# Apply the `verify_credentials` function to all routes
@app.on_event("startup")
async def on_startup():
    # Apply authentication to all routes globally
    app.include_router(
        validate_user_route, prefix="/validate-user", tags=["Validate User"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        create_member_route, prefix="/create-member", tags=["Create Member"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        user_details_route, prefix="/new-userdetail", tags=["New userdetail"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        get_points_route, prefix="/get", tags=["Points"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        update_points_route, prefix="/update", tags=["Update Points"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        get_membership_route, prefix="/get", tags=["Membership"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        update_membership_route, prefix="/update", tags=["Update Membership"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        update_user_route, prefix="/update", tags=["Update User"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        delete_user_route, prefix="/update", tags=["Delete User"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        user_details_route, prefix="/get", tags=["User detail"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        webhook_route, prefix="/webhook", tags=["Webhook"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        visitors_route, prefix="/vistors", tags=["Visitors"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        forgot_password_route, prefix="/forgot", tags=["Forgot"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        user_agreement_route, prefix="/user_agreements", tags=["User Agreements"], dependencies=[Depends(verify_credentials)]
    )
    app.include_router(
        adminEmail_route, prefix="/adminEmail", tags=["Admin Email"], dependencies=[Depends(verify_credentials)]
    )

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():                                                                           
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Service is running normally"
    }

if __name__ == "__main__":
    import uvicorn
    # Run the application with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
