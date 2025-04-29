import os
import sys

# Try absolute imports first (for local testing)
try:
    import src.api.api_manager as api_manager
    from src.functions.logger import get_lambda_logger
# If that fails, try relative imports (for Docker/SAM)
except ImportError:
    try:
        import api_manager
        from functions.logger import get_lambda_logger
    except ImportError:
        # Last resort, try adjusting the path
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import api.api_manager as api_manager
        from functions.logger import get_lambda_logger

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
