"""
Test script for Lambda handler - Health Check Endpoint
"""
import os

# Set dummy environment variables BEFORE importing handler
# This prevents Cognito initialization errors
os.environ['COGNITO_USER_POOL_ID'] = 'us-east-1_DUMMY123'
os.environ['COGNITO_CLIENT_ID'] = 'dummy-client-id-123456'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Disable AWS X-Ray for local testing
os.environ['AWS_XRAY_SDK_ENABLED'] = 'false'
os.environ['POWERTOOLS_TRACE_DISABLED'] = 'true'

# Now import handler after env vars are set
import json
from handler import lambda_handler


def create_alb_event(path: str = "/health", method: str = "GET", body: dict = None):
    """
    Create a mock ALB (Application Load Balancer) event for testing
    
    Args:
        path: The request path
        method: HTTP method
        body: Request body (dict)
    
    Returns:
        Mock ALB event dictionary
    """
    return {
        "requestContext": {
            "elb": {
                "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/lambda-target/50dc6c495c0c9188"
            }
        },
        "httpMethod": method,
        "path": path,
        "queryStringParameters": {},
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
            "host": "lambda-alb-123456789.us-east-1.elb.amazonaws.com",
            "user-agent": "Test/1.0",
            "x-amzn-trace-id": "Root=1-67234200-abcdef012345678912345678",
            "x-forwarded-for": "192.168.1.1",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https"
        },
        "body": json.dumps(body) if body else None,
        "isBase64Encoded": False
    }


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


def test_health_check():
    """Test the health check endpoint"""
    print("=" * 60)
    print("Testing Health Check Endpoint")
    print("=" * 60)
    
    # Create mock event and context
    event = create_alb_event(path="/health", method="GET")
    context = MockLambdaContext()
    
    # Call the Lambda handler
    try:
        response = lambda_handler(event, context)
        
        print("\n✅ Lambda Handler Response:")
        print(f"Status Code: {response.get('statusCode')}")
        print(f"Headers: {json.dumps(response.get('headers', {}), indent=2)}")
        
        # Parse and display the body
        body = json.loads(response.get('body', '{}'))
        print(f"\nResponse Body:")
        print(json.dumps(body, indent=2))
        
        # Validate response
        assert response['statusCode'] == 200, f"Expected status 200, got {response['statusCode']}"
        assert body.get('status') == 'healthy', "Status should be 'healthy'"
        assert body.get('service') == 'auth-lambda-service', "Service name mismatch"
        
        print("\n" + "=" * 60)
        print("✅ HEALTH CHECK TEST PASSED!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run the test
    success = test_health_check()
    exit(0 if success else 1)
