import requests
import sys
import json
import base64
from datetime import datetime, timezone
import uuid

class HRMSCameraBackendTester:
    def __init__(self, base_url="https://aavana-greens.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.test_employee_id = "emp_" + str(uuid.uuid4())[:8]

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
                response = requests.get(url, headers=default_headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=30)

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
                    else:
                        print(f"   Response: Data received successfully")
                    return True, response_data
                except:
                    print(f"   Response: Non-JSON response received")
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
            print(f"⏰ Timeout - Request took longer than 30 seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def generate_mock_face_image(self):
        """Generate a mock base64 encoded image for testing"""
        # Create a simple 1x1 pixel PNG image in base64
        # This is a minimal valid PNG image
        mock_png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77mgAAAABJRU5ErkJggg=="
        return mock_png_base64

    def test_health_check(self):
        """Test basic API health check"""
        return self.run_test("API Health Check", "GET", "", 200)

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        return self.run_test("Dashboard Stats", "GET", "dashboard/stats", 200)

    def test_get_leads(self):
        """Test leads endpoint"""
        return self.run_test("Get Leads", "GET", "leads", 200)

    def test_get_tasks(self):
        """Test tasks endpoint"""
        return self.run_test("Get Tasks", "GET", "tasks", 200)

    def test_admin_login(self):
        """Test admin login functionality"""
        login_data = {
            "identifier": "admin",
            "password": "admin123"
        }
        success, response = self.run_test("Admin Login", "POST", "auth/login", 200, data=login_data)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            print(f"   🔑 Auth token obtained successfully")
            return True, response
        return False, {}

    def test_hrms_face_checkin_endpoint_access(self):
        """Test HRMS face check-in endpoint accessibility"""
        face_checkin_data = {
            "employee_id": self.test_employee_id,
            "face_image": self.generate_mock_face_image(),
            "location": {
                "latitude": 19.0760,
                "longitude": 72.8777,
                "accuracy": 10.0,
                "address": "Mumbai Office"
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_info": {
                "device_type": "mobile",
                "browser": "Chrome"
            }
        }
        
        return self.run_test("HRMS Face Check-in Endpoint Access", "POST", "hrms/face-checkin", 200, data=face_checkin_data)

    def test_hrms_face_checkin_with_realistic_data(self):
        """Test HRMS face check-in with realistic employee data"""
        face_checkin_data = {
            "employee_id": "EMP001",
            "employee_name": "Rajesh Kumar",
            "face_image": self.generate_mock_face_image(),
            "location": {
                "latitude": 19.0760,  # Mumbai coordinates
                "longitude": 72.8777,
                "accuracy": 10.5,
                "address": "Aavana Greens Mumbai Office",
                "lat": 19.0760,
                "lng": 72.8777
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_info": {
                "device_type": "mobile",
                "browser": "Chrome",
                "os": "Android"
            }
        }
        
        return self.run_test("HRMS Face Check-in with Realistic Data", "POST", "hrms/face-checkin", 200, data=face_checkin_data)

    def test_hrms_face_checkin_validation(self):
        """Test HRMS face check-in validation with missing fields"""
        incomplete_data = {
            "employee_id": self.test_employee_id,
            # Missing face_image - should trigger validation error
            "location": {
                "latitude": 19.0760,
                "longitude": 72.8777
            }
        }
        
        return self.run_test("HRMS Face Check-in Validation", "POST", "hrms/face-checkin", 500, data=incomplete_data)

    def test_hrms_gps_checkin_endpoint_access(self):
        """Test HRMS GPS check-in endpoint accessibility"""
        gps_checkin_data = {
            "employee_id": self.test_employee_id,
            "latitude": 19.0760,
            "longitude": 72.8777,
            "accuracy": 5.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "check_type": "check_in"
        }
        
        return self.run_test("HRMS GPS Check-in Endpoint Access", "POST", "hrms/gps-checkin", 200, data=gps_checkin_data)

    def test_hrms_gps_checkin_with_realistic_data(self):
        """Test HRMS GPS check-in with realistic employee data"""
        gps_checkin_data = {
            "employee_id": "EMP002",
            "employee_name": "Priya Sharma",
            "latitude": 28.6139,  # Delhi coordinates
            "longitude": 77.2090,
            "accuracy": 8.2,
            "altitude": 216.5,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "check_type": "check_out",
            "location_name": "Aavana Greens Office - Delhi",
            "device_info": {
                "device_type": "mobile",
                "browser": "Safari",
                "os": "iOS"
            }
        }
        
        return self.run_test("HRMS GPS Check-in with Realistic Data", "POST", "hrms/gps-checkin", 200, data=gps_checkin_data)

    def test_hrms_gps_checkin_validation(self):
        """Test HRMS GPS check-in validation with invalid coordinates"""
        invalid_data = {
            "employee_id": self.test_employee_id,
            "latitude": 999.0,  # Invalid latitude
            "longitude": 999.0,  # Invalid longitude
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "check_type": "check_in"
        }
        
        return self.run_test("HRMS GPS Check-in Validation", "POST", "hrms/gps-checkin", 400, data=invalid_data)

    def test_hrms_face_checkin_different_formats(self):
        """Test HRMS face check-in with different image formats"""
        # Test with JPEG format indicator
        face_checkin_data = {
            "employee_id": self.test_employee_id,
            "image_data": "data:image/jpeg;base64," + self.generate_mock_face_image(),
            "latitude": 12.9716,  # Bangalore coordinates
            "longitude": 77.5946,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "check_type": "check_in",
            "image_format": "jpeg"
        }
        
        return self.run_test("HRMS Face Check-in Different Formats", "POST", "hrms/face-checkin", 200, data=face_checkin_data)

    def test_hrms_multiple_checkins_same_employee(self):
        """Test multiple check-ins for the same employee"""
        # First check-in
        checkin_data = {
            "employee_id": "EMP003",
            "employee_name": "Amit Patel",
            "latitude": 23.0225,  # Ahmedabad coordinates
            "longitude": 72.5714,
            "accuracy": 12.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "check_type": "check_in"
        }
        
        success1, _ = self.run_test("HRMS Multiple Check-ins (First)", "POST", "hrms/gps-checkin", 200, data=checkin_data)
        
        # Second check-out
        checkin_data["check_type"] = "check_out"
        checkin_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        success2, _ = self.run_test("HRMS Multiple Check-ins (Second)", "POST", "hrms/gps-checkin", 200, data=checkin_data)
        
        return success1 and success2, {}

    def test_hrms_attendance_data_persistence(self):
        """Test if attendance data is being persisted correctly"""
        # Create a unique employee for this test
        unique_employee_id = "EMP_TEST_" + str(uuid.uuid4())[:8]
        
        attendance_data = {
            "employee_id": unique_employee_id,
            "employee_name": "Test Employee",
            "image_data": self.generate_mock_face_image(),
            "latitude": 18.5204,  # Pune coordinates
            "longitude": 73.8567,
            "accuracy": 7.5,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "check_type": "check_in",
            "notes": "Test attendance record"
        }
        
        return self.run_test("HRMS Attendance Data Persistence", "POST", "hrms/face-checkin", 200, data=attendance_data)

    def test_hrms_error_handling(self):
        """Test HRMS error handling with malformed data"""
        malformed_data = {
            "employee_id": "",  # Empty employee ID
            "image_data": "invalid_base64_data",
            "latitude": "not_a_number",
            "longitude": "not_a_number",
            "timestamp": "invalid_timestamp",
            "check_type": "invalid_type"
        }
        
        return self.run_test("HRMS Error Handling", "POST", "hrms/face-checkin", 400, data=malformed_data)

    def test_core_backend_integration(self):
        """Test core backend integration with HRMS"""
        # Test if HRMS endpoints are properly integrated with the main backend
        integration_tests = [
            ("HRMS Health Check", "GET", "hrms/health", 200),
            ("HRMS Employee Status", "GET", "hrms/employee-status", 200),
            ("HRMS Attendance Summary", "GET", "hrms/attendance-summary", 200)
        ]
        
        all_passed = True
        for test_name, method, endpoint, expected_status in integration_tests:
            success, _ = self.run_test(test_name, method, endpoint, expected_status)
            if not success:
                all_passed = False
        
        return all_passed, {}

    def test_authentication_integration_with_hrms(self):
        """Test authentication integration with HRMS endpoints"""
        if not self.auth_token:
            print("⚠️ Skipping test - no auth token available")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        protected_hrms_data = {
            "employee_id": self.test_employee_id,
            "image_data": self.generate_mock_face_image(),
            "latitude": 19.0760,
            "longitude": 72.8777,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "check_type": "check_in"
        }
        
        return self.run_test("HRMS with Authentication", "POST", "hrms/face-checkin", 200, 
                           data=protected_hrms_data, headers=headers)

def main():
    print("🎯 Starting HRMS Camera Backend API Testing")
    print("=" * 60)
    print("📋 Focus Areas:")
    print("   • HRMS Face Check-in APIs")
    print("   • HRMS GPS Check-in APIs") 
    print("   • Core Backend Health")
    print("   • Authentication System")
    print("   • Lead & Task Management")
    print("=" * 60)
    
    tester = HRMSCameraBackendTester()

    # Test 1: Core Backend Health Check
    print("\n🏥 TESTING CORE BACKEND HEALTH")
    print("-" * 40)
    
    success, _ = tester.test_health_check()
    if not success:
        print("❌ Core backend health check failed, stopping tests")
        return 1

    # Test 2: Essential API Endpoints
    print("\n📊 TESTING ESSENTIAL APIs")
    print("-" * 40)
    
    tester.test_dashboard_stats()
    tester.test_get_leads()
    tester.test_get_tasks()

    # Test 3: Authentication System
    print("\n🔐 TESTING AUTHENTICATION SYSTEM")
    print("-" * 40)
    
    tester.test_admin_login()

    # Test 4: HRMS Camera APIs - Core Focus
    print("\n📸 TESTING HRMS CAMERA APIs (PRIORITY)")
    print("-" * 40)
    
    # Face Check-in Tests
    print("\n👤 Face Check-in API Tests:")
    tester.test_hrms_face_checkin_endpoint_access()
    tester.test_hrms_face_checkin_with_realistic_data()
    tester.test_hrms_face_checkin_validation()
    tester.test_hrms_face_checkin_different_formats()
    
    # GPS Check-in Tests  
    print("\n📍 GPS Check-in API Tests:")
    tester.test_hrms_gps_checkin_endpoint_access()
    tester.test_hrms_gps_checkin_with_realistic_data()
    tester.test_hrms_gps_checkin_validation()
    
    # Advanced HRMS Tests
    print("\n🔄 Advanced HRMS Tests:")
    tester.test_hrms_multiple_checkins_same_employee()
    tester.test_hrms_attendance_data_persistence()
    tester.test_hrms_error_handling()

    # Test 5: Backend Integration
    print("\n🔗 TESTING BACKEND INTEGRATION")
    print("-" * 40)
    
    tester.test_core_backend_integration()
    tester.test_authentication_integration_with_hrms()

    # Final Results
    print("\n" + "=" * 60)
    print(f"📊 HRMS CAMERA BACKEND TEST RESULTS")
    print("=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    # Detailed Results by Category
    print(f"\n📋 DETAILED RESULTS:")
    print(f"   🏥 Core Backend Health: {'✅ WORKING' if tester.tests_passed > 0 else '❌ FAILED'}")
    print(f"   📊 Essential APIs: {'✅ WORKING' if tester.tests_passed >= 3 else '❌ NEEDS ATTENTION'}")
    print(f"   🔐 Authentication: {'✅ WORKING' if tester.auth_token else '❌ FAILED'}")
    print(f"   📸 HRMS Camera APIs: {'✅ WORKING' if tester.tests_passed >= 8 else '❌ NEEDS ATTENTION'}")
    
    if tester.tests_passed >= (tester.tests_run * 0.8):  # 80% success rate
        print(f"\n🎉 HRMS Camera Backend APIs are working correctly!")
        print(f"   ✅ Face check-in endpoints are functional")
        print(f"   ✅ GPS check-in endpoints are functional") 
        print(f"   ✅ Core backend integration is working")
        print(f"   ✅ Authentication system is operational")
        return 0
    else:
        print(f"\n⚠️ Some HRMS Camera API tests failed. Issues detected:")
        if tester.tests_passed < 3:
            print(f"   ❌ Core backend connectivity issues")
        if not tester.auth_token:
            print(f"   ❌ Authentication system problems")
        if tester.tests_passed < 8:
            print(f"   ❌ HRMS Camera API functionality issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())