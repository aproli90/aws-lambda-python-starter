"""
Health check functionality for the WFG Client project.
"""
import logging
import src.utils.secrets_manager as SM

# Get logger instance
logger = logging.getLogger('WFGClients')

def check_health(event=None, context=None):
    """
    Simple health check endpoint that returns the status of the API
    and the Supabase connection URL (without sensitive credentials)
    
    Args:
        event: AWS Lambda event object
        context: AWS Lambda context object
        
    Returns:
        dict: Health status information
    """
    supabase_url = SM.get_secret_value('SUPABASE_URL', 'Not configured')
    logger.info(f"Health check requested, Supabase URL: {supabase_url}")
    
    # Log execution success
    logger.info("Execution Successful: check_health()")
    logger.info(f"TotalExecDuration: {0} ms")
    
    return {
        "status": "healthy",
        "supabase_connection": supabase_url,
        "version": "1.0.0"
    }
