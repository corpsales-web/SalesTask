#!/usr/bin/env python3
"""
Critical Loading Issues Test - Focused on User-Reported Problems
Testing specifically for:
1. "Failed to fetch tasks" error
2. "Failed to fetch leads" error  
3. Backend endpoint connectivity
4. Database connectivity for tasks/leads collections
5. CORS and authentication issues
"""

import requests
import sys
import json
from datetime import datetime, timezone
import uuid

class LoadingIssuesTester:
    def __init__(self, base_url="https://aavana-greens-crm.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.auth_token = None

    def log_result(self, test_name, success, details=""):
        """Log test result and track critical failures"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
            if details:
                print(f"   Details: {details}")
        else:
            print(f"❌ {test_name}: FAILED")
            if details:
                print(f"   Error: {details}")
            self.critical_failures.append(f"{test_name}: {details}")

    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        print("\n🔍 Testing Backend Connectivity...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Backend Health Check", True, f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}")
                return True
            else:
                self.log_result("Backend Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Backend Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_cors_headers(self):
        """Test CORS configuration"""
        print("\n🔍 Testing CORS Configuration...")
        try:
            # Test preflight request
            headers = {
                'Origin': 'https://aavana-greens-crm.preview.emergentagent.com',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            response = requests.options(f"{self.base_url}/leads", headers=headers, timeout=10)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if any(cors_headers.values()):
                self.log_result("CORS Headers", True, f"CORS configured: {cors_headers}")
                return True
            else:
                self.log_result("CORS Headers", False, "No CORS headers found")
                return False
        except Exception as e:
            self.log_result("CORS Headers", False, f"CORS test error: {str(e)}")
            return False

    def test_leads_endpoint(self):
        """Test GET /api/leads endpoint - Critical for 'Failed to fetch leads' issue"""
        print("\n🔍 Testing GET /api/leads endpoint...")
        try:
            response = requests.get(f"{self.base_url}/leads", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_result("GET /api/leads", True, f"Retrieved {len(data)} leads successfully")
                        
                        # Test data structure
                        if data and len(data) > 0:
                            sample_lead = data[0]
                            required_fields = ['id', 'name', 'phone', 'status']
                            missing_fields = [field for field in required_fields if field not in sample_lead]
                            
                            if not missing_fields:
                                self.log_result("Leads Data Structure", True, "All required fields present")
                            else:
                                self.log_result("Leads Data Structure", False, f"Missing fields: {missing_fields}")
                        else:
                            self.log_result("Leads Data", True, "No leads in database (empty result is valid)")
                        
                        return True
                    else:
                        self.log_result("GET /api/leads", False, f"Invalid response format: {type(data)}")
                        return False
                except json.JSONDecodeError as e:
                    self.log_result("GET /api/leads", False, f"Invalid JSON response: {str(e)}")
                    return False
            else:
                self.log_result("GET /api/leads", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("GET /api/leads", False, f"Request failed: {str(e)}")
            return False

    def test_tasks_endpoint(self):
        """Test GET /api/tasks endpoint - Critical for 'Failed to fetch tasks' issue"""
        print("\n🔍 Testing GET /api/tasks endpoint...")
        try:
            response = requests.get(f"{self.base_url}/tasks", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_result("GET /api/tasks", True, f"Retrieved {len(data)} tasks successfully")
                        
                        # Test data structure
                        if data and len(data) > 0:
                            sample_task = data[0]
                            required_fields = ['id', 'title', 'status', 'priority']
                            missing_fields = [field for field in required_fields if field not in sample_task]
                            
                            if not missing_fields:
                                self.log_result("Tasks Data Structure", True, "All required fields present")
                            else:
                                self.log_result("Tasks Data Structure", False, f"Missing fields: {missing_fields}")
                        else:
                            self.log_result("Tasks Data", True, "No tasks in database (empty result is valid)")
                        
                        return True
                    else:
                        self.log_result("GET /api/tasks", False, f"Invalid response format: {type(data)}")
                        return False
                except json.JSONDecodeError as e:
                    self.log_result("GET /api/tasks", False, f"Invalid JSON response: {str(e)}")
                    return False
            else:
                self.log_result("GET /api/tasks", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("GET /api/tasks", False, f"Request failed: {str(e)}")
            return False

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        print("\n🔍 Testing Dashboard Stats endpoint...")
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    required_fields = ['total_leads', 'total_revenue', 'pending_tasks', 'conversion_rate']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_result("Dashboard Stats", True, f"Stats: {data.get('total_leads', 0)} leads, {data.get('pending_tasks', 0)} tasks")
                        return True
                    else:
                        self.log_result("Dashboard Stats", False, f"Missing fields: {missing_fields}")
                        return False
                except json.JSONDecodeError as e:
                    self.log_result("Dashboard Stats", False, f"Invalid JSON response: {str(e)}")
                    return False
            else:
                self.log_result("Dashboard Stats", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Dashboard Stats", False, f"Request failed: {str(e)}")
            return False

    def test_database_connectivity(self):
        """Test database connectivity by creating and retrieving test data"""
        print("\n🔍 Testing Database Connectivity...")
        
        # Test creating a lead
        test_lead = {
            "name": "Test Lead for Connectivity",
            "phone": "9999999999",
            "email": "test@connectivity.com",
            "budget": 50000,
            "location": "Test City",
            "notes": "Database connectivity test"
        }
        
        try:
            # Create lead
            response = requests.post(f"{self.base_url}/leads", json=test_lead, timeout=10)
            
            if response.status_code == 200:
                lead_data = response.json()
                lead_id = lead_data.get('id')
                
                if lead_id:
                    self.log_result("Database Write (Lead)", True, f"Created lead with ID: {lead_id}")
                    
                    # Test retrieving the lead
                    get_response = requests.get(f"{self.base_url}/leads/{lead_id}", timeout=10)
                    if get_response.status_code == 200:
                        retrieved_lead = get_response.json()
                        if retrieved_lead.get('name') == test_lead['name']:
                            self.log_result("Database Read (Lead)", True, "Successfully retrieved created lead")
                            
                            # Clean up - delete the test lead
                            delete_response = requests.delete(f"{self.base_url}/leads/{lead_id}", timeout=10)
                            if delete_response.status_code == 200:
                                self.log_result("Database Delete (Lead)", True, "Successfully deleted test lead")
                            else:
                                self.log_result("Database Delete (Lead)", False, f"Failed to delete: HTTP {delete_response.status_code}")
                            
                            return True
                        else:
                            self.log_result("Database Read (Lead)", False, "Retrieved lead data doesn't match")
                            return False
                    else:
                        self.log_result("Database Read (Lead)", False, f"Failed to retrieve: HTTP {get_response.status_code}")
                        return False
                else:
                    self.log_result("Database Write (Lead)", False, "No ID returned from created lead")
                    return False
            else:
                self.log_result("Database Write (Lead)", False, f"Failed to create lead: HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Database test failed: {str(e)}")
            return False

    def test_task_operations(self):
        """Test task creation, retrieval, and status updates"""
        print("\n🔍 Testing Task Operations...")
        
        test_task = {
            "title": "Test Task for Connectivity",
            "description": "Testing task operations",
            "priority": "Medium",
            "assigned_to": "Test User"
        }
        
        try:
            # Create task
            response = requests.post(f"{self.base_url}/tasks", json=test_task, timeout=10)
            
            if response.status_code == 200:
                task_data = response.json()
                task_id = task_data.get('id')
                
                if task_id:
                    self.log_result("Task Creation", True, f"Created task with ID: {task_id}")
                    
                    # Test task status update
                    update_data = {"status": "In Progress"}
                    update_response = requests.put(f"{self.base_url}/tasks/{task_id}", json=update_data, timeout=10)
                    
                    if update_response.status_code == 200:
                        updated_task = update_response.json()
                        if updated_task.get('status') == 'In Progress':
                            self.log_result("Task Status Update", True, "Successfully updated task status")
                            return True
                        else:
                            self.log_result("Task Status Update", False, f"Status not updated correctly: {updated_task.get('status')}")
                            return False
                    else:
                        self.log_result("Task Status Update", False, f"Failed to update: HTTP {update_response.status_code}")
                        return False
                else:
                    self.log_result("Task Creation", False, "No ID returned from created task")
                    return False
            else:
                self.log_result("Task Creation", False, f"Failed to create task: HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Task Operations", False, f"Task operations test failed: {str(e)}")
            return False

    def test_response_times(self):
        """Test response times for critical endpoints"""
        print("\n🔍 Testing Response Times...")
        
        endpoints = [
            ("leads", "/leads"),
            ("tasks", "/tasks"),
            ("dashboard", "/dashboard/stats")
        ]
        
        all_passed = True
        
        for name, endpoint in endpoints:
            try:
                import time
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.status_code == 200 and response_time < 5000:  # 5 second threshold
                    self.log_result(f"Response Time ({name})", True, f"{response_time:.0f}ms")
                else:
                    self.log_result(f"Response Time ({name})", False, f"{response_time:.0f}ms (too slow or failed)")
                    all_passed = False
                    
            except Exception as e:
                self.log_result(f"Response Time ({name})", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def run_all_tests(self):
        """Run all critical loading issue tests"""
        print("🚨 CRITICAL LOADING ISSUES TEST SUITE")
        print("=" * 60)
        print("Testing for user-reported 'Failed to fetch tasks/leads' errors")
        print("=" * 60)
        
        # Test 1: Backend Connectivity
        backend_ok = self.test_backend_connectivity()
        if not backend_ok:
            print("\n❌ CRITICAL: Backend is not accessible. All other tests will fail.")
            return False
        
        # Test 2: CORS Configuration
        self.test_cors_headers()
        
        # Test 3: Critical Endpoints
        leads_ok = self.test_leads_endpoint()
        tasks_ok = self.test_tasks_endpoint()
        
        # Test 4: Dashboard Stats
        self.test_dashboard_stats()
        
        # Test 5: Database Connectivity
        db_ok = self.test_database_connectivity()
        
        # Test 6: Task Operations
        task_ops_ok = self.test_task_operations()
        
        # Test 7: Response Times
        self.test_response_times()
        
        # Summary
        print("\n" + "=" * 60)
        print("🔍 CRITICAL LOADING ISSUES TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Critical Issues Analysis
        print("\n🚨 CRITICAL ISSUES ANALYSIS:")
        
        if not leads_ok:
            print("❌ LEADS LOADING ISSUE CONFIRMED: GET /api/leads endpoint is failing")
        else:
            print("✅ LEADS LOADING: Working correctly")
            
        if not tasks_ok:
            print("❌ TASKS LOADING ISSUE CONFIRMED: GET /api/tasks endpoint is failing")
        else:
            print("✅ TASKS LOADING: Working correctly")
            
        if not db_ok:
            print("❌ DATABASE CONNECTIVITY ISSUE: Cannot read/write to database")
        else:
            print("✅ DATABASE CONNECTIVITY: Working correctly")
        
        if self.critical_failures:
            print(f"\n🔥 {len(self.critical_failures)} CRITICAL FAILURES DETECTED:")
            for i, failure in enumerate(self.critical_failures, 1):
                print(f"   {i}. {failure}")
        else:
            print("\n🎉 NO CRITICAL FAILURES DETECTED!")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if not backend_ok:
            print("   1. Check backend service status and logs")
            print("   2. Verify network connectivity and firewall settings")
        if not (leads_ok and tasks_ok):
            print("   3. Check database connection and collection permissions")
            print("   4. Verify API endpoint implementations")
        if self.critical_failures:
            print("   5. Address critical failures listed above immediately")
        
        return leads_ok and tasks_ok and backend_ok

def main():
    tester = LoadingIssuesTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())