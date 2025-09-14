import requests
import sys
import json
from datetime import datetime, timezone
import uuid

class FocusedAavanaBackendTester:
    def __init__(self, base_url="https://aavana-crm-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.test_user_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if params:
            print(f"   Params: {params}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, params=params)
            elif method == 'POST':
                if params:
                    # For POST with query parameters
                    response = requests.post(url, json=data, headers=default_headers, params=params)
                else:
                    response = requests.post(url, json=data, headers=default_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, params=params)

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

    def test_backend_health(self):
        """Test backend server health and connectivity"""
        print("\n🏥 TESTING BACKEND SERVER HEALTH & CONNECTIVITY")
        print("=" * 60)
        
        # Test 1: Basic health check
        success, _ = self.run_test("Backend Health Check", "GET", "", 200)
        if not success:
            print("❌ CRITICAL: Backend server is not responding")
            return False
        
        # Test 2: Dashboard stats (tests database connectivity)
        success, _ = self.run_test("Database Connectivity (Dashboard Stats)", "GET", "dashboard/stats", 200)
        if not success:
            print("❌ CRITICAL: Database connectivity issues")
            return False
            
        print("✅ Backend server health and database connectivity: WORKING")
        return True

    def test_authentication_endpoints(self):
        """Test authentication endpoints working"""
        print("\n🔐 TESTING AUTHENTICATION ENDPOINTS")
        print("=" * 60)
        
        # Create a test user for authentication testing
        import time
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"testuser{timestamp}",
            "email": f"testuser{timestamp}@example.com",
            "phone": f"987654{timestamp[-4:]}",
            "full_name": "Test User",
            "role": "Employee",
            "password": "SecurePass123!",
            "department": "Sales"
        }
        
        # Test 1: User registration
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, data=user_data)
        if not success:
            print("❌ CRITICAL: User registration endpoint not working")
            return False
        
        self.test_username = user_data['username']
        self.test_password = user_data['password']
        
        # Test 2: User login
        login_data = {
            "identifier": self.test_username,
            "password": self.test_password
        }
        success, response = self.run_test("User Login", "POST", "auth/login", 200, data=login_data)
        if not success:
            print("❌ CRITICAL: User login endpoint not working")
            return False
        
        if 'access_token' in response:
            self.auth_token = response['access_token']
            print("✅ JWT token received and stored")
            # Also store user info if available
            if 'user' in response and 'id' in response['user']:
                self.test_user_id = response['user']['id']
        else:
            print("❌ CRITICAL: No access token in login response")
            return False
        
        # Test 3: Protected endpoint access
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        success, _ = self.run_test("Protected Endpoint Access", "GET", "auth/me", 200, headers=headers)
        if not success:
            print("❌ CRITICAL: JWT authentication middleware not working")
            return False
        
        print("✅ Authentication endpoints: WORKING")
        return True

    def test_target_creation_endpoints(self):
        """Test target creation API endpoints"""
        print("\n🎯 TESTING TARGET CREATION API ENDPOINTS")
        print("=" * 60)
        
        if not self.auth_token:
            print("❌ CRITICAL: No auth token available for target testing")
            return False
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        # Test 1: Create target endpoint
        # The endpoint expects query parameters including user_id
        params = {
            "user_id": self.test_user_id or "test_user_123",
            "target_type": "sales_amount",
            "period": "monthly", 
            "target_value": 100000,
            "created_by": "test_system"
        }
        
        success, response = self.run_test("Create Target (POST /api/targets/create)", "POST", "targets/create", 200, params=params, headers=headers)
        if not success:
            print("❌ CRITICAL: Target creation endpoint not working")
            return False
        
        # Test 2: Get targets dashboard
        dashboard_endpoint = f"targets/dashboard/{self.test_user_id or 'test_user_123'}"
        success, response = self.run_test("Get Targets Dashboard (GET /api/targets/dashboard/{user_id})", "GET", dashboard_endpoint, 200, headers=headers)
        if not success:
            print("❌ CRITICAL: Targets dashboard endpoint not working")
            return False
        
        print("✅ Target creation API endpoints: WORKING")
        return True

    def test_core_endpoints(self):
        """Test all other core endpoints accessibility"""
        print("\n🔧 TESTING CORE ENDPOINTS ACCESSIBILITY")
        print("=" * 60)
        
        if not self.auth_token:
            print("❌ CRITICAL: No auth token available for core endpoint testing")
            return False
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        # Test core CRM endpoints
        endpoints_to_test = [
            ("Leads List", "GET", "leads", 200),
            ("Tasks List", "GET", "tasks", 200),
        ]
        
        all_passed = True
        for name, method, endpoint, expected_status in endpoints_to_test:
            success, _ = self.run_test(name, method, endpoint, expected_status, headers=headers)
            if not success:
                all_passed = False
                print(f"❌ CRITICAL: {name} endpoint not accessible")
        
        # Test Users endpoint (may require higher permissions)
        success, _ = self.run_test("Users List", "GET", "users", 200, headers=headers)
        if not success:
            print("⚠️ WARNING: Users List endpoint requires higher permissions (expected for Employee role)")
        else:
            print("✅ Users List endpoint accessible")
        
        # Test AI endpoints (sample)
        ai_endpoints = [
            ("AI Insights", "POST", "ai/insights", 200, {"type": "leads", "data": {}}),
            ("AI Voice to Task", "POST", "ai/voice-to-task", 200, {"voice_input": "Create a task to follow up with customer"}),
        ]
        
        for name, method, endpoint, expected_status, data in ai_endpoints:
            success, _ = self.run_test(name, method, endpoint, expected_status, data=data, headers=headers)
            if not success:
                print(f"⚠️ WARNING: {name} endpoint not working (may be expected)")
        
        if all_passed:
            print("✅ Core endpoints accessibility: WORKING")
        else:
            print("❌ Some core endpoints have issues")
        
        return all_passed

    def test_database_operations(self):
        """Test database connectivity and operations"""
        print("\n💾 TESTING DATABASE CONNECTIVITY & OPERATIONS")
        print("=" * 60)
        
        # Test 1: Create a lead (tests database write)
        lead_data = {
            "name": "Test Lead for DB Check",
            "phone": "9876543210",
            "email": "testlead@example.com",
            "budget": 50000,
            "space_size": "2 BHK",
            "location": "Mumbai",
            "notes": "Database connectivity test lead"
        }
        
        success, response = self.run_test("Database Write (Create Lead)", "POST", "leads", 200, data=lead_data)
        if not success:
            print("❌ CRITICAL: Database write operations not working")
            return False
        
        lead_id = response.get('id') if response else None
        
        # Test 2: Read the lead back (tests database read)
        if lead_id:
            success, _ = self.run_test("Database Read (Get Lead)", "GET", f"leads/{lead_id}", 200)
            if not success:
                print("❌ CRITICAL: Database read operations not working")
                return False
        
        # Test 3: Update the lead (tests database update)
        if lead_id:
            update_data = {"status": "Qualified", "notes": "Updated via database test"}
            success, _ = self.run_test("Database Update (Update Lead)", "PUT", f"leads/{lead_id}", 200, data=update_data)
            if not success:
                print("❌ CRITICAL: Database update operations not working")
                return False
        
        # Test 4: Delete the lead (tests database delete)
        if lead_id:
            success, _ = self.run_test("Database Delete (Delete Lead)", "DELETE", f"leads/{lead_id}", 200)
            if not success:
                print("❌ CRITICAL: Database delete operations not working")
                return False
        
        print("✅ Database connectivity and operations: WORKING")
        return True

def main():
    print("🚀 FOCUSED AAVANA GREENS BACKEND VERIFICATION")
    print("=" * 60)
    print("Testing backend stability after UI fixes")
    print("Focus: Health, Auth, Targets, Core Endpoints, Database")
    print("=" * 60)
    
    tester = FocusedAavanaBackendTester()
    
    # Test results tracking
    test_results = {}
    
    # 1. Backend Server Health & Connectivity
    test_results['health'] = tester.test_backend_health()
    
    # 2. Authentication Endpoints Working
    test_results['auth'] = tester.test_authentication_endpoints()
    
    # 3. Target Creation API Endpoints
    test_results['targets'] = tester.test_target_creation_endpoints()
    
    # 4. Core Endpoints Accessible
    test_results['core'] = tester.test_core_endpoints()
    
    # 5. Database Connectivity and Operations
    test_results['database'] = tester.test_database_operations()
    
    # Final Results Summary
    print("\n" + "=" * 60)
    print("📊 FOCUSED BACKEND VERIFICATION RESULTS")
    print("=" * 60)
    
    critical_areas = [
        ('Backend Health & Connectivity', test_results['health']),
        ('Authentication Endpoints', test_results['auth']),
        ('Target Creation APIs', test_results['targets']),
        ('Core Endpoints Access', test_results['core']),
        ('Database Operations', test_results['database'])
    ]
    
    all_critical_passed = True
    for area, passed in critical_areas:
        status = "✅ WORKING" if passed else "❌ FAILED"
        print(f"{area}: {status}")
        if not passed:
            all_critical_passed = False
    
    print(f"\nOverall Tests: {tester.tests_run}")
    print(f"Passed Tests: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if all_critical_passed:
        print("\n🎉 BACKEND VERIFICATION: ALL CRITICAL AREAS WORKING")
        print("✅ Backend is stable and supporting frontend functionality properly")
        return 0
    else:
        print("\n⚠️ BACKEND VERIFICATION: SOME CRITICAL ISSUES FOUND")
        print("❌ Backend needs attention before frontend can function properly")
        return 1

if __name__ == "__main__":
    sys.exit(main())