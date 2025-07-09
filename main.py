from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse, Response
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
import base64
from routes.admin.export_data import export_data_route
from routes.validate_user import validate_user_route
from routes.admin.create_member import create_member_route
from routes.admin.points import points_route
from routes.admin.membership import membership_route
from routes.admin.delete_user import delete_user_route
from routes.admin.update_user import update_user_route
from routes.user_detail import user_details_route
from routes.webhooks_FH import webhook_route
from routes.visitors import visitors_route
from routes.forgotpass import forgot_password_route
from routes.admin.get_usernames import get_usernames_route
from utils.secrets_util import SECRET_KEY, SESSION_COOKIES, JWT_SECRET
from starlette.middleware.sessions import SessionMiddleware
from routes.admin.bookings_fh import booking_route
from routes.websocket import websocket_router
#from logger_config import app_logger

# Initialize FastAPI app
app = FastAPI()

# Define security scheme (Basic Auth)
security = HTTPBasic()

# Add SessionMiddleware with customized cookie name
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie=SESSION_COOKIES
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://kokomoyachtclub.vip"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The Docusign URL you provided
DOCUSIGN_URL = "https://us.services.docusign.net/webforms-ux/v1.0/forms/690282cb4272b0df7605b26ae28788f2"

@app.get("/apply-for-membership")
async def apply_for_membership_redirect():
    """
    Redirects requests for /apply-for-membership to the Docusign URL.
    """
    return RedirectResponse(url=DOCUSIGN_URL)


# Function to enforce authentication for Swagger UI & OpenAPI
async def enforce_docs_auth(request: Request):
    if request.url.path in ["/docs", "/openapi.json"]:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return Response(
                headers={"WWW-Authenticate": "Basic"},
                status_code=401,
                content="Unauthorized: Missing authentication"
            )

        # Decode the Base64-encoded credentials
        encoded_credentials = auth_header.split("Basic ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)

        # Validate credentials
        correct_username = "Admin"
        correct_password = JWT_SECRET  # Ensure JWT_SECRET is set correctly

        if username != correct_username or password != correct_password:
            return Response(
                headers={"WWW-Authenticate": "Basic"},
                status_code=401,
                content="Unauthorized: Incorrect credentials"
            )

# Add authentication middleware for Swagger UI & OpenAPI
@app.middleware("http")
async def docs_auth_middleware(request: Request, call_next):
    response = await enforce_docs_auth(request)
    if response:
        return response  # Return 401 if unauthorized

    return await call_next(request)

# Secure the Swagger UI
@app.get("/docs", include_in_schema=False)
async def get_documentation():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")

# Secure the OpenAPI schema (optional)
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(title="API", version="1.0.0", routes=app.routes)

# Include routers (without authentication)
app.include_router(validate_user_route, prefix="/validate-user", tags=["Validate User"])
app.include_router(create_member_route, prefix="/create-member", tags=["Create Member"])
app.include_router(user_details_route, prefix="/new-userdetail", tags=["New userdetail"])
app.include_router(points_route, prefix="/points", tags=["Points"])
app.include_router(membership_route, prefix="/get-membership", tags=["Membership"])
app.include_router(update_user_route, prefix="/update", tags=["Update User"])
app.include_router(delete_user_route, prefix="/update", tags=["Delete User"])
app.include_router(webhook_route, prefix="/webhook", tags=["Webhook"])
app.include_router(visitors_route, prefix="/visitors", tags=["Visitors"])
app.include_router(forgot_password_route, prefix="/forgot", tags=["Forgot"])
app.include_router(export_data_route, prefix="/export-data", tags=["Export Data"])
app.include_router(get_usernames_route, prefix="/usernames", tags=["Get Usernames"])
app.include_router(booking_route,prefix="/booking", tags=["Booking History"])
app.include_router(websocket_router, prefix="/web_socket")

# Public Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "message": "Service is running normally"}

if __name__ == "__main__":
    import uvicorn
    # Run the application with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)