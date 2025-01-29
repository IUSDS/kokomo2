# https://aws.amazon.com/developer/language/python/

import boto3
from botocore.exceptions import ClientError

def get_secret():

    secret_name = "my-fastapi-secret-key"
    region_name = "ap-southeast-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # Handle specific errors gracefully
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise Exception(f"The requested secret {secret_name} was not found.")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise Exception(f"The request was invalid: {e}")
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise Exception(f"The request had invalid params: {e}")
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            raise Exception("Secrets Manager can't decrypt the protected secret text.")
        elif e.response['Error']['Code'] == 'InternalServiceError':
            raise Exception("An error occurred on the AWS side.")
        else:
            raise e
    # Parse and return the secret value
    if 'SecretString' in get_secret_value_response:
        return get_secret_value_response['SecretString']
    else:
        # Handle cases where the secret is stored as binary
        return get_secret_value_response['SecretBinary']
    