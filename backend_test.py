import requests
import sys
from datetime import datetime
import json

class BackendAPITester:
    def __init__(self, base_url="https://hi-there-419.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, expected_keys=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            print(f"Response Status: {response.status_code}")
            
            # Check status code
            status_success = response.status_code == expected_status
            
            # Parse response
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
            except:
                response_data = {}
                print(f"Response Text: {response.text}")

            # Check expected keys if provided
            keys_success = True
            if expected_keys and response_data:
                for key in expected_keys:
                    if key not in response_data:
                        keys_success = False
                        print(f"❌ Missing expected key: {key}")

            success = status_success and keys_success
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed")
            else:
                print(f"❌ Failed - Expected status {expected_status}, got {response.status_code}")

            self.test_results.append({
                'name': name,
                'success': success,
                'status_code': response.status_code,
                'response': response_data
            })

            return success, response_data

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                'name': name,
                'success': False,
                'error': str(e)
            })
            return False, {}

    def test_hello_world(self):
        """Test GET /api/ endpoint"""
        success, response = self.run_test(
            "Hello World API",
            "GET",
            "api/",
            200,
            expected_keys=["message"]
        )
        
        if success and response.get("message") == "Hello World":
            print("✅ Hello World message correct")
            return True
        elif success:
            print(f"❌ Unexpected message: {response.get('message')}")
            return False
        return False

    def test_create_status(self, client_name="test"):
        """Test POST /api/status endpoint"""
        success, response = self.run_test(
            "Create Status Check",
            "POST",
            "api/status",
            200,  # Based on FastAPI, should be 200 for successful POST
            data={"client_name": client_name},
            expected_keys=["id", "client_name", "timestamp"]
        )
        
        if success:
            # Verify UUID format (should be string, not ObjectID)
            status_id = response.get('id')
            if status_id and isinstance(status_id, str) and len(status_id) == 36:
                print("✅ ID is UUID format (not MongoDB ObjectID)")
            else:
                print(f"❌ ID format issue: {status_id}")
                return False, None
            
            # Verify client_name matches
            if response.get('client_name') == client_name:
                print("✅ Client name matches")
            else:
                print(f"❌ Client name mismatch: expected {client_name}, got {response.get('client_name')}")
                return False, None
                
            return True, status_id
        
        return False, None

    def test_get_status_list(self):
        """Test GET /api/status endpoint"""
        success, response = self.run_test(
            "Get Status List",
            "GET",
            "api/status",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"✅ Received list with {len(response)} items")
                return True, response
            else:
                print(f"❌ Expected list, got {type(response)}")
                return False, []
        
        return False, []

def main():
    print("🚀 Starting Backend API Tests")
    print("=" * 50)
    
    tester = BackendAPITester()
    
    # Test 1: Hello World endpoint
    print("\n" + "="*30)
    print("TEST 1: Hello World API")
    print("="*30)
    hello_success = tester.test_hello_world()
    
    # Test 2: Create status check
    print("\n" + "="*30)
    print("TEST 2: Create Status Check")
    print("="*30)
    create_success, status_id = tester.test_create_status("test")
    
    # Test 3: Get status list
    print("\n" + "="*30)
    print("TEST 3: Get Status List")
    print("="*30)
    list_success, status_list = tester.test_get_status_list()
    
    # Verify the created status appears in the list
    if create_success and list_success and status_id:
        found_status = any(item.get('id') == status_id for item in status_list)
        if found_status:
            print("✅ Created status found in list")
        else:
            print("❌ Created status not found in list")
            tester.tests_run += 1
    
    # Print final results
    print("\n" + "="*50)
    print("📊 FINAL RESULTS")
    print("="*50)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())