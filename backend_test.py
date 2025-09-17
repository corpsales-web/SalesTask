#!/usr/bin/env python3
"""
Backend API Testing for 502 Error Resolution
Focus: Testing specific endpoints reported with 502 errors by user
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://green-crm-suite.preview.emergentagent.com/api"
TIMEOUT = 30

class BackendTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, test_name, status, details="", response_time=0):
        """Log test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            print(f"✅ {test_name}: {status} ({response_time:.2f}s)")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {status} - {details}")
        
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_endpoint(self, method, endpoint, test_name, expected_status=200, data=None, headers=None):
        """Generic endpoint testing"""
        url = f"{BACKEND_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=TIMEOUT, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=TIMEOUT, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=TIMEOUT, headers=headers)
            else:
                self.log_result(test_name, "FAIL", f"Unsupported method: {method}")
                return None
            
            response_time = time.time() - start_time
            
            if response.status_code == expected_status:
                self.log_result(test_name, "PASS", f"Status: {response.status_code}", response_time)
                return response
            else:
                error_detail = f"Expected {expected_status}, got {response.status_code}"
                if response.status_code == 502:
                    error_detail += " - BACKEND GATEWAY ERROR"
                try:
                    error_detail += f" - Response: {response.text[:200]}"
                except:
                    pass
                self.log_result(test_name, "FAIL", error_detail, response_time)
                return None
                
        except requests.exceptions.Timeout:
            self.log_result(test_name, "FAIL", "Request timeout")
            return None
        except requests.exceptions.ConnectionError:
            self.log_result(test_name, "FAIL", "Connection error")
            return None
        except Exception as e:
            self.log_result(test_name, "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_critical_endpoints(self):
        """Test the specific endpoints mentioned in review request"""
        print("🎯 TESTING CRITICAL ENDPOINTS FOR 502 ERROR RESOLUTION")
        print("=" * 60)
        
        # 1. Dashboard Stats (should be working)
        print("\n📊 Testing Dashboard Stats...")
        self.test_endpoint("GET", "/dashboard/stats", "Dashboard Stats API")
        
        # 2. Leads Endpoint (reported 502 error)
        print("\n👥 Testing Leads Endpoints...")
        self.test_endpoint("GET", "/leads", "Get All Leads")
        self.test_endpoint("GET", "/leads?limit=10", "Get Leads with Limit")
        
        # 3. Tasks Endpoint (reported 502 error)  
        print("\n📋 Testing Tasks Endpoints...")
        self.test_endpoint("GET", "/tasks", "Get All Tasks")
        self.test_endpoint("GET", "/tasks?limit=10", "Get Tasks with Limit")
        
        # 4. Workflow Templates (should be working)
        print("\n🔄 Testing Workflow Templates...")
        self.test_endpoint("GET", "/workflow-templates", "Get Workflow Templates")
        
        # 5. Workflows Endpoint (reported 502 error)
        print("\n⚙️ Testing Workflows Endpoints...")
        self.test_endpoint("GET", "/workflows", "Get All Workflows")
        
        # Additional critical endpoints
        print("\n🔍 Testing Additional Critical Endpoints...")
        self.test_endpoint("GET", "/", "Root API Endpoint")
        
    def test_backend_health(self):
        """Test overall backend health"""
        print("\n🏥 BACKEND HEALTH CHECK")
        print("=" * 30)
        
        # Test basic connectivity
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                print("✅ Backend is responding")
                print(f"📡 Response: {response.json()}")
            else:
                print(f"⚠️ Backend responding with status: {response.status_code}")
        except Exception as e:
            print(f"❌ Backend connectivity failed: {str(e)}")
    
    def test_specific_502_scenarios(self):
        """Test scenarios that commonly cause 502 errors"""
        print("\n🚨 TESTING 502 ERROR SCENARIOS")
        print("=" * 35)
        
        # Test with different HTTP methods
        endpoints_to_test = [
            ("/leads", "GET"),
            ("/tasks", "GET"), 
            ("/workflows", "GET"),
            ("/dashboard/stats", "GET")
        ]
        
        for endpoint, method in endpoints_to_test:
            print(f"\n🔍 Testing {method} {endpoint} for 502 errors...")
            response = self.test_endpoint(method, endpoint, f"{method} {endpoint} - 502 Check")
            
            if response and response.status_code == 502:
                print(f"🚨 CONFIRMED: 502 error on {endpoint}")
                print(f"Response headers: {dict(response.headers)}")
                print(f"Response body: {response.text[:500]}")
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🎯 BACKEND API TESTING FOR 502 ERROR RESOLUTION")
        print("=" * 55)
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"⏰ Timeout: {TIMEOUT}s")
        print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test backend health first
        self.test_backend_health()
        
        # Test critical endpoints
        self.test_critical_endpoints()
        
        # Test specific 502 scenarios
        self.test_specific_502_scenarios()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📈 Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        if self.failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        print("\n🎯 CRITICAL FINDINGS:")
        
        # Check for 502 errors specifically
        has_502_errors = any("502" in result["details"] for result in self.results if result["status"] == "FAIL")
        
        if has_502_errors:
            print("🚨 502 BACKEND GATEWAY ERRORS DETECTED:")
            for result in self.results:
                if result["status"] == "FAIL" and "502" in result["details"]:
                    print(f"   🔴 {result['test']}")
            print("\n💡 RECOMMENDED ACTIONS:")
            print("   1. Check if backend service is running")
            print("   2. Verify supervisor backend logs")
            print("   3. Check for missing dependencies")
            print("   4. Restart backend service if needed")
        else:
            print("✅ No 502 errors detected in tested endpoints")
        
        # Check for working endpoints
        working_endpoints = [result["test"] for result in self.results if result["status"] == "PASS"]
        if working_endpoints:
            print(f"\n✅ WORKING ENDPOINTS ({len(working_endpoints)}):")
            for endpoint in working_endpoints:
                print(f"   ✅ {endpoint}")

if __name__ == "__main__":
    print("🚀 Starting Backend API Testing for 502 Error Resolution...")
    tester = BackendTester()
    tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if tester.failed_tests > 0:
        print(f"\n⚠️ Testing completed with {tester.failed_tests} failures")
        sys.exit(1)
    else:
        print(f"\n🎉 All tests passed successfully!")
        sys.exit(0)