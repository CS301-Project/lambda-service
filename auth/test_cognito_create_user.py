"""
Simple test script for CognitoService.create_user() method
Tests the actual Cognito integration without Lambda/ALB overhead
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    """Load .env file from the same directory"""
    env_path = Path(__file__).parent / '.env'
    
    if env_path.exists():
        print(f"📁 Loading .env from: {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    os.environ[key.strip()] = value
        print("✅ Environment variables loaded\n")
    else:
        print(f"⚠️  No .env file found at: {env_path}")
        print("You can set variables manually in PowerShell:")
        print("$env:COGNITO_USER_POOL_ID='your-pool-id'")
        print("$env:COGNITO_CLIENT_ID='your-client-id'\n")

# Load .env before importing other modules
load_env_file()

from cognito_service import CognitoService
from models import UserRole

def test_create_user():
    """Test creating a user directly with CognitoService"""
    
    # Check environment variables
    user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
    client_id = os.getenv('COGNITO_CLIENT_ID')
    
    if not user_pool_id:
        print("❌ Error: COGNITO_USER_POOL_ID environment variable not set")
        print("\nOption 1: Add to .env file:")
        print("COGNITO_USER_POOL_ID=your-pool-id")
        print("\nOption 2: Set in PowerShell:")
        print("$env:COGNITO_USER_POOL_ID='your-pool-id'")
        sys.exit(1)
    
    print("🧪 Testing CognitoService.create_user()")
    print(f"User Pool ID: {user_pool_id}")
    print(f"Client ID: {client_id}")
    print("-" * 50)
    
    # Initialize service
    cognito_service = CognitoService()
    
    # Test data
    test_email = "test.user@example.com"
    test_role = UserRole.AGENT
    test_password = "TempPass123!"
    
    print(f"\n📝 Test User Details:")
    print(f"   Email: {test_email}")
    print(f"   Role: {test_role}")
    print(f"   Temporary Password: {test_password}")
    
    try:
        print("\n🚀 Creating user...")
        
        user = cognito_service.create_user(
            email=test_email,
            role=test_role,
            temporary_password=test_password,
        )
        
        print("\n✅ User created successfully!")
        print("\n📊 Response Details:")
        print(f"   Username: {user.get('Username')}")
        print(f"   User Status: {user.get('UserStatus')}")
        print(f"   Enabled: {user.get('Enabled')}")
        print(f"   User Create Date: {user.get('UserCreateDate')}")
        print(f"   User Last Modified: {user.get('UserLastModifiedDate')}")
        
        print("\n📋 Attributes:")
        for attr in user.get('Attributes', []):
            print(f"   {attr['Name']}: {attr['Value']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating user: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Provide helpful error messages
        if "UsernameExistsException" in str(e):
            print("\n💡 Tip: User already exists. Try a different username or delete the existing user:")
            print(f"   aws cognito-idp admin-delete-user --user-pool-id {user_pool_id} --username {test_email}")
        elif "InvalidPasswordException" in str(e):
            print("\n💡 Tip: Password doesn't meet requirements. Ensure it has:")
            print("   - At least 8 characters")
            print("   - Uppercase letters")
            print("   - Lowercase letters")
            print("   - Numbers")
            print("   - Special characters")
        elif "InvalidParameterException" in str(e) and "custom:role" in str(e):
            print("\n💡 Tip: The User Pool doesn't have custom:role attribute configured.")
            print("   Add it in Cognito Console or use Terraform configuration.")
        elif "ResourceNotFoundException" in str(e):
            print("\n💡 Tip: User Pool not found. Check your COGNITO_USER_POOL_ID:")
            print(f"   Current value: {user_pool_id}")
            print("   Verify in AWS Console or run:")
            print("   aws cognito-idp list-user-pools --max-results 10")
        
        return False

def verify_user_in_cognito(username):
    """Verify the user was created in Cognito"""
    user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
    
    print(f"\n🔍 Verifying user in Cognito...")
    print(f"\nRun this command to verify:")
    print(f"aws cognito-idp admin-get-user --user-pool-id {user_pool_id} --username {username}")

if __name__ == "__main__":
    print("=" * 50)
    print("CognitoService.create_user() Test")
    print("=" * 50)
    print()
    
    success = test_create_user()
    
    if success:
        verify_user_in_cognito("test.user@example.com")
        print("\n" + "=" * 50)
        print("✅ Test completed successfully!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ Test failed!")
        print("=" * 50)
        sys.exit(1)
