#!/usr/bin/env python3
"""
Focused Authentication System Test for Aavana Greens CRM
Tests the specific authentication issues identified in the review request
"""

import requests
import json
import time
from datetime import datetime

class AuthenticationTester:
    def __init__(self, base_url="https://aavana-greens-crm.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.test_results = []
        self.auth_token = None
        self.admin_token = None
        self.test_user_data = None
        self.admin_user_data = None
        
    def log_result(self, test_name, success, details="", expected="", actual=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and expected and actual:
            print(f"    Expected: {expected}")
            print(f"    Actual: {actual}")
        print()

    def test_user_registration_and_login_flow(self):
        """Test complete user registration and login flow"""
        print("🔐 Testing User Registration and Login Flow")
        print("=" * 60)
        
        # Generate unique test data
        timestamp = str(int(time.time()))
        
        # Test 1: Register regular user
        user_data = {
            "username": f"testuser{timestamp}",
            "email": f"testuser{timestamp}@example.com", 
            "phone": f"987654{timestamp[-4:]}",
            "full_name": "Test User",
            "role": "Employee",
            "password": "SecurePass123!",
            "department": "Sales"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=user_data)
            if response.status_code == 200:
                self.test_user_data = user_data
                user_response = response.json()
                self.log_result("User Registration", True, f"User created with ID: {user_response.get('id')}")
            else:
                self.log_result("User Registration", False, f"Status: {response.status_code}, Error: {response.text}")
                return False
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
            return False
            
        # Test 2: Register admin user
        admin_data = {
            "username": f"admin{timestamp}",
            "email": f"admin{timestamp}@example.com",
            "phone": f"987655{timestamp[-4:]}",
            "full_name": "Admin User",
            "role": "Admin",
            "password": "AdminPass123!",
            "department": "Management"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=admin_data)
            if response.status_code == 200:
                self.admin_user_data = admin_data
                admin_response = response.json()
                self.log_result("Admin Registration", True, f"Admin created with ID: {admin_response.get('id')}")
            else:
                self.log_result("Admin Registration", False, f"Status: {response.status_code}, Error: {response.text}")
        except Exception as e:
            self.log_result("Admin Registration", False, f"Exception: {str(e)}")
            
        return True

    def test_login_endpoints(self):
        """Test all login endpoints with different identifiers"""
        print("🔑 Testing Login Endpoints")
        print("=" * 40)
        
        if not self.test_user_data:
            self.log_result("Login Tests", False, "No test user data available")
            return False
            
        # Test 3: Username login
        login_data = {
            "identifier": self.test_user_data["username"],
            "password": self.test_user_data["password"]
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.log_result("Username Login", True, f"Token received, expires in {token_data.get('expires_in')} seconds")
            else:
                self.log_result("Username Login", False, f"Status: {response.status_code}, Error: {response.text}")
        except Exception as e:
            self.log_result("Username Login", False, f"Exception: {str(e)}")
            
        # Test 4: Email login
        login_data = {
            "identifier": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                self.log_result("Email Login", True, "Login successful with email")
            else:
                self.log_result("Email Login", False, f"Status: {response.status_code}, Error: {response.text}")
        except Exception as e:
            self.log_result("Email Login", False, f"Exception: {str(e)}")
            
        # Test 5: Phone login
        login_data = {
            "identifier": self.test_user_data["phone"],
            "password": self.test_user_data["password"]
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                self.log_result("Phone Login", True, "Login successful with phone")
            else:
                self.log_result("Phone Login", False, f"Status: {response.status_code}, Error: {response.text}")
        except Exception as e:
            self.log_result("Phone Login", False, f"Exception: {str(e)}")
            
        # Test 6: Admin login
        if self.admin_user_data:
            login_data = {
                "identifier": self.admin_user_data["username"],
                "password": self.admin_user_data["password"]
            }
            
            try:
                response = requests.post(f"{self.base_url}/auth/login", json=login_data)
                if response.status_code == 200:
                    token_data = response.json()
                    self.admin_token = token_data.get("access_token")
                    self.log_result("Admin Login", True, "Admin login successful")
                else:
                    self.log_result("Admin Login", False, f"Status: {response.status_code}, Error: {response.text}")
            except Exception as e:
                self.log_result("Admin Login", False, f"Exception: {str(e)}")
                
        return True

    def test_phone_otp_flow(self):
        """Test phone-based OTP authentication flow"""
        print("📱 Testing Phone OTP Flow")
        print("=" * 30)
        
        test_phone = "9876543210"
        
        # Test 7: OTP Generation
        try:
            response = requests.post(f"{self.base_url}/auth/phone-login", json={"phone": test_phone})
            if response.status_code == 200:
                otp_data = response.json()
                demo_otp = otp_data.get("demo_otp")
                self.log_result("OTP Generation", True, f"OTP generated: {demo_otp}")
                
                # Test 8: OTP Verification with correct OTP
                if demo_otp:
                    try:
                        response = requests.post(f"{self.base_url}/auth/phone-login", 
                                               json={"phone": test_phone, "otp": demo_otp})
                        if response.status_code == 200:
                            token_data = response.json()
                            self.log_result("OTP Verification (Correct)", True, "OTP verification successful")
                        else:
                            self.log_result("OTP Verification (Correct)", False, 
                                          f"Status: {response.status_code}, Error: {response.text}")
                    except Exception as e:
                        self.log_result("OTP Verification (Correct)", False, f"Exception: {str(e)}")
                        
                # Test 9: OTP Verification with incorrect OTP
                try:
                    response = requests.post(f"{self.base_url}/auth/phone-login", 
                                           json={"phone": test_phone, "otp": "000000"})
                    if response.status_code == 401:
                        self.log_result("OTP Verification (Incorrect)", True, "Correctly rejected invalid OTP")
                    else:
                        self.log_result("OTP Verification (Incorrect)", False, 
                                      f"Expected 401, got {response.status_code}")
                except Exception as e:
                    self.log_result("OTP Verification (Incorrect)", False, f"Exception: {str(e)}")
                    
            else:
                self.log_result("OTP Generation", False, f"Status: {response.status_code}, Error: {response.text}")
        except Exception as e:
            self.log_result("OTP Generation", False, f"Exception: {str(e)}")

    def test_password_reset_flow(self):
        """Test password reset flow"""
        print("🔄 Testing Password Reset Flow")
        print("=" * 35)
        
        if not self.test_user_data:
            self.log_result("Password Reset Tests", False, "No test user data available")
            return False
            
        # Test 10: Forgot password request
        try:
            response = requests.post(f"{self.base_url}/auth/forgot-password", 
                                   json={"email": self.test_user_data["email"]})
            if response.status_code == 200:
                reset_data = response.json()
                demo_token = reset_data.get("demo_token")
                self.log_result("Forgot Password Request", True, f"Reset token generated: {demo_token[:20]}...")
                
                # Test 11: Password reset with valid token
                if demo_token:
                    try:
                        response = requests.post(f"{self.base_url}/auth/reset-password", 
                                               json={"token": demo_token, "new_password": "NewSecurePass123!"})
                        if response.status_code == 200:
                            self.log_result("Password Reset (Valid Token)", True, "Password reset successful")
                        else:
                            self.log_result("Password Reset (Valid Token)", False, 
                                          f"Status: {response.status_code}, Error: {response.text}")
                    except Exception as e:
                        self.log_result("Password Reset (Valid Token)", False, f"Exception: {str(e)}")
                        
            else:
                self.log_result("Forgot Password Request", False, f"Status: {response.status_code}, Error: {response.text}")
        except Exception as e:
            self.log_result("Forgot Password Request", False, f"Exception: {str(e)}")
            
        # Test 12: Password reset with invalid token
        try:
            response = requests.post(f"{self.base_url}/auth/reset-password", 
                                   json={"token": "invalid_token_xyz", "new_password": "NewSecurePass123!"})
            if response.status_code == 400:
                self.log_result("Password Reset (Invalid Token)", True, "Correctly rejected invalid token")
            else:
                self.log_result("Password Reset (Invalid Token)", False, 
                              f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("Password Reset (Invalid Token)", False, f"Exception: {str(e)}")

    def test_token_validation_and_protected_endpoints(self):
        """Test JWT token validation and protected endpoints"""
        print("🛡️ Testing Token Validation and Protected Endpoints")
        print("=" * 55)
        
        # Test 13: Access protected endpoint with valid token
        if self.auth_token:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            try:
                response = requests.get(f"{self.base_url}/auth/me", headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    self.log_result("Protected Endpoint (Valid Token)", True, 
                                  f"User profile retrieved: {user_data.get('username')}")
                else:
                    self.log_result("Protected Endpoint (Valid Token)", False, 
                                  f"Status: {response.status_code}, Error: {response.text}")
            except Exception as e:
                self.log_result("Protected Endpoint (Valid Token)", False, f"Exception: {str(e)}")
        else:
            self.log_result("Protected Endpoint (Valid Token)", False, "No auth token available")
            
        # Test 14: Access protected endpoint with invalid token
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        try:
            response = requests.get(f"{self.base_url}/auth/me", headers=headers)
            if response.status_code == 401:
                self.log_result("Protected Endpoint (Invalid Token)", True, "Correctly rejected invalid token")
            else:
                self.log_result("Protected Endpoint (Invalid Token)", False, 
                              f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Protected Endpoint (Invalid Token)", False, f"Exception: {str(e)}")

    def test_user_management_with_authentication(self):
        """Test user management operations with role-based access control"""
        print("👥 Testing User Management with Authentication")
        print("=" * 50)
        
        # Test 15: Access users list without authentication
        try:
            response = requests.get(f"{self.base_url}/users")
            if response.status_code == 401:
                self.log_result("Users List (No Auth)", True, "Correctly rejected unauthenticated request")
            else:
                self.log_result("Users List (No Auth)", False, 
                              f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Users List (No Auth)", False, f"Exception: {str(e)}")
            
        # Test 16: Access users list with employee token (should fail)
        if self.auth_token:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            try:
                response = requests.get(f"{self.base_url}/users", headers=headers)
                if response.status_code == 403:
                    self.log_result("Users List (Employee Role)", True, "Correctly rejected insufficient permissions")
                else:
                    self.log_result("Users List (Employee Role)", False, 
                                  f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_result("Users List (Employee Role)", False, f"Exception: {str(e)}")
        else:
            self.log_result("Users List (Employee Role)", False, "No employee auth token available")
            
        # Test 17: Access users list with admin token (should succeed)
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            try:
                response = requests.get(f"{self.base_url}/users", headers=headers)
                if response.status_code == 200:
                    users_data = response.json()
                    self.log_result("Users List (Admin Role)", True, 
                                  f"Successfully retrieved {len(users_data)} users")
                else:
                    self.log_result("Users List (Admin Role)", False, 
                                  f"Status: {response.status_code}, Error: {response.text}")
            except Exception as e:
                self.log_result("Users List (Admin Role)", False, f"Exception: {str(e)}")
        else:
            self.log_result("Users List (Admin Role)", False, "No admin auth token available")
            
        # Test 18: Create user with admin token
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
            new_user_data = {
                "username": f"newuser{int(time.time())}",
                "email": f"newuser{int(time.time())}@example.com",
                "phone": f"987656{str(int(time.time()))[-4:]}",
                "full_name": "New Test User",
                "role": "Employee",
                "password": "SecurePass123!",
                "department": "Marketing"
            }
            
            try:
                response = requests.post(f"{self.base_url}/users", json=new_user_data, headers=headers)
                if response.status_code in [200, 201]:
                    user_response = response.json()
                    self.log_result("Create User (Admin)", True, 
                                  f"User created with ID: {user_response.get('id')}")
                else:
                    self.log_result("Create User (Admin)", False, 
                                  f"Status: {response.status_code}, Error: {response.text}")
            except Exception as e:
                self.log_result("Create User (Admin)", False, f"Exception: {str(e)}")
        else:
            self.log_result("Create User (Admin)", False, "No admin auth token available")

    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting Comprehensive Authentication System Tests")
        print("=" * 70)
        print()
        
        # Run all test suites
        self.test_user_registration_and_login_flow()
        self.test_login_endpoints()
        self.test_phone_otp_flow()
        self.test_password_reset_flow()
        self.test_token_validation_and_protected_endpoints()
        self.test_user_management_with_authentication()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
            print()
            
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        print()
        
        # Critical issues analysis
        critical_issues = []
        for result in self.test_results:
            if not result["success"]:
                if "OTP" in result["test"]:
                    critical_issues.append("Phone-based OTP authentication has issues")
                elif "Password Reset" in result["test"] and "Valid Token" in result["test"]:
                    critical_issues.append("Password reset flow with valid tokens failing")
                elif "Admin" in result["test"] and "Role" in result["test"]:
                    critical_issues.append("Role-based access control issues")
                elif "Login" in result["test"]:
                    critical_issues.append("Login endpoint issues")
                    
        if critical_issues:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in set(critical_issues):
                print(f"  • {issue}")
        else:
            print("🎉 No critical authentication issues found!")

if __name__ == "__main__":
    tester = AuthenticationTester()
    tester.run_all_tests()