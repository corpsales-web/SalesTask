#!/usr/bin/env python3
"""
CRM Backend Smoke Test
Light smoke test to ensure backend still responds after frontend changes
Tests: GET /api/health, GET /api/uploads/catalogue/list, GET /api/whatsapp/conversations
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration - Use frontend's REACT_APP_BACKEND_URL
BASE_URL = "https://crm-visual-studio.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class CRMSmokeTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def test_health_endpoint(self):
        """Test GET /api/health"""
        try:
            response = self.session.get(f"{API_BASE}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if (data.get("status") == "ok" and 
                    data.get("service") == "crm-backend" and
                    data.get("time")):
                    self.log_test("Health Endpoint", True, f"Backend healthy: {data}")
                    return True
                else:
                    self.log_test("Health Endpoint", False, "Invalid response format", data)
            else:
                self.log_test("Health Endpoint", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Connection error: {str(e)}")
        return False
    
    def test_uploads_catalogue_list(self):
        """Test GET /api/uploads/catalogue/list"""
        try:
            response = self.session.get(f"{API_BASE}/uploads/catalogue/list", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "catalogues" in data and isinstance(data["catalogues"], list):
                    self.log_test("Uploads Catalogue List", True, 
                                f"Retrieved {len(data['catalogues'])} catalogue items")
                    return True
                else:
                    self.log_test("Uploads Catalogue List", False, "Invalid response format", data)
            else:
                self.log_test("Uploads Catalogue List", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Uploads Catalogue List", False, f"Connection error: {str(e)}")
        return False
    
    def test_whatsapp_conversations(self):
        """Test GET /api/whatsapp/conversations"""
        try:
            response = self.session.get(f"{API_BASE}/whatsapp/conversations", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("WhatsApp Conversations", True, 
                                f"Retrieved {len(data)} conversations")
                    return True
                else:
                    self.log_test("WhatsApp Conversations", False, "Response is not a list", data)
            else:
                self.log_test("WhatsApp Conversations", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("WhatsApp Conversations", False, f"Connection error: {str(e)}")
        return False
    
    def run_smoke_tests(self):
        """Run the three smoke tests"""
        print("🚀 Starting CRM Backend Smoke Test")
        print("=" * 50)
        print(f"Testing backend at: {BASE_URL}")
        print("=" * 50)
        
        # Test the three specific endpoints
        print("\n1️⃣ Testing Health Endpoint...")
        health_ok = self.test_health_endpoint()
        
        print("\n2️⃣ Testing Uploads Catalogue List...")
        uploads_ok = self.test_uploads_catalogue_list()
        
        print("\n3️⃣ Testing WhatsApp Conversations...")
        whatsapp_ok = self.test_whatsapp_conversations()
        
        # Summary
        self.print_summary()
        
        return health_ok and uploads_ok and whatsapp_ok
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 SMOKE TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        else:
            print("\n✅ All smoke tests passed!")

def main():
    """Main test execution"""
    tester = CRMSmokeTest()
    success = tester.run_smoke_tests()
    
    if success:
        print("\n✅ CRM Backend smoke test completed successfully!")
        print("Backend is responding properly after frontend changes.")
        return True
    else:
        print("\n❌ CRM Backend smoke test had failures!")
        print("Backend may have issues that need investigation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)