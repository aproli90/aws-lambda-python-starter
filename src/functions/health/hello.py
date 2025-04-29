"""
Hello world functionality for the WFG Client project.
"""

import logging
import src.utils.secrets_manager as SM

# Get logger instance
logger = logging.getLogger('WFGClients')

def say_hello(event=None, context=None):
    """
    Simple hello world endpoint that returns a greeting message
    and the Supabase connection URL (without sensitive credentials)
    
    Args:
        event: AWS Lambda event object
        context: AWS Lambda context object
        
    Returns:
        dict: Greeting message and connection information
    """
    supabase_url = SM.get_secret_value('SUPABASE_URL', 'Not configured')
    logger.info(f"Hello request received, Supabase URL: {supabase_url}")
    
    # Log execution success
    logger.info("Execution Successful: say_hello()")
    logger.info(f"TotalExecDuration: {0} ms")
    
    return {
        "message": "Hello from Lambda!",
        "supabase_url": supabase_url
    }
