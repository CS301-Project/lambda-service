"""
Test suite for create_user endpoint
"""
import json
import pytest
from botocore.exceptions import ClientError
from pydantic import ValidationError

# Import after environment variables are set in conftest.py
from handler import lambda_handler
from models import UserRole


class TestCreateUserEndpoint:
    """Test cases for the POST /api/users endpoint"""
    
    def test_create_user_success(self, alb_event, lambda_context, sample_user_data):
        """Test successful user creation"""
        # Arrange
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 201
        assert body['message'] == 'User created successfully'
        assert 'user' in body
        assert body['user']['username'] == sample_user_data['username'].lower()
        assert body['user']['email'] == sample_user_data['email']
        assert body['user']['role'] == sample_user_data['role']
        assert body['user']['enabled'] is True
    
    def test_create_user_with_names(self, alb_event, lambda_context):
        """Test user creation with first and last names"""
        # Arrange
        user_data = {
            "username": "john_smith",
            "email": "john.smith@example.com",
            "password": "SecurePass123!",
            "role": "agent",
            "temporary_password": "TempPass123!",
            "first_name": "john",
            "last_name": "smith"
        }
        event = alb_event(path="/api/users", method="POST", body=user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 201
        assert body['user']['username'] == 'john_smith'
    
    def test_create_user_invalid_email(self, alb_event, lambda_context, sample_user_data):
        """Test user creation with invalid email format"""
        # Arrange
        sample_user_data['email'] = 'invalid-email'
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 400
        assert 'Invalid request data' in body['message']
    
    def test_create_user_short_username(self, alb_event, lambda_context, sample_user_data):
        """Test user creation with username too short"""
        # Arrange
        sample_user_data['username'] = 'ab'  # Less than 3 chars
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 400
        assert 'Invalid request data' in body['message']
    
    def test_create_user_invalid_username_chars(self, alb_event, lambda_context, sample_user_data):
        """Test user creation with invalid username characters"""
        # Arrange
        sample_user_data['username'] = 'user@name!'  # Contains invalid chars
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 400
        assert 'Invalid request data' in body['message']
    
    def test_create_user_weak_password(self, alb_event, lambda_context, sample_user_data):
        """Test user creation with weak password"""
        # Arrange
        sample_user_data['temporary_password'] = 'weak'  # Too short, no complexity
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 400
        assert 'Invalid request data' in body['message']
    
    def test_create_user_no_uppercase_password(self, alb_event, lambda_context, sample_user_data):
        """Test user creation with password missing uppercase"""
        # Arrange
        sample_user_data['temporary_password'] = 'password123!'
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 400
        assert 'uppercase' in body['message'].lower()
    
    def test_create_user_no_number_password(self, alb_event, lambda_context, sample_user_data):
        """Test user creation with password missing number"""
        # Arrange
        sample_user_data['temporary_password'] = 'PasswordOnly!'
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 400
        assert 'number' in body['message'].lower()
    
    def test_create_user_no_special_char_password(self, alb_event, lambda_context, sample_user_data):
        """Test user creation with password missing special character"""
        # Arrange
        sample_user_data['temporary_password'] = 'Password123'
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 400
        assert 'special character' in body['message'].lower()
    
    def test_create_user_invalid_role(self, alb_event, lambda_context, sample_user_data):
        """Test user creation with invalid role"""
        # Arrange
        sample_user_data['role'] = 'superuser'  # Invalid role
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 400
        assert 'Invalid request data' in body['message']
    
    def test_create_user_missing_required_fields(self, alb_event, lambda_context):
        """Test user creation with missing required fields"""
        # Arrange
        incomplete_data = {
            "username": "testuser"
            # Missing email, role, password
        }
        event = alb_event(path="/api/users", method="POST", body=incomplete_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 400
        assert 'Invalid request data' in body['message']
    
    def test_create_user_empty_body(self, alb_event, lambda_context):
        """Test user creation with empty request body"""
        # Arrange
        event = alb_event(path="/api/users", method="POST", body=None)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 400
        assert 'Request body is required' in body['message']
    
    def test_create_user_username_normalization(self, alb_event, lambda_context, sample_user_data):
        """Test that username is normalized to lowercase"""
        # Arrange
        sample_user_data['username'] = 'TestUser123'
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 201
        assert body['user']['username'] == 'testuser123'
    
    def test_create_user_name_capitalization(self, alb_event, lambda_context, sample_user_data):
        """Test that first and last names are properly capitalized"""
        # Arrange
        sample_user_data['first_name'] = 'john'
        sample_user_data['last_name'] = 'doe'
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        
        # Assert
        assert response['statusCode'] == 201
    
    def test_create_admin_user(self, alb_event, lambda_context, sample_user_data):
        """Test creating a user with admin role"""
        # Arrange
        sample_user_data['role'] = 'admin'
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 201
        assert body['user']['role'] == 'admin'
    
    def test_create_agent_user(self, alb_event, lambda_context, sample_user_data):
        """Test creating a user with agent role"""
        # Arrange
        sample_user_data['role'] = 'agent'
        event = alb_event(path="/api/users", method="POST", body=sample_user_data)
        
        # Act
        response = lambda_handler(event, lambda_context)
        body = json.loads(response['body'])
        
        # Assert
        assert response['statusCode'] == 201
        assert body['user']['role'] == 'agent'
