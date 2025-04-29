#!/usr/bin/env python3
"""
Local testing script for Lambda functions
"""
import json
import os
import sys
import uuid
import argparse

# Set environment variables for local testing
os.environ['SUPABASE_URL'] = 'https://mpfxatlnmikcwvvxejzf.supabase.co'
os.environ['LOG_LEVEL'] = 'INFO'

# Add the project root to the Python path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # Go up one level from scripts directory
sys.path.insert(0, PROJECT_ROOT)

# Define event file paths
EVENT_FILES = {
    'api-hello': 'events/api-hello.json',
    'api-health': 'events/api-health.json',
    'event-daily-processing': 'events/event-daily-processing.json',
    'event-data-sync': 'events/event-data-sync.json'
}

class MockLambdaContext:
    """Mock AWS Lambda context object for local testing"""
    def __init__(self):
        self.function_name = "local-test"
        self.function_version = "$LATEST"
        self.memory_limit_in_mb = 128
        self.aws_request_id = str(uuid.uuid4())
        self.log_group_name = "/aws/lambda/local-test"
        self.log_stream_name = f"{self.aws_request_id}"
        self.identity = None
        self.client_context = None
        self.invoked_function_arn = "arn:aws:lambda:local:123456789012:function:local-test"
        
    def get_remaining_time_in_millis(self):
        """Return a mock value for remaining execution time"""
        return 30000  # 30 seconds

def load_event_from_file(event_name):
    """Load an event from a JSON file"""
    if event_name not in EVENT_FILES:
        raise ValueError(f"Unknown event: {event_name}. Available events: {', '.join(EVENT_FILES.keys())}")
    
    file_path = os.path.join(PROJECT_ROOT, EVENT_FILES[event_name])
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Event file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        return json.load(f)

def test_api_function(event_name):
    """Test the API Lambda function locally with a specific event"""
    print(f"Testing API function with event: {event_name}...")
    
    # Import the Lambda handler
    from src.api.app import lambda_handler as api_handler
    
    # Load the event from file
    event = load_event_from_file(event_name)
    
    # Create a mock context
    context = MockLambdaContext()
    
    # Call the Lambda handler
    response = api_handler(event, context)
    
    # Print the response
    print(f"Status Code: {response['statusCode']}")
    print(f"Response Body: {response['body']}")
    print(f"API function test ({event_name}) completed.")
    print("-" * 50)
    
    return response

def test_event_function(event_name):
    """Test the Event Lambda function locally with a specific event"""
    print(f"Testing Event function with event: {event_name}...")
    
    # Import the Lambda handler
    from src.event.app import lambda_handler as event_handler
    
    # Load the event from file
    event = load_event_from_file(event_name)
    
    # Create a mock context
    context = MockLambdaContext()
    
    # Call the Lambda handler
    response = event_handler(event, context)
    
    # Print the response
    print(f"Status Code: {response['statusCode']}")
    print(f"Response Body: {response['body']}")
    print(f"Event function test ({event_name}) completed.")
    print("-" * 50)
    
    return response

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Test Lambda functions locally')
    parser.add_argument('--function', '-f', choices=['api', 'event', 'all'], default='all',
                        help='The function to test (api, event, or all)')
    parser.add_argument('--event', '-e', choices=list(EVENT_FILES.keys()),
                        help='Specific event to use for testing')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    print("Starting local tests...")
    print("=" * 50)
    
    if args.event:
        # Test with a specific event
        if args.event.startswith('api-'):
            test_api_function(args.event)
        elif args.event.startswith('event-'):
            test_event_function(args.event)
        else:
            print(f"Unknown event type: {args.event}")
    else:
        # Run all tests based on function type
        if args.function in ['api', 'all']:
            test_api_function('api-hello')
            test_api_function('api-health')
        
        if args.function in ['event', 'all']:
            test_event_function('event-daily-processing')
            test_event_function('event-data-sync')
    
    print("All tests completed.")
