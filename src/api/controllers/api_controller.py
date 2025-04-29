def error_function():
    raise RuntimeError("Unrecognized controller invoked")


def get_controller_details(
    api_name: str,
    body: dict,
    query_params: dict,
    method: str,
    ip_address: str,
    origin: str
):
    execute = error_function
    params = []
    dont_nest_response = False
    timeout_in_secs = None
    custom_headers = {}

    # Update details of your new API here

    if api_name == "hello":
        from src.functions.health.hello import say_hello
        execute = say_hello
        params = []
        timeout_in_secs = 10  # 10 seconds timeout

    elif api_name == "health":
        from src.functions.health.check import check_health
        execute = check_health
        params = []
        timeout_in_secs = 5  # 5 seconds timeout

    # Add more API routes here
    
    return {
        "execute": execute,
        "params": params,
        "dontNestResponse": dont_nest_response,
        "timeoutInSecs": timeout_in_secs,
        "customHeaders": custom_headers
    }
