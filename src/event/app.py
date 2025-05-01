import json
import src.event.event_manager as event_manager
from src.utils.logger import get_lambda_logger

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
