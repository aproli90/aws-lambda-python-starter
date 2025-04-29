import json
import os
import boto3
import logging
from botocore.exceptions import ClientError

# Initialize logger
logger = logging.getLogger(__name__)

# Global cache for secrets
_secrets_cache = {}

# Hardcoded configuration
DEFAULT_REGION = "ap-south-1"
SECRETS_NAME = "wfg-clients-secrets"

def get_secret(secret_name=SECRETS_NAME, region_name=DEFAULT_REGION, force_refresh=False):
    """
    Retrieve a secret from AWS Secrets Manager.
    
    Parameters:
    -----------
    secret_name : str, optional
        Name of the secret to retrieve, defaults to SECRETS_NAME
    region_name : str, optional
        AWS region where the secret is stored, defaults to DEFAULT_REGION
    force_refresh : bool, optional
        If True, will bypass cache and fetch fresh secret from AWS
        
    Returns:
    --------
    dict
        The secret value as a dictionary
    """
    # Check if secret is in cache and we're not forcing a refresh
    if not force_refresh and secret_name in _secrets_cache:
        logger.debug(f"Using cached secret for {secret_name}")
        return _secrets_cache[secret_name]
    
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        logger.info(f"Fetching secret {secret_name} from AWS Secrets Manager")
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise Exception(f"Decryption failure when accessing secret {secret_name}")
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise Exception(f"Internal service error when accessing secret {secret_name}")
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise Exception(f"Invalid parameter when accessing secret {secret_name}")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise Exception(f"Invalid request when accessing secret {secret_name}")
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise Exception(f"Secret {secret_name} not found")
        else:
            raise Exception(f"Unknown error when accessing secret {secret_name}: {str(e)}")
    else:
        # Depending on whether the secret is a string or binary, one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            # Parse JSON string into dictionary
            try:
                secret_dict = json.loads(secret)
                _secrets_cache[secret_name] = secret_dict
                return secret_dict
            except json.JSONDecodeError:
                # If not valid JSON, return as string in a dict
                _secrets_cache[secret_name] = {"value": secret}
                return {"value": secret}
        else:
            # Binary secrets are not supported in this implementation
            raise Exception(f"Binary secrets are not supported for {secret_name}")

def get_secret_value(key=None, default=None, secret_name=SECRETS_NAME):
    """
    Get a specific value from a secret.
    
    Parameters:
    -----------
    key : str, optional
        Key within the secret JSON to retrieve. If None, returns the entire secret.
    default : any, optional
        Default value to return if the key is not found
    secret_name : str, optional
        Name of the secret, defaults to SECRETS_NAME
        
    Returns:
    --------
    any
        The value of the specified key in the secret, or the default if not found
    """
    try:
        secret = get_secret(secret_name)
        if key is None:
            return secret
        return secret.get(key, default)
    except Exception as e:
        logger.error(f"Error retrieving value from secret {secret_name}: {str(e)}")
        return default

def is_local_environment():
    """Check if code is running in a local development environment"""
    return os.environ.get('AWS_EXECUTION_ENV') is None

def init_secrets():
    """
    Initialize secrets at application startup.
    In local environment, will look for local secrets file.
    
    Returns:
    --------
    dict
        Dictionary with all loaded secrets
    """
    if is_local_environment():
        logger.info("Running in local environment, checking for local secrets file")
        try:
            # Look for local secrets file for development
            local_secrets_path = os.path.join(os.path.dirname(__file__), '..', '..', 'local_secrets.json')
            if os.path.exists(local_secrets_path):
                with open(local_secrets_path, 'r') as f:
                    local_secrets = json.load(f)
                    for secret_name, secret_value in local_secrets.items():
                        _secrets_cache[secret_name] = secret_value
                    logger.info(f"Loaded secrets from local file: {', '.join(local_secrets.keys())}")
                    return _secrets_cache.get(SECRETS_NAME, {})
        except Exception as e:
            logger.warning(f"Failed to load local secrets: {str(e)}")
    
    # Load from AWS Secrets Manager
    return get_secret(SECRETS_NAME, DEFAULT_REGION)
