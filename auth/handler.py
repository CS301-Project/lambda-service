import os
from typing import Dict, Any
from botocore.exceptions import ClientError
from pydantic import ValidationError

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import ALBResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    InternalServerError,
    NotFoundError,
    UnauthorizedError
)

import models
from cognito_service import CognitoService

# Initialize Powertools utilities
tracer = Tracer()
logger = Logger()
app = ALBResolver()

# Initialize Cognito service
cognito_service = CognitoService()

@app.get("/health")
@tracer.capture_method
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'auth-lambda-service',
        'version': '1.0.0'
    }, 200

# Lambda handler
@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPLICATION_LOAD_BALANCER)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Main Lambda handler for ALB events
    
    Args:
        event: ALB event
        context: Lambda context
        
    Returns:
        ALB response
    """
    return app.resolve(event, context)
