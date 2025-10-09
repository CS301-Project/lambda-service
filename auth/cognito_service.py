"""
AWS Cognito service for user management operations
"""
import os
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

from models import UserRole, UserResponse

logger = Logger(child=True)


class CognitoService:
    """Service class for AWS Cognito operations"""
    
    def __init__(self):
        self.client = boto3.client('cognito-idp')
        self.user_pool_id = os.environ.get('COGNITO_USER_POOL_ID')
        self.client_id = os.environ.get('COGNITO_CLIENT_ID')
        self.root_admin_username = os.environ.get('ROOT_ADMIN_USERNAME', 'root_admin')
        
        if not self.user_pool_id or not self.client_id:
            raise ValueError("COGNITO_USER_POOL_ID and COGNITO_CLIENT_ID must be set")
        
    def create_user(
        self,
        email: str,
        role: UserRole,
        temporary_password: str,
    ) -> Dict[str, Any]:
        """
        Create a new user in Cognito User Pool
        
        Args:
            email: User email address
            role: User role (admin or agent)
            temporary_password: Temporary password for the user
            
        Returns:
            Dict with Cognito user details (Username, Attributes, UserStatus, etc.)
            
        Raises:
            ClientError: If user creation fails
        """
        try:
            # Build user attributes
            user_attributes = [
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'},
                {'Name': 'custom:role', 'Value': role.value}
            ]
            
            logger.info(f"Creating user {email} with role {role.value}")
            
            # Create user in Cognito
            response = self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,  # Use email as username
                UserAttributes=user_attributes,
                TemporaryPassword=temporary_password,
                MessageAction='SUPPRESS',  # Don't send welcome email
                DesiredDeliveryMediums=['EMAIL']  # Set email as delivery medium
            )
            
            logger.info(f"User {email} created successfully with role {role.value}")
            
            # Return the raw Cognito user object for testing/debugging
            # In production, you might want to return _map_user_response(response['User'])
            return response['User']
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Cognito error creating user {email}: {error_code} - {error_message}")
            
            # Re-raise with original error for handler to process
            raise
        except Exception as e:
            logger.exception(f"Unexpected error creating user {email}")
            raise
    
    def _map_user_response(self, cognito_user: Dict[str, Any]) -> UserResponse:
        """
        Map Cognito user object to UserResponse model
        
        Args:
            cognito_user: Cognito user object from API response
            
        Returns:
            UserResponse object
        """
        # Extract attributes from Cognito user
        attributes = {attr['Name']: attr['Value'] for attr in cognito_user.get('Attributes', [])}
        
        # Get role from custom attribute
        role = attributes.get('custom:role', UserRole.AGENT.value)
        
        return UserResponse(
            email=attributes.get('email', ''),
            role=UserRole(role),
            enabled=cognito_user.get('Enabled', True)
            )