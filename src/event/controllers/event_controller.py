# from functools import partial

def error_function():
    raise RuntimeError("Unrecognized controller invoked")


def get_controller_function(event_name: str):
    controller = error_function

    # Update details of your new event handlers here

    if event_name == "DailyProcessing":
        from src.functions.data_sync.daily_processing import process_daily_tasks
        controller = process_daily_tasks

    elif event_name == "DataSync":
        from src.functions.data_sync.sync import sync_data
        controller = sync_data
    
    # Add more event handlers here

    return controller
