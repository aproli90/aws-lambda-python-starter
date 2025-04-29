import json
import os
import sys

# Try absolute imports first (for local testing)
try:
    import src.event.event_manager as event_manager
    from src.functions.logger import get_lambda_logger
# If that fails, try relative imports (for Docker/SAM)
except ImportError:
    try:
        import event_manager
        from functions.logger import get_lambda_logger
    except ImportError:
        # Last resort, try adjusting the path
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import event.event_manager as event_manager
        from functions.logger import get_lambda_logger

def lambda_handler(event, context):
    """
    Event Lambda function handler - Entry point for scheduled events
    
    Parameters:
    -----------
    event : dict
        Event data
    context : object
        Lambda Context runtime methods and attributes
        
    Returns:
    --------
    dict
        Response containing execution status
    """
    # Initialize a basic logger with Lambda context
    logger = get_lambda_logger(context)
    
    logger.info('Event triggered')
    logger.info(f'Event data: {json.dumps(event)}')
    
    # Delegate all routing to the Event manager
    return event_manager.lambda_handler(event, context, logger)
