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