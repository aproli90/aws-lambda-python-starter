import src.api.api_manager as api_manager
from src.utils.logger import get_lambda_logger

def lambda_handler(event, context):
    """
    API Lambda function handler - Entry point for API Gateway requests
    
    Parameters:
    -----------
    event : dict
        API Gateway Lambda Proxy Input Format
    context : object
        Lambda Context runtime methods and attributes
        
    Returns:
    --------
    dict
        API Gateway Lambda Proxy Output Format
    """
    # Initialize a basic logger with Lambda context
    logger = get_lambda_logger(context)
    
    logger.info('API request received')
    
    # Delegate all routing to the API manager
    return api_manager.lambda_handler(event, context, logger)
