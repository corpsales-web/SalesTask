#!/usr/bin/env python3
"""
Critical Backend Test for Aavana Greens CRM
Focus: Task status updates and leads fetching failures
"""

import requests
import sys
import json
from datetime import datetime, timezone
import uuid
import time

class CriticalBackendTester:
    def __init__(self, base_url="https://navdebug-crm.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.auth_token = None
        self.test_lead_id = None
        self.test_task_id = None
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            self.failed_tests.append(f"{test_name}: {details}")
            print(f"❌ {test_name}: FAILED {details}")
    
    def make_request(self, method, endpoint, data=None, params=None, auth_required=False):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"   Request failed: {str(e)}")
            return None

    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        print("\n🔍 TESTING BACKEND CONNECTIVITY")
        
        response = self.make_request('GET', '')
        if response and response.status_code == 200:
            self.log_result("Backend Health Check", True, f"Status: {response.status_code}")
            return True
        else:
            status = response.status_code if response else "No Response"
            self.log_result("Backend Health Check", False, f"Status: {status}")
            return False

    def test_leads_fetching(self):
        """Test GET /api/leads endpoint - Critical Issue #2"""
        print("\n🔍 TESTING LEADS FETCHING (Critical Issue)")
        
        # Test basic leads fetching
        response = self.make_request('GET', 'leads')
        if response:
            if response.status_code == 200:
                try:
                    leads_data = response.json()
                    if isinstance(leads_data, list):
                        self.log_result("GET /api/leads", True, f"Retrieved {len(leads_data)} leads")
                        
                        # Store a lead ID for task testing if available
                        if leads_data and len(leads_data) > 0:
                            self.test_lead_id = leads_data[0].get('id')
                            print(f"   Using lead ID for testing: {self.test_lead_id}")
                        
                        return True
                    else:
                        self.log_result("GET /api/leads", False, "Response is not a list")
                        return False
                except json.JSONDecodeError:
                    self.log_result("GET /api/leads", False, "Invalid JSON response")
                    return False
            else:
                self.log_result("GET /api/leads", False, f"Status: {response.status_code}")
                return False
        else:
            self.log_result("GET /api/leads", False, "No response received")
            return False

    def test_tasks_fetching(self):
        """Test GET /api/tasks endpoint - Critical Issue #1 related"""
        print("\n🔍 TESTING TASKS FETCHING")
        
        response = self.make_request('GET', 'tasks')
        if response:
            if response.status_code == 200:
                try:
                    tasks_data = response.json()
                    if isinstance(tasks_data, list):
                        self.log_result("GET /api/tasks", True, f"Retrieved {len(tasks_data)} tasks")
                        
                        # Store a task ID for status update testing
                        if tasks_data and len(tasks_data) > 0:
                            self.test_task_id = tasks_data[0].get('id')
                            current_status = tasks_data[0].get('status', 'Unknown')
                            print(f"   Using task ID for testing: {self.test_task_id}")
                            print(f"   Current status: {current_status}")
                        
                        return True
                    else:
                        self.log_result("GET /api/tasks", False, "Response is not a list")
                        return False
                except json.JSONDecodeError:
                    self.log_result("GET /api/tasks", False, "Invalid JSON response")
                    return False
            else:
                self.log_result("GET /api/tasks", False, f"Status: {response.status_code}")
                return False
        else:
            self.log_result("GET /api/tasks", False, "No response received")
            return False

    def create_test_task(self):
        """Create a test task for status update testing"""
        print("\n🔍 CREATING TEST TASK")
        
        task_data = {
            "title": "Critical Test Task - Status Updates",
            "description": "Test task for verifying status update functionality",
            "priority": "High",
            "lead_id": self.test_lead_id,
            "ai_generated": False
        }
        
        response = self.make_request('POST', 'tasks', data=task_data)
        if response and response.status_code == 200:
            try:
                task_response = response.json()
                self.test_task_id = task_response.get('id')
                self.log_result("Create Test Task", True, f"Task ID: {self.test_task_id}")
                return True
            except json.JSONDecodeError:
                self.log_result("Create Test Task", False, "Invalid JSON response")
                return False
        else:
            status = response.status_code if response else "No Response"
            self.log_result("Create Test Task", False, f"Status: {status}")
            return False

    def test_task_status_updates(self):
        """Test PUT /api/tasks/{task_id} for status updates - Critical Issue #1"""
        print("\n🔍 TESTING TASK STATUS UPDATES (Critical Issue)")
        
        if not self.test_task_id:
            print("   No test task ID available, creating one...")
            if not self.create_test_task():
                self.log_result("Task Status Updates", False, "Could not create test task")
                return False
        
        # Test status transitions: Pending -> In Progress -> Completed
        status_transitions = [
            ("In Progress", "Pending to In Progress"),
            ("Completed", "In Progress to Completed")
        ]
        
        success_count = 0
        for new_status, transition_name in status_transitions:
            print(f"\n   Testing transition: {transition_name}")
            
            update_data = {
                "status": new_status
            }
            
            response = self.make_request('PUT', f'tasks/{self.test_task_id}', data=update_data)
            if response:
                if response.status_code == 200:
                    try:
                        updated_task = response.json()
                        actual_status = updated_task.get('status')
                        if actual_status == new_status:
                            self.log_result(f"Status Update: {transition_name}", True, f"Status: {actual_status}")
                            success_count += 1
                        else:
                            self.log_result(f"Status Update: {transition_name}", False, f"Expected: {new_status}, Got: {actual_status}")
                    except json.JSONDecodeError:
                        self.log_result(f"Status Update: {transition_name}", False, "Invalid JSON response")
                else:
                    self.log_result(f"Status Update: {transition_name}", False, f"Status: {response.status_code}")
            else:
                self.log_result(f"Status Update: {transition_name}", False, "No response received")
        
        return success_count == len(status_transitions)

    def test_task_completion_endpoint(self):
        """Test POST /api/tasks/{task_id}/complete endpoint if it exists"""
        print("\n🔍 TESTING TASK COMPLETION ENDPOINT")
        
        if not self.test_task_id:
            self.log_result("Task Completion Endpoint", False, "No test task ID available")
            return False
        
        # First, reset task to Pending status
        reset_data = {"status": "Pending"}
        reset_response = self.make_request('PUT', f'tasks/{self.test_task_id}', data=reset_data)
        
        if reset_response and reset_response.status_code == 200:
            print("   Task reset to Pending status")
            
            # Now test the completion endpoint
            response = self.make_request('POST', f'tasks/{self.test_task_id}/complete')
            if response:
                if response.status_code == 200:
                    try:
                        completed_task = response.json()
                        status = completed_task.get('status')
                        completed_at = completed_task.get('completed_at')
                        
                        if status == "Completed" and completed_at:
                            self.log_result("Task Completion Endpoint", True, f"Status: {status}, Completed at: {completed_at}")
                            return True
                        else:
                            self.log_result("Task Completion Endpoint", False, f"Status: {status}, Completed at: {completed_at}")
                            return False
                    except json.JSONDecodeError:
                        self.log_result("Task Completion Endpoint", False, "Invalid JSON response")
                        return False
                elif response.status_code == 404:
                    self.log_result("Task Completion Endpoint", False, "Endpoint not found (404) - may not be implemented")
                    return False
                else:
                    self.log_result("Task Completion Endpoint", False, f"Status: {response.status_code}")
                    return False
            else:
                self.log_result("Task Completion Endpoint", False, "No response received")
                return False
        else:
            self.log_result("Task Completion Endpoint", False, "Could not reset task status")
            return False

    def test_database_connectivity(self):
        """Test database connectivity through CRUD operations"""
        print("\n🔍 TESTING DATABASE CONNECTIVITY")
        
        # Test Create operation
        test_lead_data = {
            "name": "Database Test Lead",
            "phone": "9999999999",
            "email": "dbtest@example.com",
            "location": "Test City",
            "budget": 25000,
            "space_size": "Test Space",
            "source": "API Test",
            "category": "Test Category"
        }
        
        create_response = self.make_request('POST', 'leads', data=test_lead_data)
        if create_response and create_response.status_code == 200:
            try:
                created_lead = create_response.json()
                test_lead_id = created_lead.get('id')
                self.log_result("Database Create Operation", True, f"Lead ID: {test_lead_id}")
                
                # Test Read operation
                read_response = self.make_request('GET', f'leads/{test_lead_id}')
                if read_response and read_response.status_code == 200:
                    self.log_result("Database Read Operation", True, "Lead retrieved successfully")
                    
                    # Test Update operation
                    update_data = {"notes": "Database connectivity test - updated"}
                    update_response = self.make_request('PUT', f'leads/{test_lead_id}', data=update_data)
                    if update_response and update_response.status_code == 200:
                        self.log_result("Database Update Operation", True, "Lead updated successfully")
                        
                        # Test Delete operation
                        delete_response = self.make_request('DELETE', f'leads/{test_lead_id}')
                        if delete_response and delete_response.status_code == 200:
                            self.log_result("Database Delete Operation", True, "Lead deleted successfully")
                            return True
                        else:
                            status = delete_response.status_code if delete_response else "No Response"
                            self.log_result("Database Delete Operation", False, f"Status: {status}")
                    else:
                        status = update_response.status_code if update_response else "No Response"
                        self.log_result("Database Update Operation", False, f"Status: {status}")
                else:
                    status = read_response.status_code if read_response else "No Response"
                    self.log_result("Database Read Operation", False, f"Status: {status}")
            except json.JSONDecodeError:
                self.log_result("Database Create Operation", False, "Invalid JSON response")
        else:
            status = create_response.status_code if create_response else "No Response"
            self.log_result("Database Create Operation", False, f"Status: {status}")
        
        return False

    def test_authentication_endpoints(self):
        """Test authentication for task and lead endpoints"""
        print("\n🔍 TESTING AUTHENTICATION/AUTHORIZATION")
        
        # Test without authentication first
        response = self.make_request('GET', 'leads')
        if response:
            if response.status_code == 200:
                self.log_result("Leads Access (No Auth)", True, "Public access allowed")
            elif response.status_code == 401:
                self.log_result("Leads Access (No Auth)", True, "Authentication required (expected)")
            else:
                self.log_result("Leads Access (No Auth)", False, f"Unexpected status: {response.status_code}")
        
        # Test tasks endpoint
        response = self.make_request('GET', 'tasks')
        if response:
            if response.status_code == 200:
                self.log_result("Tasks Access (No Auth)", True, "Public access allowed")
            elif response.status_code == 401:
                self.log_result("Tasks Access (No Auth)", True, "Authentication required (expected)")
            else:
                self.log_result("Tasks Access (No Auth)", False, f"Unexpected status: {response.status_code}")

    def run_critical_tests(self):
        """Run all critical tests focusing on the reported issues"""
        print("🚀 STARTING CRITICAL BACKEND TESTS")
        print("=" * 60)
        print("Focus: Task status updates and leads fetching failures")
        print("=" * 60)
        
        # Test 1: Backend Connectivity
        if not self.test_backend_connectivity():
            print("\n❌ CRITICAL: Backend is not accessible. Stopping tests.")
            return self.generate_summary()
        
        # Test 2: Leads Fetching (Critical Issue #2)
        self.test_leads_fetching()
        
        # Test 3: Tasks Fetching
        self.test_tasks_fetching()
        
        # Test 4: Task Status Updates (Critical Issue #1)
        self.test_task_status_updates()
        
        # Test 5: Task Completion Endpoint
        self.test_task_completion_endpoint()
        
        # Test 6: Database Connectivity
        self.test_database_connectivity()
        
        # Test 7: Authentication/Authorization
        self.test_authentication_endpoints()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🎯 CRITICAL BACKEND TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for i, failure in enumerate(self.failed_tests, 1):
                print(f"   {i}. {failure}")
        
        if success_rate >= 80:
            print(f"\n✅ OVERALL RESULT: GOOD - Most critical functionality is working")
        elif success_rate >= 60:
            print(f"\n⚠️  OVERALL RESULT: PARTIAL - Some critical issues need attention")
        else:
            print(f"\n❌ OVERALL RESULT: CRITICAL ISSUES - Major functionality is broken")
        
        return {
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "success_rate": success_rate,
            "failed_tests": self.failed_tests
        }

if __name__ == "__main__":
    tester = CriticalBackendTester()
    results = tester.run_critical_tests()
    
    # Exit with appropriate code
    if results["success_rate"] >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure