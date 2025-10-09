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

from models import CreateUserRequest, CreateUserResponse
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

@app.post("/api/users")
@tracer.capture_method
def create_user() -> tuple[dict, int]:
    """
    Create a new user in the CRM system
    
    Returns:
        tuple[dict, int]: Response body and HTTP status code (201)
    """
    try:
        # Parse and validate request body
        body = app.current_event.json_body
        
        if not body:
            raise BadRequestError("Request body is required")
        
        request = CreateUserRequest(**body)
        
        logger.info(f"Creating user: {request.username} with role: {request.role}")
        
        # Create user in Cognito
        user = cognito_service.create_user(
            username=request.username,
            email=request.email,
            role=request.role,
            temporary_password=request.temporary_password,
            first_name=request.first_name,
            last_name=request.last_name
        )
        
        logger.info(f"User {request.username} created successfully")
        
        # Return validated response using CreateUserResponse model
        response = CreateUserResponse(
            message="User created successfully",
            user=user
        )
        
        return response.model_dump(), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error for user creation: {e.errors()}")
        errors = [{"field": err["loc"][0], "message": err["msg"]} for err in e.errors()]
        raise BadRequestError(f"Invalid request data: {errors}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'UsernameExistsException':
            logger.warning(f"Attempt to create duplicate user: {body.get('username')}")
            raise BadRequestError(f"Username already exists")
        elif error_code == 'InvalidPasswordException':
            logger.warning(f"Invalid password provided for user: {body.get('username')}")
            raise BadRequestError(f"Password does not meet requirements: {error_message}")
        elif error_code == 'InvalidParameterException':
            logger.warning(f"Invalid parameter: {error_message}")
            raise BadRequestError(f"Invalid parameter: {error_message}")
        elif error_code == 'UserLambdaValidationException':
            logger.error(f"Lambda validation error: {error_message}")
            raise InternalServerError("User validation failed")
        else:
            logger.error(f"Cognito error ({error_code}): {error_message}")
            raise InternalServerError(f"Failed to create user. Please try again later.")
            
    except BadRequestError:
        # Re-raise BadRequestError as-is
        raise
        
    except Exception as e:
        logger.exception("Unexpected error creating user")
        raise InternalServerError(f"An unexpected error occurred while creating the user")


# ==========================
# ===== Lambda handler =====
# ==========================
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

