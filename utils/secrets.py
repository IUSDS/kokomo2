import boto3
import json
from botocore.exceptions import ClientError

# Define global variables
SECRET_KEY = None
SMTP_PASS = None
DB_PASSWORD = None
JWT_SECRET = None
SESSION_COOKIES = None
SMTP_USER = None
Access_Point_ALIAS = None

def load_secrets(secret_name="my-fastapi-secret-key", region_name="ap-southeast-2"):
    """Fetches secrets from AWS Secrets Manager and assigns them to global variables."""
    global SECRET_KEY, SMTP_PASS, DB_PASSWORD, JWT_SECRET, SESSION_COOKIES, SMTP_USER, Access_Point_ALIAS

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_messages = {
            'ResourceNotFoundException': f"Secret {secret_name} not found.",
            'InvalidRequestException': f"Invalid request: {e}",
            'InvalidParameterException': f"Invalid parameters: {e}",
            'DecryptionFailure': "Secrets Manager couldn't decrypt the data.",
            'InternalServiceError': "An AWS internal service error occurred."
        }
        raise Exception(error_messages.get(error_code, str(e)))

    # Parse secrets
    secret_data = response.get('SecretString') or response.get('SecretBinary')
    secrets_dict = json.loads(secret_data) if isinstance(secret_data, str) else secret_data

    # Assign to global variables
    SECRET_KEY = secrets_dict.get("SECRET_KEY", "default_secret_key")
    SMTP_PASS = secrets_dict.get("SMTP_PASS", "default_smtp_pass")
    DB_PASSWORD = secrets_dict.get("DB_PASSWORD", "default_db_password")
    JWT_SECRET = secrets_dict.get("JWT_SECRET", "default_jwt_secret")
    SESSION_COOKIES = secrets_dict.get("SESSION_COOKIES", "default_session_cookies")
    SMTP_USER = secrets_dict.get("SMTP_USER", "default_smtp_user")
    Access_Point_ALIAS = secrets_dict.get("Access_Point_ALIAS", "default_access_point_ALIAS")

# Load secrets when imported
load_secrets()
