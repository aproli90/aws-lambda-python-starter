import json
import traceback
from src.utils.logger import update_master_logger, init_master_logger
import src.utils.secrets_manager as SM

import src.api.controllers.api_controller as CONTRL

# Configure logging
logger = init_master_logger()
log_level = SM.get_secret_value('LOG_LEVEL', 'DEBUG')
logger.setLevel(log_level)

# Load secrets at initialization time
app_secrets = SM.init_secrets()
logger.info("Secrets loaded successfully")

def __get_api_name(event):
    """Extract API name from the resource path"""
    resource = event.get("resource", "")
    if resource.startswith("/"):
        return resource[1:]
    return resource

def __get_ip_address(event):
    """Extract IP address from headers"""
    return event.get("headers", {}).get("X-Forwarded-For", "unknown")

def __get_origin(event):
    """Extract origin from headers"""
    return event.get("headers", {}).get("Origin", "unknown")

def __safe_parse_json(text):
    """Safely parse JSON or return empty dict"""
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        return {}

def lambda_handler(event, context, input_logger=None):
    """
    Main entry point for the API Lambda function.
    Routes requests to the appropriate controller based on the API name.
    
    Parameters:
    -----------
    event : dict
        API Gateway Lambda Proxy Input Format
    context : object
        Lambda Context runtime methods and attributes
    input_logger : logging.Logger, optional
        Logger instance from the calling function
        
    Returns:
    --------
    dict
        API Gateway Lambda Proxy Output Format
    """
    global logger
    request_id = context.aws_request_id
    
    # Extract API name for classifier
    api_name = __get_api_name(event)
    
    # Update logger with API-specific classifier if provided
    if input_logger:
        logger = update_master_logger(f'API:{api_name}', request_id)
    
    logger.info(f"Request ID: {request_id}")
    logger.info(f"API Name: {api_name}")
    
    start_time = __get_current_time_ms()
    
    ip_address = __get_ip_address(event)
    origin = __get_origin(event)
    
    execute_function_name = "UNKNOWN_FUNC"
    
    body = None
    query_params = None
    timeout_in_secs = None
    
    try:
        method = event.get("httpMethod", "GET")
        default_response = {
            "statusCode": 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Max-Age': 86400,
            }
        }
        
        if method == "OPTIONS":
            logger.info(f"OPTIONS:{api_name} | SKIPPING")
            return default_response
        
        query_params = event.get("queryStringParameters") or {}
        body = __safe_parse_json(event.get("body") or "{}")
        logger.info(f"Request body: {body}")
        
        controller_details = CONTRL.get_controller_details(
            api_name, body, query_params, method, ip_address, origin
        )
        
        execute_function = controller_details["execute"]
        execute_function_name = execute_function.__name__
        execute_params = controller_details["params"] or []
        dont_nest_response = controller_details["dontNestResponse"]
        timeout_in_secs = controller_details["timeoutInSecs"]
        custom_headers = controller_details["customHeaders"]
        
        response = execute_function(*execute_params)
        logger.info(f"Execution Successful: {execute_function_name}()")
        logger.info(f"apiResponse: {response}")
        
        response_body = response if dont_nest_response else {
            "message": f"API:{api_name} successfully processed",
            "response": response
        }
        
        default_response["headers"] = {
            **default_response["headers"],
            **custom_headers
        }
        
        skip_json_dump = isinstance(response_body, str)
        return {
            "body": response_body if skip_json_dump else json.dumps(response_body),
            **default_response
        }
    except Exception as ex:
        error_msg = f"API:{api_name}:{execute_function_name}()\n::{ex}"
        logger.error(error_msg)
        stacktrace = traceback.format_exc()
        logger.error(stacktrace)
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(ex),
                "message": f"Error processing API:{api_name}"
            }),
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Max-Age': 86400,
            }
        }
    finally:
        total_exec_duration = __get_current_time_ms() - start_time
        logger.info(f"TotalExecDuration: {total_exec_duration} ms")
        
        if timeout_in_secs and (total_exec_duration > (timeout_in_secs * 1000)):
            total_exec_duration_secs = round(total_exec_duration / 1000)
            logger.warning(f"Timeout recorded: {total_exec_duration_secs}s > {timeout_in_secs}s")

def __get_current_time_ms():
    """Get current time in milliseconds"""
    import time
    return int(time.time() * 1000)
