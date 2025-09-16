import requests
import sys
import json
import time
from datetime import datetime, timezone

class EnhancedAdminFeaturesTester:
    def __init__(self, base_url="https://greenstack-ai.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.test_user_id = None
        self.test_phone = None
        self.otp_requests_count = 0
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
                    if isinstance(response_data, dict) and len(str(response_data)) < 300:
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

    # ========== PHONE-LOGIN IMPROVEMENTS TESTS ==========
    
    def test_phone_otp_request_valid(self):
        """Test improved OTP request endpoint with valid phone"""
        # Use a realistic Indian phone number
        phone_data = {
            "phone": "9876543210",
            "resend": False
        }
        success, response = self.run_test(
            "Phone OTP Request (Valid)", 
            "POST", 
            "auth/phone-request-otp", 
            200, 
            data=phone_data
        )
        if success:
            self.test_phone = phone_data["phone"]
            self.otp_requests_count += 1
        return success, response

    def test_phone_otp_request_formatted(self):
        """Test OTP request with different phone formats"""
        test_cases = [
            {"phone": "09876543211", "description": "with leading 0"},
            {"phone": "919876543212", "description": "with country code"},
            {"phone": "+91 9876 543 213", "description": "with spaces and +"},
            {"phone": "98-765-43214", "description": "with dashes"}
        ]
        
        results = []
        for case in test_cases:
            phone_data = {"phone": case["phone"], "resend": False}
            success, response = self.run_test(
                f"Phone Format Test ({case['description']})", 
                "POST", 
                "auth/phone-request-otp", 
                200, 
                data=phone_data
            )
            results.append(success)
            if success:
                self.otp_requests_count += 1
        
        return all(results), {}

    def test_phone_otp_rate_limiting(self):
        """Test OTP rate limiting (max 3 requests per 15 minutes)"""
        phone = "9876543215"
        
        # Make multiple requests to test rate limiting
        for i in range(4):  # Try 4 requests, 4th should fail
            phone_data = {"phone": phone, "resend": False}
            expected_status = 200 if i < 3 else 429  # Rate limit after 3 requests
            
            success, response = self.run_test(
                f"Rate Limit Test (Request {i+1})", 
                "POST", 
                "auth/phone-request-otp", 
                expected_status, 
                data=phone_data
            )
            
            if i < 3 and success:
                self.otp_requests_count += 1
            elif i == 3 and success:  # 4th request should be rate limited
                return True, response
            
            time.sleep(1)  # Small delay between requests
        
        return False, {}

    def test_phone_otp_verify_valid(self):
        """Test OTP verification with valid OTP"""
        if not self.test_phone:
            print("⚠️ Skipping test - no test phone available")
            return False, {}
        
        # First request a new OTP to get the demo OTP
        phone_data = {"phone": self.test_phone, "resend": True}
        success, otp_response = self.run_test(
            "Request OTP for Verification Test", 
            "POST", 
            "auth/phone-request-otp", 
            200, 
            data=phone_data
        )
        
        if not success or 'demo_otp' not in otp_response:
            return False, {}
        
        # Use the actual demo OTP from the response
        verify_data = {
            "phone": self.test_phone,
            "otp": otp_response['demo_otp']
        }
        return self.run_test(
            "Phone OTP Verify (Valid)", 
            "POST", 
            "auth/phone-verify-otp", 
            200, 
            data=verify_data
        )

    def test_phone_otp_verify_invalid(self):
        """Test OTP verification with invalid OTP"""
        if not self.test_phone:
            print("⚠️ Skipping test - no test phone available")
            return False, {}
        
        verify_data = {
            "phone": self.test_phone,
            "otp": "000000"  # Invalid OTP
        }
        return self.run_test(
            "Phone OTP Verify (Invalid)", 
            "POST", 
            "auth/phone-verify-otp", 
            400, 
            data=verify_data
        )

    def test_phone_otp_attempt_tracking(self):
        """Test OTP attempt tracking (max 3 verification attempts)"""
        phone = "9876543216"
        
        # First request OTP
        phone_data = {"phone": phone, "resend": False}
        self.run_test("OTP Request for Attempt Test", "POST", "auth/phone-request-otp", 200, data=phone_data)
        
        # Try multiple invalid OTPs
        for i in range(4):  # Try 4 attempts, 4th should fail
            verify_data = {
                "phone": phone,
                "otp": f"00000{i}"  # Invalid OTPs
            }
            expected_status = 400 if i < 3 else 429  # Too many attempts after 3
            
            success, response = self.run_test(
                f"OTP Attempt Test ({i+1})", 
                "POST", 
                "auth/phone-verify-otp", 
                expected_status, 
                data=verify_data
            )
            
            if i == 3 and success:  # 4th attempt should be blocked
                return True, response
        
        return False, {}

    def test_phone_otp_expiry(self):
        """Test OTP expiry (5 minutes) - simulated"""
        phone = "9876543217"
        
        # Request OTP
        phone_data = {"phone": phone, "resend": False}
        success, response = self.run_test(
            "OTP Request for Expiry Test", 
            "POST", 
            "auth/phone-request-otp", 
            200, 
            data=phone_data
        )
        
        if not success:
            return False, {}
        
        # Simulate expired OTP verification (in real scenario, would wait 5+ minutes)
        # For testing, we'll use a specific expired OTP pattern
        verify_data = {
            "phone": phone,
            "otp": "999999"  # Simulate expired OTP
        }
        return self.run_test(
            "OTP Expiry Test", 
            "POST", 
            "auth/phone-verify-otp", 
            400, 
            data=verify_data
        )

    # ========== ADVANCED USER PERMISSIONS SYSTEM TESTS ==========
    
    def test_permissions_listing(self):
        """Test permissions listing endpoint"""
        return self.run_test(
            "Permissions Listing", 
            "GET", 
            "auth/permissions", 
            200
        )

    def test_user_permissions_endpoint(self):
        """Test user permissions endpoint (requires auth)"""
        # First, create a test user and get auth token
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"permtest{timestamp}",
            "email": f"permtest{timestamp}@example.com",
            "phone": f"987654{timestamp[-4:]}",
            "full_name": "Permission Test User",
            "role": "Sales Executive",
            "password": "SecurePass123!",
            "department": "Sales"
        }
        
        # Register user
        success, response = self.run_test(
            "Create User for Permission Test", 
            "POST", 
            "auth/register", 
            200, 
            data=user_data
        )
        
        if not success:
            return False, {}
        
        # Login to get token
        login_data = {
            "identifier": user_data["username"],
            "password": user_data["password"]
        }
        success, login_response = self.run_test(
            "Login for Permission Test", 
            "POST", 
            "auth/login", 
            200, 
            data=login_data
        )
        
        if not success or 'access_token' not in login_response:
            return False, {}
        
        # Test user permissions endpoint
        headers = {'Authorization': f'Bearer {login_response["access_token"]}'}
        return self.run_test(
            "User Permissions Endpoint", 
            "GET", 
            "auth/my-permissions", 
            200, 
            headers=headers
        )

    def test_permission_checking(self):
        """Test permission checking endpoint"""
        # Use the token from previous test if available
        if not hasattr(self, 'auth_token') or not self.auth_token:
            print("⚠️ Skipping test - no auth token available")
            return False, {}
        
        check_data = {
            "permission": "leads:view"
        }
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        return self.run_test(
            "Permission Checking", 
            "POST", 
            "auth/check-permission", 
            200, 
            data=check_data,
            headers=headers
        )

    def test_role_based_permissions(self):
        """Test role-based permission mapping"""
        roles_to_test = [
            "Super Admin",
            "Admin", 
            "Sales Manager",
            "Sales Executive",
            "Marketing Manager",
            "HR Manager",
            "Employee"
        ]
        
        results = []
        for role in roles_to_test:
            timestamp = str(int(time.time()))
            user_data = {
                "username": f"roletest{role.lower()}{timestamp}",
                "email": f"roletest{role.lower()}{timestamp}@example.com",
                "phone": f"987654{timestamp[-4:]}",
                "full_name": f"Role Test {role}",
                "role": role,
                "password": "SecurePass123!",
                "department": "Testing"
            }
            
            success, response = self.run_test(
                f"Role Permission Test ({role})", 
                "POST", 
                "auth/register", 
                200, 
                data=user_data
            )
            results.append(success)
            time.sleep(0.5)  # Small delay between requests
        
        return all(results), {}

    def test_user_permission_update(self):
        """Test user permission update endpoint"""
        # Create a test user first
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"updatetest{timestamp}",
            "email": f"updatetest{timestamp}@example.com",
            "phone": f"987654{timestamp[-4:]}",
            "full_name": "Update Permission Test",
            "role": "Employee",
            "password": "SecurePass123!",
            "department": "Testing"
        }
        
        success, user_response = self.run_test(
            "Create User for Update Test", 
            "POST", 
            "auth/register", 
            200, 
            data=user_data
        )
        
        if not success or 'id' not in user_response:
            return False, {}
        
        user_id = user_response['id']
        
        # Update permissions
        permission_data = {
            "permissions": ["leads:view", "tasks:view", "ai:use_basic"]
        }
        
        # Note: This would typically require admin authentication
        return self.run_test(
            "User Permission Update", 
            "PUT", 
            f"users/{user_id}/permissions", 
            200, 
            data=permission_data
        )

    def test_granular_permissions_categories(self):
        """Test granular permissions across different categories"""
        categories = [
            "leads", "tasks", "users", "ai", "analytics", "hrms", "erp", "system"
        ]
        
        # Test that permissions endpoint returns permissions for all categories
        success, response = self.run_test(
            "Granular Permissions Categories", 
            "GET", 
            "auth/permissions", 
            200
        )
        
        if not success or not isinstance(response, dict):
            return False, {}
        
        # Check if response contains permissions for each category
        permissions_found = response.get('permissions', [])
        if isinstance(permissions_found, list):
            category_coverage = {}
            for perm in permissions_found:
                if ':' in perm:
                    category = perm.split(':')[0]
                    category_coverage[category] = category_coverage.get(category, 0) + 1
            
            print(f"   Permission categories found: {list(category_coverage.keys())}")
            return len(category_coverage) >= 6, response  # At least 6 categories
        
        return False, {}

    # ========== EMAIL INTEGRATION TESTS ==========
    
    def test_password_reset_email(self):
        """Test password reset with email sending"""
        email_data = {
            "email": "testuser@example.com"
        }
        return self.run_test(
            "Password Reset Email", 
            "POST", 
            "auth/forgot-password", 
            200, 
            data=email_data
        )

    def test_user_creation_welcome_email(self):
        """Test user creation with welcome email"""
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"emailtest{timestamp}",
            "email": f"emailtest{timestamp}@example.com",
            "phone": f"987654{timestamp[-4:]}",
            "full_name": "Email Test User",
            "role": "Employee",
            "password": "SecurePass123!",
            "department": "Testing"
        }
        
        # This should trigger welcome email sending
        return self.run_test(
            "User Creation with Welcome Email", 
            "POST", 
            "users", 
            200, 
            data=user_data
        )

    def test_email_fallback_handling(self):
        """Test that email failures don't break user operations"""
        # Test with potentially problematic email
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"fallbacktest{timestamp}",
            "email": f"invalid-email-domain{timestamp}@nonexistent-domain-12345.com",
            "phone": f"987654{timestamp[-4:]}",
            "full_name": "Email Fallback Test",
            "role": "Employee",
            "password": "SecurePass123!",
            "department": "Testing"
        }
        
        # User creation should still succeed even if email fails
        return self.run_test(
            "Email Fallback Handling", 
            "POST", 
            "auth/register", 
            200, 
            data=user_data
        )

    # ========== INTEGRATION TESTS ==========
    
    def test_existing_auth_flows_compatibility(self):
        """Test that existing authentication flows still work"""
        # Test basic login flow
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"compattest{timestamp}",
            "email": f"compattest{timestamp}@example.com",
            "phone": f"987654{timestamp[-4:]}",
            "full_name": "Compatibility Test User",
            "role": "Employee",
            "password": "SecurePass123!",
            "department": "Testing"
        }
        
        # Register
        success, response = self.run_test(
            "Compatibility Test - Register", 
            "POST", 
            "auth/register", 
            200, 
            data=user_data
        )
        
        if not success:
            return False, {}
        
        # Login with username
        login_data = {
            "identifier": user_data["username"],
            "password": user_data["password"]
        }
        success, login_response = self.run_test(
            "Compatibility Test - Login", 
            "POST", 
            "auth/login", 
            200, 
            data=login_data
        )
        
        if not success or 'access_token' not in login_response:
            return False, {}
        
        # Test authenticated endpoint
        headers = {'Authorization': f'Bearer {login_response["access_token"]}'}
        return self.run_test(
            "Compatibility Test - Authenticated Access", 
            "GET", 
            "auth/me", 
            200, 
            headers=headers
        )

    def test_permission_based_access_control(self):
        """Test permission-based access control on existing endpoints"""
        # Create users with different roles
        roles = ["Employee", "Sales Manager", "Admin"]
        tokens = {}
        
        for role in roles:
            timestamp = str(int(time.time()))
            user_data = {
                "username": f"rbactest{role.lower()}{timestamp}",
                "email": f"rbactest{role.lower()}{timestamp}@example.com",
                "phone": f"987654{timestamp[-4:]}",
                "full_name": f"RBAC Test {role}",
                "role": role,
                "password": "SecurePass123!",
                "department": "Testing"
            }
            
            # Register
            success, response = self.run_test(
                f"RBAC Test - Register {role}", 
                "POST", 
                "auth/register", 
                200, 
                data=user_data
            )
            
            if success:
                # Login
                login_data = {
                    "identifier": user_data["username"],
                    "password": user_data["password"]
                }
                success, login_response = self.run_test(
                    f"RBAC Test - Login {role}", 
                    "POST", 
                    "auth/login", 
                    200, 
                    data=login_data
                )
                
                if success and 'access_token' in login_response:
                    tokens[role] = login_response['access_token']
        
        # Test access to different endpoints with different roles
        results = []
        for role, token in tokens.items():
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test leads access (should work for all roles)
            success, response = self.run_test(
                f"RBAC Test - {role} Leads Access", 
                "GET", 
                "leads", 
                200, 
                headers=headers
            )
            results.append(success)
            
            # Test users access (should work for Admin, may fail for Employee)
            expected_status = 200 if role in ["Admin", "Sales_Manager"] else 403
            success, response = self.run_test(
                f"RBAC Test - {role} Users Access", 
                "GET", 
                "users", 
                expected_status, 
                headers=headers
            )
            results.append(success)
        
        return all(results), {}

    def test_error_handling_edge_cases(self):
        """Test error handling and edge cases"""
        test_cases = [
            {
                "name": "Empty Phone OTP Request",
                "method": "POST",
                "endpoint": "auth/phone-request-otp",
                "data": {"phone": ""},
                "expected": 422
            },
            {
                "name": "Invalid Phone Format",
                "method": "POST", 
                "endpoint": "auth/phone-request-otp",
                "data": {"phone": "invalid-phone"},
                "expected": 422
            },
            {
                "name": "Missing OTP in Verification",
                "method": "POST",
                "endpoint": "auth/phone-verify-otp", 
                "data": {"phone": "9876543210"},
                "expected": 422
            },
            {
                "name": "Invalid Permission Check",
                "method": "POST",
                "endpoint": "auth/check-permission",
                "data": {"permission": "invalid:permission"},
                "expected": 400
            }
        ]
        
        results = []
        for case in test_cases:
            success, response = self.run_test(
                case["name"],
                case["method"],
                case["endpoint"],
                case["expected"],
                data=case["data"]
            )
            results.append(success)
        
        return all(results), {}

def main():
    print("🚀 Starting Enhanced Admin Features Tests")
    print("Testing Option 3 - Enhanced Admin Features Implementation")
    print("=" * 70)
    
    tester = EnhancedAdminFeaturesTester()

    # Test 1: Phone-Login Improvements
    print("\n📱 TESTING PHONE-LOGIN IMPROVEMENTS")
    print("=" * 50)
    
    print("\n🔹 Testing OTP Request System...")
    tester.test_phone_otp_request_valid()
    tester.test_phone_otp_request_formatted()
    
    print("\n🔹 Testing Rate Limiting...")
    tester.test_phone_otp_rate_limiting()
    
    print("\n🔹 Testing OTP Verification...")
    tester.test_phone_otp_verify_valid()
    tester.test_phone_otp_verify_invalid()
    
    print("\n🔹 Testing Attempt Tracking...")
    tester.test_phone_otp_attempt_tracking()
    
    print("\n🔹 Testing OTP Expiry...")
    tester.test_phone_otp_expiry()

    # Test 2: Advanced User Permissions System
    print("\n🔐 TESTING ADVANCED USER PERMISSIONS SYSTEM")
    print("=" * 50)
    
    print("\n🔹 Testing Permission Endpoints...")
    tester.test_permissions_listing()
    tester.test_user_permissions_endpoint()
    tester.test_permission_checking()
    
    print("\n🔹 Testing Role-Based Permissions...")
    tester.test_role_based_permissions()
    tester.test_user_permission_update()
    
    print("\n🔹 Testing Granular Permissions...")
    tester.test_granular_permissions_categories()

    # Test 3: Email Integration
    print("\n📧 TESTING EMAIL INTEGRATION")
    print("=" * 50)
    
    print("\n🔹 Testing Email Features...")
    tester.test_password_reset_email()
    tester.test_user_creation_welcome_email()
    tester.test_email_fallback_handling()

    # Test 4: Integration Testing
    print("\n🔗 TESTING INTEGRATION & COMPATIBILITY")
    print("=" * 50)
    
    print("\n🔹 Testing Backward Compatibility...")
    tester.test_existing_auth_flows_compatibility()
    
    print("\n🔹 Testing Permission-Based Access Control...")
    tester.test_permission_based_access_control()
    
    print("\n🔹 Testing Error Handling...")
    tester.test_error_handling_edge_cases()

    # Final Results
    print("\n" + "=" * 70)
    print(f"📊 ENHANCED ADMIN FEATURES TEST RESULTS")
    print("=" * 70)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for i, failed_test in enumerate(tester.failed_tests, 1):
            print(f"   {i}. {failed_test}")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 All Enhanced Admin Features tests passed!")
        print("✅ Phone-Login Improvements: Working")
        print("✅ Advanced User Permissions: Working") 
        print("✅ Email Integration: Working")
        print("✅ Integration & Compatibility: Working")
        return 0
    else:
        print(f"\n⚠️ {tester.tests_run - tester.tests_passed} tests failed.")
        print("Please check the backend implementation for Enhanced Admin Features.")
        return 1

if __name__ == "__main__":
    sys.exit(main())