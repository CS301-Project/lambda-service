"""
Test suite for Lambda handler using pytest
"""
import os
import json
import pytest

# Set environment variables before importing handler
os.environ['COGNITO_USER_POOL_ID'] = 'us-east-1_DUMMY123'
os.environ['COGNITO_CLIENT_ID'] = 'dummy-client-id-123456'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_XRAY_SDK_ENABLED'] = 'false'
os.environ['POWERTOOLS_TRACE_DISABLED'] = 'true'

from handler import lambda_handler


class TestHealthCheckEndpoint:
    """Test cases for the health check endpoint"""
    
    def test_health_check_returns_200(self, alb_event, lambda_context):
        """Test that health check endpoint returns 200 status code"""
        # Arrange
        event = alb_event(path="/health", method="GET")
        
        # Act
        response = lambda_handler(event, lambda_context)
        
        # Assert
        assert response['statusCode'] == 200
    
    def test_health_check_returns_correct_content_type(self, alb_event, lambda_context):
        """Test that health check returns JSON content type"""
        # Arrange
        event = alb_event(path="/health", method="GET")
        
        # Act
        response = lambda_handler(event, lambda_context)
        
        # Assert
        assert response['headers']['Content-Type'] == 'application/json'
    
    def test_health_check_returns_healthy_status(self, alb_event, lambda_context):
        """Test that health check returns healthy status in body"""
        # Arrange
        event = alb_event(path="/health", method="GET")
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert body['status'] == 'healthy'
    
    def test_health_check_returns_service_name(self, alb_event, lambda_context):
        """Test that health check returns correct service name"""
        # Arrange
        event = alb_event(path="/health", method="GET")
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert body['service'] == 'auth-lambda-service'
    
    def test_health_check_returns_version(self, alb_event, lambda_context):
        """Test that health check returns version number"""
        # Arrange
        event = alb_event(path="/health", method="GET")
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert 'version' in body
        assert body['version'] == '1.0.0'
    
    def test_health_check_response_structure(self, alb_event, lambda_context):
        """Test that health check returns all expected fields"""
        # Arrange
        event = alb_event(path="/health", method="GET")
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert 'status' in body
        assert 'service' in body
        assert 'version' in body
        assert len(body) == 3  # Ensure no extra fields
