import logging
import uuid


def init_logger():
    """
    Initialize a basic logger with a unique request ID.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger("WFGClient")
    if not logger.hasHandlers():
        request_id = str(uuid.uuid4())
        format_str = f"({request_id}) [%(levelname)s] %(message)s"
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger


class LogHandler(logging.StreamHandler):
    """
    Custom log handler that splits multi-line messages into separate log entries.
    """
    def __init__(self):
        super(LogHandler, self).__init__()

    def emit(self, record):
        if not isinstance(record.msg, str):
            record.msg = str(record.msg)
        messages = record.msg.split('\n')
        for message in messages:
            record.msg = message
            super(LogHandler, self).emit(record)


def __update_or_init_master_logger(
    classifier: str = None,
    request_id: str = None
):
    """
    Internal function to update or initialize the master logger.
    
    Args:
        classifier (str, optional): Service classifier. Defaults to None.
        request_id (str, optional): Unique request ID. Defaults to None.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger('WFGClients')
    logger.setLevel(logging.DEBUG)

    if request_id:
        handler = LogHandler()
        logger.handlers.clear()
        formatter = logging.Formatter(
            f"<<{classifier or 'UNKNOWN_SERVICE'}>> ({request_id}) [%(levelname)s] %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger


def init_master_logger():
    """
    Initialize the master logger with default configuration.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger('WFGClients')
    logger.setLevel(logging.DEBUG)
    
    # Add a default handler if none exists
    if not logger.handlers:
        handler = LogHandler()
        logger.addHandler(handler)
    
    return logger


def update_master_logger(
    classifier: str,
    request_id: str
):
    """
    Update the master logger with a specific classifier and request ID.
    
    Args:
        classifier (str): Service classifier (e.g., 'API', 'EVENT')
        request_id (str): Unique request ID
        
    Returns:
        logging.Logger: Updated logger instance
    """
    return __update_or_init_master_logger(classifier, request_id)


def get_lambda_logger(context=None, classifier: str = None):
    """
    Get a logger configured for AWS Lambda functions.
    
    Args:
        context: AWS Lambda context object
        classifier (str, optional): Service classifier. Defaults to None.
        
    Returns:
        logging.Logger: Configured logger instance for Lambda
    """
    request_id = context.aws_request_id if context else str(uuid.uuid4())
    return update_master_logger(classifier or 'LAMBDA', request_id)
