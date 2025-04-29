import json
import traceback
from src.utils.logger import update_master_logger, init_master_logger
import src.utils.secrets_manager as SM

import src.event.controllers.event_controller as CONTRL

# Configure logging
logger = init_master_logger()
log_level = SM.get_secret_value('LOG_LEVEL', 'DEBUG')
logger.setLevel(log_level)

# Load secrets at initialization time
app_secrets = SM.init_secrets()
logger.info("Secrets loaded successfully")

def __get_event_name(event):
    """Extract event name from the event object"""
    # Default to DailyProcessing if no name is provided
    return event.get("name", "DailyProcessing")

def __get_current_time_ms():
    """Get current time in milliseconds"""
    import time
    return int(time.time() * 1000)

def lambda_handler(event, context, input_logger=None):
    """
    Main entry point for the Event Lambda function.
    Routes events to the appropriate controller based on the event name.
    
    Parameters:
    -----------
    event : dict
        Event data
    context : object
        Lambda Context runtime methods and attributes
    input_logger : logging.Logger, optional
        Logger instance from the calling function
        
    Returns:
    --------
    dict
        Response containing execution status
    """
    global logger
    request_id = context.aws_request_id
    
    # Extract event name for classifier
    event_name = __get_event_name(event)
    
    # Update logger with event-specific classifier if provided
    if input_logger:
        logger = update_master_logger(f'EVENT:{event_name}', request_id)
    
    logger.info(f"Request ID: {request_id}")
    logger.info(f"Event Name: {event_name}")
    
    start_time = __get_current_time_ms()
    
    execute_function_name = "UNKNOWN_FUNC"
    
    try:
        # Get the controller function for this event
        execute_function = CONTRL.get_controller_function(event_name)
        
        # Get the function name for logging
        from functools import partial
        if isinstance(execute_function, partial):
            execute_function_name = execute_function.func.__name__
        else:
            execute_function_name = execute_function.__name__
        
        # Execute the controller function
        response = execute_function()
        logger.info(f"Execution Successful: {execute_function_name}()")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"EVENT:{event_name} successfully processed",
                "response": response
            })
        }
    except Exception as ex:
        error_msg = f"EVENT:{event_name}:{execute_function_name}()\n::{ex}"
        logger.error(error_msg)
        stacktrace = traceback.format_exc()
        logger.error(stacktrace)
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(ex),
                "message": f"Error processing EVENT:{event_name}"
            })
        }
    finally:
        total_exec_duration = __get_current_time_ms() - start_time
        logger.info(f"TotalExecDuration: {total_exec_duration} ms")
