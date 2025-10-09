"""
Simple test script for CognitoService.create_user() method
Tests the actual Cognito integration without Lambda/ALB overhead
"""

import os
import sys
from cognito_service import CognitoService
from models import UserRole

def test_create_user():
    """Test creating a user directly with CognitoService"""
    
    # Check environment variables
    user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
    if not user_pool_id:
        print("❌ Error: COGNITO_USER_POOL_ID environment variable not set")
        print("Set it with: $env:COGNITO_USER_POOL_ID='your-pool-id'")
        sys.exit(1)
    
    print("🧪 Testing CognitoService.create_user()")
    print(f"User Pool ID: {user_pool_id}")
    print("-" * 50)
    
    # Initialize service
    cognito_service = CognitoService()
    
    # Test data
    test_email = "test.user@example.com"
    test_role = UserRole.AGENT
    test_password = "TempPass123!"
    
    print(f"\n📝 Test User Details:")
    print(f"   Email: {test_email}")
    print(f"   Username: {test_username}")
    print(f"   Role: {test_role}")
    print(f"   First Name: {test_first_name}")
    print(f"   Last Name: {test_last_name}")
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
        print(f"   Username: {user.Username}")
        print(f"   User Status: {user.UserStatus}")
        print(f"   Enabled: {user.Enabled}")
        print(f"   User Create Date: {user.UserCreateDate}")
        print(f"   User Last Modified: {user.UserLastModifiedDate}")
        
        print("\n📋 Attributes:")
        for attr in user.Attributes:
            print(f"   {attr.Name}: {attr.Value}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating user: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Provide helpful error messages
        if "UsernameExistsException" in str(e):
            print("\n💡 Tip: User already exists. Try a different username or delete the existing user:")
            print(f"   aws cognito-idp admin-delete-user --user-pool-id {user_pool_id} --username {test_username}")
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
    
    success = test_create_user()
    
    if success:
        verify_user_in_cognito("testuser")
        print("\n" + "=" * 50)
        print("✅ Test completed successfully!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ Test failed!")
        print("=" * 50)
        sys.exit(1)
