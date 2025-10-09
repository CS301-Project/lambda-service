"""
Pytest fixtures for Lambda handler tests
"""
import json
import pytest


@pytest.fixture
def alb_event():
    """
    Fixture that returns a function to create mock ALB events
    
    Usage:
        def test_something(alb_event):
            event = alb_event(path="/health", method="GET")
    """
    def _create_alb_event(path: str = "/health", method: str = "GET", body: dict = None, headers: dict = None):
        """
        Create a mock ALB (Application Load Balancer) event
        
        Args:
            path: The request path
            method: HTTP method
            body: Request body (dict)
            headers: Additional headers (dict)
        
        Returns:
            Mock ALB event dictionary
        """
        default_headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "host": "lambda-alb-123456789.us-east-1.elb.amazonaws.com",
            "user-agent": "Test/1.0",
            "x-amzn-trace-id": "Root=1-67234200-abcdef012345678912345678",
            "x-forwarded-for": "192.168.1.1",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https"
        }
        
        if headers:
            default_headers.update(headers)
        
        return {
            "requestContext": {
                "elb": {
                    "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/lambda-target/50dc6c495c0c9188"
                }
            },
            "httpMethod": method,
            "path": path,
            "queryStringParameters": {},
            "headers": default_headers,
            "body": json.dumps(body) if body else None,
            "isBase64Encoded": False
        }
    
    return _create_alb_event


@pytest.fixture
def lambda_context():
    """
    Fixture that provides a mock Lambda context object
    
    Usage:
        def test_something(lambda_context):
            response = lambda_handler(event, lambda_context)
    """
    class MockLambdaContext:
        """Mock Lambda context for testing"""
        
        def __init__(self):
            self.function_name = "auth-lambda-test"
            self.function_version = "$LATEST"
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:auth-lambda-test"
            self.memory_limit_in_mb = "128"
            self.aws_request_id = "test-request-id-123"
            self.log_group_name = "/aws/lambda/auth-lambda-test"
            self.log_stream_name = "2025/10/08/[$LATEST]test123"
        
        def get_remaining_time_in_millis(self):
            return 300000  # 5 minutes
    
    return MockLambdaContext()


@pytest.fixture
def sample_user_data():
    """
    Fixture that provides sample user data for testing
    
    Usage:
        def test_user_creation(sample_user_data):
            username = sample_user_data['username']
    """
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "temporary_password": "TestPassword123!",
        "role": "agent"
    }
