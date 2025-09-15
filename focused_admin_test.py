import requests
import sys
import json
import time
from datetime import datetime, timezone

class FocusedAdminTester:
    def __init__(self, base_url="https://aavana-green-crm.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    return True, {}
            else:
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            self.failed_tests.append(f"{name}: Exception - {str(e)}")
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

def main():
    print("🔍 FOCUSED ENHANCED ADMIN FEATURES TESTING")
    print("=" * 60)
    
    tester = FocusedAdminTester()

    # Test 1: Basic OTP Request (working)
    print("\n📱 Testing Basic OTP Request...")
    import time
    unique_phone = f"99999{str(int(time.time()))[-5:]}"
    phone_data = {"phone": unique_phone, "resend": False}
    success, otp_response = tester.run_test(
        "Basic OTP Request", 
        "POST", 
        "auth/phone-request-otp", 
        200, 
        data=phone_data
    )
    
    # Test 2: OTP Verification with correct OTP
    if success and 'demo_otp' in otp_response:
        print("\n🔐 Testing OTP Verification with Correct OTP...")
        verify_data = {
            "phone": unique_phone,
            "otp": otp_response['demo_otp']
        }
        success, verify_response = tester.run_test(
            "OTP Verification (Correct)", 
            "POST", 
            "auth/phone-verify-otp", 
            200, 
            data=verify_data
        )
        
        if success and 'access_token' in verify_response:
            print("✅ OTP verification successful, got access token")
            auth_token = verify_response['access_token']
            
            # Test 3: User Permissions with valid token
            print("\n🔐 Testing User Permissions...")
            headers = {'Authorization': f'Bearer {auth_token}'}
            tester.run_test(
                "My Permissions", 
                "GET", 
                "auth/my-permissions", 
                200, 
                headers=headers
            )
            
            # Test 4: Permission Check
            print("\n🔍 Testing Permission Check...")
            check_data = {"permission": "leads:view"}
            tester.run_test(
                "Permission Check", 
                "POST", 
                "auth/check-permission", 
                200, 
                data=check_data,
                headers=headers
            )

    # Test 5: Permissions Listing (no auth required)
    print("\n📋 Testing Permissions Listing...")
    tester.run_test(
        "Permissions Listing", 
        "GET", 
        "auth/permissions", 
        200
    )

    # Test 6: User Registration with correct role format
    print("\n👤 Testing User Registration...")
    timestamp = str(int(time.time()))
    user_data = {
        "username": f"testuser{timestamp}",
        "email": f"testuser{timestamp}@example.com",
        "phone": f"987654{timestamp[-4:]}",
        "full_name": "Test User",
        "role": "Employee",  # Correct format
        "password": "SecurePass123!",
        "department": "Testing"
    }
    success, user_response = tester.run_test(
        "User Registration", 
        "POST", 
        "auth/register", 
        200, 
        data=user_data
    )
    
    if success:
        # Test 7: Login with new user
        print("\n🔑 Testing Login...")
        login_data = {
            "identifier": user_data["username"],
            "password": user_data["password"]
        }
        success, login_response = tester.run_test(
            "User Login", 
            "POST", 
            "auth/login", 
            200, 
            data=login_data
        )
        
        if success and 'access_token' in login_response:
            # Test 8: Access control test
            print("\n🛡️ Testing Access Control...")
            headers = {'Authorization': f'Bearer {login_response["access_token"]}'}
            
            # Should work - leads access
            tester.run_test(
                "Leads Access (Employee)", 
                "GET", 
                "leads", 
                200, 
                headers=headers
            )
            
            # Should fail - users access (Employee role)
            tester.run_test(
                "Users Access (Employee - Should Fail)", 
                "GET", 
                "users", 
                403, 
                headers=headers
            )

    # Test 9: Email Integration (Password Reset)
    print("\n📧 Testing Email Integration...")
    email_data = {"email": "test@example.com"}
    tester.run_test(
        "Password Reset Email", 
        "POST", 
        "auth/forgot-password", 
        200, 
        data=email_data
    )

    # Final Results
    print("\n" + "=" * 60)
    print(f"📊 FOCUSED TEST RESULTS")
    print("=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for i, failed_test in enumerate(tester.failed_tests, 1):
            print(f"   {i}. {failed_test}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())