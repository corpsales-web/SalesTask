import requests
import sys
import json
from datetime import datetime, timezone
import uuid

class AavanaGreensCRMTester:
    def __init__(self, base_url="https://aavana-ai-hub.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_leads = []
        self.created_tasks = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 200:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health check"""
        return self.run_test("Health Check", "GET", "", 200)

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        return self.run_test("Dashboard Stats", "GET", "dashboard/stats", 200)

    def test_create_lead(self, lead_data):
        """Test creating a new lead"""
        success, response = self.run_test("Create Lead", "POST", "leads", 200, data=lead_data)
        if success and 'id' in response:
            self.created_leads.append(response['id'])
            return True, response
        return False, {}

    def test_get_leads(self):
        """Test getting all leads"""
        return self.run_test("Get All Leads", "GET", "leads", 200)

    def test_get_lead_by_id(self, lead_id):
        """Test getting a specific lead"""
        return self.run_test("Get Lead by ID", "GET", f"leads/{lead_id}", 200)

    def test_update_lead(self, lead_id, update_data):
        """Test updating a lead"""
        return self.run_test("Update Lead", "PUT", f"leads/{lead_id}", 200, data=update_data)

    def test_delete_lead(self, lead_id):
        """Test deleting a lead"""
        return self.run_test("Delete Lead", "DELETE", f"leads/{lead_id}", 200)

    def test_create_task(self, task_data):
        """Test creating a new task"""
        success, response = self.run_test("Create Task", "POST", "tasks", 200, data=task_data)
        if success and 'id' in response:
            self.created_tasks.append(response['id'])
            return True, response
        return False, {}

    def test_get_tasks(self):
        """Test getting all tasks"""
        return self.run_test("Get All Tasks", "GET", "tasks", 200)

    def test_update_task(self, task_id, update_data):
        """Test updating a task"""
        return self.run_test("Update Task", "PUT", f"tasks/{task_id}", 200, data=update_data)

    # Aavana 2.0 Orchestration Tests
    def test_aavana_health_check(self):
        """Test Aavana 2.0 health check endpoint"""
        return self.run_test("Aavana 2.0 Health Check", "GET", "aavana/health", 200)

    def test_aavana_conversation_english(self):
        """Test Aavana 2.0 conversation processing with English message"""
        data = {
            "message": "Hello, I need help with plants",
            "channel": "in_app_chat",
            "user_id": "test_user_001",
            "language": "en"
        }
        return self.run_test("Aavana 2.0 Conversation (English)", "POST", "aavana/conversation", 200, data=data)

    def test_aavana_conversation_hindi(self):
        """Test Aavana 2.0 conversation processing with Hindi message"""
        data = {
            "message": "नमस्ते, मुझे पौधों की जानकारी चाहिए",
            "channel": "in_app_chat", 
            "user_id": "test_user_002",
            "language": "hi"
        }
        return self.run_test("Aavana 2.0 Conversation (Hindi)", "POST", "aavana/conversation", 200, data=data)

    def test_aavana_conversation_hinglish(self):
        """Test Aavana 2.0 conversation processing with Hinglish message"""
        data = {
            "message": "kya haal hai, garden ke liye help chahiye",
            "channel": "in_app_chat",
            "user_id": "test_user_003", 
            "language": "hinglish"
        }
        return self.run_test("Aavana 2.0 Conversation (Hinglish)", "POST", "aavana/conversation", 200, data=data)

    def test_aavana_language_detect_english(self):
        """Test Aavana 2.0 language detection with English text"""
        data = {"text": "Hello, how are you today?"}
        return self.run_test("Aavana 2.0 Language Detection (English)", "POST", "aavana/language-detect", 200, data=data)

    def test_aavana_language_detect_hindi(self):
        """Test Aavana 2.0 language detection with Hindi text"""
        data = {"text": "नमस्ते, आप कैसे हैं?"}
        return self.run_test("Aavana 2.0 Language Detection (Hindi)", "POST", "aavana/language-detect", 200, data=data)

    def test_aavana_language_detect_hinglish(self):
        """Test Aavana 2.0 language detection with Hinglish text"""
        data = {"text": "Hello yaar, kya chal raha hai?"}
        return self.run_test("Aavana 2.0 Language Detection (Hinglish)", "POST", "aavana/language-detect", 200, data=data)

    def test_aavana_audio_templates_english(self):
        """Test Aavana 2.0 audio templates for English"""
        return self.run_test("Aavana 2.0 Audio Templates (English)", "GET", "aavana/audio-templates", 200, params={"language": "en"})

    def test_aavana_audio_templates_hindi(self):
        """Test Aavana 2.0 audio templates for Hindi"""
        return self.run_test("Aavana 2.0 Audio Templates (Hindi)", "GET", "aavana/audio-templates", 200, params={"language": "hi"})

    def test_aavana_audio_templates_hinglish(self):
        """Test Aavana 2.0 audio templates for Hinglish"""
        return self.run_test("Aavana 2.0 Audio Templates (Hinglish)", "GET", "aavana/audio-templates", 200, params={"language": "hinglish"})

    def test_aavana_whatsapp_integration(self):
        """Test Aavana 2.0 WhatsApp integration with mock data"""
        mock_whatsapp_data = {
            "from": "919876543210",
            "id": "wamid.test123",
            "text": {
                "body": "Hi, I want to know about your garden services"
            },
            "timestamp": "1640995200"
        }
        return self.run_test("Aavana 2.0 WhatsApp Integration", "POST", "aavana/whatsapp", 200, data=mock_whatsapp_data)

    # Admin Panel Authentication Tests
    def test_user_registration_valid(self):
        """Test user registration with valid data"""
        user_data = {
            "username": "testuser123",
            "email": "testuser@example.com",
            "phone": "9876543210",
            "full_name": "Test User",
            "role": "Employee",
            "password": "SecurePass123!",
            "department": "Sales"
        }
        success, response = self.run_test("User Registration (Valid)", "POST", "auth/register", 200, data=user_data)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            self.test_user_id = response.get('user', {}).get('id')
            return True, response
        return False, {}

    def test_user_registration_duplicate(self):
        """Test user registration with duplicate username/email"""
        user_data = {
            "username": "testuser123",  # Same as above
            "email": "testuser@example.com",  # Same as above
            "phone": "9876543211",
            "full_name": "Duplicate User",
            "role": "Employee",
            "password": "SecurePass123!"
        }
        return self.run_test("User Registration (Duplicate)", "POST", "auth/register", 400, data=user_data)

    def test_user_registration_invalid_email(self):
        """Test user registration with invalid email format"""
        user_data = {
            "username": "testuser456",
            "email": "invalid-email-format",
            "phone": "9876543212",
            "full_name": "Invalid Email User",
            "role": "Employee",
            "password": "SecurePass123!"
        }
        return self.run_test("User Registration (Invalid Email)", "POST", "auth/register", 422, data=user_data)

    def test_user_registration_missing_fields(self):
        """Test user registration with missing required fields"""
        user_data = {
            "username": "testuser789",
            # Missing email, full_name, password
            "phone": "9876543213",
            "role": "Employee"
        }
        return self.run_test("User Registration (Missing Fields)", "POST", "auth/register", 422, data=user_data)

    def test_user_login_username(self):
        """Test user login with username/password"""
        login_data = {
            "identifier": "testuser123",
            "password": "SecurePass123!"
        }
        success, response = self.run_test("User Login (Username)", "POST", "auth/login", 200, data=login_data)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            return True, response
        return False, {}

    def test_user_login_email(self):
        """Test user login with email/password"""
        login_data = {
            "identifier": "testuser@example.com",
            "password": "SecurePass123!"
        }
        success, response = self.run_test("User Login (Email)", "POST", "auth/login", 200, data=login_data)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            return True, response
        return False, {}

    def test_user_login_phone(self):
        """Test user login with phone/password"""
        login_data = {
            "identifier": "9876543210",
            "password": "SecurePass123!"
        }
        success, response = self.run_test("User Login (Phone)", "POST", "auth/login", 200, data=login_data)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            return True, response
        return False, {}

    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials"""
        login_data = {
            "identifier": "testuser123",
            "password": "WrongPassword123!"
        }
        return self.run_test("User Login (Invalid Credentials)", "POST", "auth/login", 401, data=login_data)

    def test_phone_login_otp_generation(self):
        """Test phone-based login OTP generation"""
        phone_data = {
            "phone": "9876543210"
            # No OTP field - should generate OTP
        }
        return self.run_test("Phone Login (OTP Generation)", "POST", "auth/phone-login", 200, data=phone_data)

    def test_phone_login_otp_verification(self):
        """Test phone-based login OTP verification"""
        phone_data = {
            "phone": "9876543210",
            "otp": "123456"  # Mock OTP
        }
        return self.run_test("Phone Login (OTP Verification)", "POST", "auth/phone-login", 200, data=phone_data)

    def test_phone_login_invalid_otp(self):
        """Test phone-based login with invalid OTP"""
        phone_data = {
            "phone": "9876543210",
            "otp": "000000"  # Invalid OTP
        }
        return self.run_test("Phone Login (Invalid OTP)", "POST", "auth/phone-login", 400, data=phone_data)

    def test_forgot_password_request(self):
        """Test forgot password request"""
        forgot_data = {
            "email": "testuser@example.com"
        }
        return self.run_test("Forgot Password Request", "POST", "auth/forgot-password", 200, data=forgot_data)

    def test_reset_password_valid_token(self):
        """Test reset password with valid token"""
        reset_data = {
            "token": "mock_reset_token_123",
            "new_password": "NewSecurePass123!"
        }
        return self.run_test("Reset Password (Valid Token)", "POST", "auth/reset-password", 200, data=reset_data)

    def test_reset_password_invalid_token(self):
        """Test reset password with invalid/expired token"""
        reset_data = {
            "token": "invalid_token_xyz",
            "new_password": "NewSecurePass123!"
        }
        return self.run_test("Reset Password (Invalid Token)", "POST", "auth/reset-password", 400, data=reset_data)

    def test_get_current_user_valid_token(self):
        """Test getting current user profile with valid token"""
        if not hasattr(self, 'auth_token'):
            print("⚠️ Skipping test - no auth token available")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        url = f"{self.base_url}/auth/me"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Get Current User (Valid Token)...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers)
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: User profile retrieved")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_get_current_user_invalid_token(self):
        """Test getting current user profile with invalid token"""
        headers = {'Authorization': 'Bearer invalid_token_xyz'}
        url = f"{self.base_url}/auth/me"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Get Current User (Invalid Token)...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers)
            success = response.status_code == 401
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return True, {}
            else:
                print(f"❌ Failed - Expected 401, got {response.status_code}")
                return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_get_users_list(self):
        """Test getting users list (requires authentication)"""
        if not hasattr(self, 'auth_token'):
            print("⚠️ Skipping test - no auth token available")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        url = f"{self.base_url}/users"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Get Users List...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers)
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: List with {len(response_data)} users")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_create_user_admin(self):
        """Test creating new user (admin only)"""
        if not hasattr(self, 'auth_token'):
            print("⚠️ Skipping test - no auth token available")
            return False, {}
        
        user_data = {
            "username": "newemployee123",
            "email": "newemployee@example.com",
            "phone": "9876543214",
            "full_name": "New Employee",
            "role": "Employee",
            "password": "SecurePass123!",
            "department": "Marketing"
        }
        
        headers = {'Authorization': f'Bearer {self.auth_token}', 'Content-Type': 'application/json'}
        url = f"{self.base_url}/users"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Create User (Admin)...")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, json=user_data, headers=headers)
            success = response.status_code in [200, 201]
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if 'id' in response_data:
                        self.created_user_id = response_data['id']
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected 200/201, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_update_user(self):
        """Test updating user information"""
        if not hasattr(self, 'auth_token') or not hasattr(self, 'created_user_id'):
            print("⚠️ Skipping test - no auth token or user ID available")
            return False, {}
        
        update_data = {
            "full_name": "Updated Employee Name",
            "department": "Sales",
            "status": "Active"
        }
        
        headers = {'Authorization': f'Bearer {self.auth_token}', 'Content-Type': 'application/json'}
        url = f"{self.base_url}/users/{self.created_user_id}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Update User...")
        print(f"   URL: {url}")
        
        try:
            response = requests.put(url, json=update_data, headers=headers)
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return True, {}
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_delete_user_admin(self):
        """Test deleting user (admin only)"""
        if not hasattr(self, 'auth_token') or not hasattr(self, 'created_user_id'):
            print("⚠️ Skipping test - no auth token or user ID available")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        url = f"{self.base_url}/users/{self.created_user_id}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Delete User (Admin)...")
        print(f"   URL: {url}")
        
        try:
            response = requests.delete(url, headers=headers)
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return True, {}
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_unauthorized_access(self):
        """Test accessing protected endpoints without authentication"""
        return self.run_test("Unauthorized Access to Users", "GET", "users", 401)

def main():
    print("🚀 Starting Aavana Greens CRM API Tests")
    print("=" * 50)
    
    tester = AavanaGreensCRMTester()

    # Test 1: Health Check
    success, _ = tester.test_health_check()
    if not success:
        print("❌ Health check failed, stopping tests")
        return 1

    # Test 2: Dashboard Stats (initial state)
    print("\n📊 Testing Dashboard Stats...")
    tester.test_dashboard_stats()

    # Test 3: Create multiple leads with different data
    print("\n👥 Testing Lead Management...")
    
    test_leads = [
        {
            "name": "Rajesh Kumar",
            "phone": "9876543210",
            "email": "rajesh@example.com",
            "budget": 500000,
            "space_size": "2 BHK",
            "location": "Bangalore",
            "notes": "Interested in green building features",
            "tags": ["premium", "eco-friendly"],
            "assigned_to": "Sales Team A"
        },
        {
            "name": "Priya Sharma",
            "phone": "8765432109",
            "email": "priya@example.com",
            "budget": 750000,
            "space_size": "3 BHK",
            "location": "Mumbai",
            "notes": "Looking for immediate possession",
            "tags": ["urgent", "high-value"],
            "assigned_to": "Sales Team B"
        },
        {
            "name": "Amit Patel",
            "phone": "7654321098",
            "budget": 300000,
            "location": "Pune",
            "notes": "First-time buyer, needs guidance"
        }
    ]

    created_lead_ids = []
    for i, lead_data in enumerate(test_leads):
        success, response = tester.test_create_lead(lead_data)
        if success:
            created_lead_ids.append(response['id'])

    # Test 4: Get all leads
    tester.test_get_leads()

    # Test 5: Get specific lead
    if created_lead_ids:
        tester.test_get_lead_by_id(created_lead_ids[0])

    # Test 6: Update lead status (simulate pipeline progression)
    if created_lead_ids:
        print("\n🔄 Testing Lead Status Updates...")
        statuses = ["Qualified", "Proposal", "Negotiation", "Won"]
        
        for i, status in enumerate(statuses):
            if i < len(created_lead_ids):
                tester.test_update_lead(created_lead_ids[i], {"status": status})

    # Test 7: Create tasks
    print("\n📋 Testing Task Management...")
    
    test_tasks = [
        {
            "title": "Follow up with Rajesh Kumar",
            "description": "Call to discuss green building features and pricing",
            "priority": "High",
            "assigned_to": "Sales Team A",
            "lead_id": created_lead_ids[0] if created_lead_ids else None,
            "due_date": "2024-12-31T10:00:00Z"
        },
        {
            "title": "Prepare proposal for Priya Sharma",
            "description": "Create detailed proposal with floor plans",
            "priority": "Urgent",
            "assigned_to": "Sales Team B",
            "lead_id": created_lead_ids[1] if len(created_lead_ids) > 1 else None,
            "due_date": "2024-12-30T15:00:00Z"
        },
        {
            "title": "Site visit coordination",
            "description": "Arrange site visit for interested customers",
            "priority": "Medium",
            "assigned_to": "Operations Team"
        }
    ]

    created_task_ids = []
    for task_data in test_tasks:
        success, response = tester.test_create_task(task_data)
        if success:
            created_task_ids.append(response['id'])

    # Test 8: Get all tasks
    tester.test_get_tasks()

    # Test 9: Update task status
    if created_task_ids:
        print("\n✅ Testing Task Status Updates...")
        tester.test_update_task(created_task_ids[0], {"status": "In Progress"})
        if len(created_task_ids) > 1:
            tester.test_update_task(created_task_ids[1], {"status": "Completed"})

    # Test 10: Dashboard stats after changes
    print("\n📊 Testing Dashboard Stats After Changes...")
    tester.test_dashboard_stats()

    # Test 11: Error handling - invalid lead ID
    print("\n🚫 Testing Error Handling...")
    tester.run_test("Get Invalid Lead", "GET", "leads/invalid-id", 404)

    # Test 12: Delete a lead
    if created_lead_ids:
        print("\n🗑️ Testing Lead Deletion...")
        tester.test_delete_lead(created_lead_ids[-1])

    # Final Results
    print("\n" + "=" * 50)
    print(f"📊 FINAL TEST RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the backend implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())