import requests
import sys
import json
from datetime import datetime, timezone
import uuid

class FocusedAITester:
    def __init__(self, base_url="https://greenstack-ai.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=10):
        """Run a single API test with timeout"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

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
                    else:
                        print(f"   Response: Data received successfully")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text[:200]}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"⏰ Timeout - Request took longer than {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("🏥 BASIC API HEALTH CHECKS")
        print("-" * 40)
        
        # Health check
        self.run_test("API Health Check", "GET", "", 200)
        
        # Dashboard stats
        self.run_test("Dashboard Statistics", "GET", "dashboard/stats", 200)
        
        # Core CRM endpoints
        self.run_test("Get Leads", "GET", "leads", 200)
        self.run_test("Get Tasks", "GET", "tasks", 200)

    def test_ai_endpoints_basic(self):
        """Test AI endpoints with basic requests"""
        print("\n🤖 AI ENDPOINTS - BASIC TESTS")
        print("-" * 40)
        
        # Test AI generate with simple prompt
        simple_data = {
            "prompt": "Hello, test AI response",
            "provider": "openai",
            "model": "gpt-5",
            "temperature": 0.7
        }
        self.run_test("AI Generate - Simple", "POST", "ai/generate", 200, data=simple_data, timeout=30)
        
        # Test conversation analysis
        conv_data = {
            "conversation": [
                {"speaker": "customer", "message": "Hi, I need help"},
                {"speaker": "agent", "message": "How can I help you?"}
            ]
        }
        self.run_test("AI Conversation Analysis", "POST", "ai/analyze-conversation", 200, data=conv_data, timeout=20)

    def test_hrms_endpoints(self):
        """Test HRMS endpoints"""
        print("\n👤 HRMS API TESTS")
        print("-" * 40)
        
        # GPS check-in (simpler than face check-in)
        gps_data = {
            "employee_id": "emp_test_001",
            "location": {
                "latitude": 19.0760,
                "longitude": 72.8777,
                "accuracy": 10
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "check_type": "check_in"
        }
        self.run_test("HRMS GPS Check-in", "POST", "hrms/gps-checkin", 200, data=gps_data)

    def test_workflow_endpoints(self):
        """Test workflow endpoints"""
        print("\n⚙️ WORKFLOW API TESTS")
        print("-" * 40)
        
        # Get workflow templates
        self.run_test("Get Workflow Templates", "GET", "workflow-templates", 200)

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 AUTHENTICATION TESTS")
        print("-" * 40)
        
        # Test login with demo credentials
        login_data = {
            "identifier": "admin",
            "password": "admin123"
        }
        self.run_test("Admin Login", "POST", "auth/login", 200, data=login_data)

def main():
    print("🚀 Starting Focused AI Backend Testing")
    print("🎯 Focus: Critical endpoints verification")
    print("="*60)
    
    tester = FocusedAITester()
    
    # Run focused tests
    tester.test_basic_endpoints()
    tester.test_ai_endpoints_basic()
    tester.test_hrms_endpoints()
    tester.test_workflow_endpoints()
    tester.test_auth_endpoints()
    
    # Results
    print("\n" + "="*60)
    print(f"📊 FOCUSED TEST RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    success_rate = (tester.tests_passed/tester.tests_run*100) if tester.tests_run > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 70:
        print("🎉 Backend is responding well!")
        return 0
    else:
        print("⚠️ Backend has issues that need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())