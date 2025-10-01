#!/usr/bin/env python3
"""
CRM Backend Endpoints Test Suite
Tests the newly added CRM endpoints as per review request:
1) Health: GET /api/health → 200 with {status: ok, service: crm-backend, time}
2) Leads CRUD: POST, GET, PUT, DELETE /api/leads
3) Tasks CRUD: POST, GET, PUT, DELETE /api/tasks
"""

import requests
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

# Configuration - Use external URL from frontend/.env
BASE_URL = "https://aavana-crm-dmm.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class CRMEndpointsTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_leads = []  # Track created leads for cleanup
        self.created_tasks = []  # Track created tasks for cleanup
        
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
        """Test GET /api/health - expect 200 with {status: ok, service: crm-backend, time}"""
        try:
            response = self.session.get(f"{API_BASE}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["status", "service", "time"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    if (data.get("status") == "ok" and 
                        data.get("service") == "crm-backend" and
                        data.get("time")):  # Check time is present and ISO format
                        try:
                            # Validate ISO format
                            datetime.fromisoformat(data["time"].replace('Z', '+00:00'))
                            self.log_test("Health Check", True, "CRM backend healthy with correct schema")
                            return True
                        except ValueError:
                            self.log_test("Health Check", False, "Invalid ISO time format", data)
                    else:
                        self.log_test("Health Check", False, "Invalid field values", data)
                else:
                    self.log_test("Health Check", False, f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_create_lead(self):
        """Test POST /api/leads with minimal body {name} → success true and id, status default New"""
        try:
            lead_data = {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@techcorp.com",
                "phone": "+1-555-0199",
                "source": "Website Contact Form"
            }
            
            response = self.session.post(
                f"{API_BASE}/leads",
                json=lead_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "lead" in data:
                    lead = data["lead"]
                    # Verify required fields
                    required_fields = ["id", "name", "status", "created_at", "updated_at"]
                    missing_fields = [field for field in required_fields if field not in lead]
                    
                    if not missing_fields:
                        # Verify UUID format for id
                        try:
                            uuid.UUID(lead["id"])
                            uuid_valid = True
                        except ValueError:
                            uuid_valid = False
                        
                        # Verify default status
                        status_correct = lead.get("status") == "New"
                        
                        # Verify ISO timestamps
                        try:
                            datetime.fromisoformat(lead["created_at"].replace('Z', '+00:00'))
                            datetime.fromisoformat(lead["updated_at"].replace('Z', '+00:00'))
                            timestamps_valid = True
                        except ValueError:
                            timestamps_valid = False
                        
                        if uuid_valid and status_correct and timestamps_valid:
                            self.created_leads.append(lead["id"])
                            self.log_test("Create Lead", True, 
                                        f"Created lead with ID: {lead['id']}, status: {lead['status']}")
                            return True
                        else:
                            issues = []
                            if not uuid_valid: issues.append("invalid UUID")
                            if not status_correct: issues.append(f"wrong status: {lead.get('status')}")
                            if not timestamps_valid: issues.append("invalid timestamps")
                            self.log_test("Create Lead", False, 
                                        f"Validation issues: {', '.join(issues)}", data)
                    else:
                        self.log_test("Create Lead", False, 
                                    f"Missing fields: {missing_fields}", data)
                else:
                    self.log_test("Create Lead", False, "Invalid response format", data)
            else:
                self.log_test("Create Lead", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Lead", False, f"Error: {str(e)}")
        return False
    
    def test_create_lead_minimal(self):
        """Test POST /api/leads with minimal body {name} only"""
        try:
            lead_data = {"name": "Michael Chen"}
            
            response = self.session.post(
                f"{API_BASE}/leads",
                json=lead_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "lead" in data:
                    lead = data["lead"]
                    if (lead.get("name") == "Michael Chen" and 
                        lead.get("status") == "New" and
                        "id" in lead):
                        self.created_leads.append(lead["id"])
                        self.log_test("Create Lead (Minimal)", True, 
                                    f"Created minimal lead with default status 'New'")
                        return True
                    else:
                        self.log_test("Create Lead (Minimal)", False, 
                                    "Missing required fields or wrong defaults", data)
                else:
                    self.log_test("Create Lead (Minimal)", False, "Invalid response format", data)
            else:
                self.log_test("Create Lead (Minimal)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Lead (Minimal)", False, f"Error: {str(e)}")
        return False
    
    def test_list_leads(self):
        """Test GET /api/leads (list) with pagination → returns items array without _id"""
        try:
            response = self.session.get(f"{API_BASE}/leads", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["items", "page", "limit", "total"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    items = data["items"]
                    if isinstance(items, list):
                        # Verify items don't include _id field
                        has_mongo_id = any("_id" in item for item in items if isinstance(item, dict))
                        if not has_mongo_id:
                            self.log_test("List Leads", True, 
                                        f"Retrieved {len(items)} leads without _id fields")
                            return True
                        else:
                            self.log_test("List Leads", False, 
                                        "Response contains _id fields", items[:2])
                    else:
                        self.log_test("List Leads", False, "Items is not a list", data)
                else:
                    self.log_test("List Leads", False, f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("List Leads", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("List Leads", False, f"Error: {str(e)}")
        return False
    
    def test_update_lead(self):
        """Test PUT /api/leads/{id} to change status and notes → reflected in GET by id"""
        if not self.created_leads:
            self.log_test("Update Lead", False, "No leads available to update")
            return False
        
        try:
            lead_id = self.created_leads[0]
            update_data = {
                "status": "Qualified",
                "notes": "Interested in enterprise solution - follow up next week"
            }
            
            response = self.session.put(
                f"{API_BASE}/leads/{lead_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "lead" in data:
                    lead = data["lead"]
                    if (lead.get("status") == "Qualified" and 
                        lead.get("notes") == "Interested in enterprise solution - follow up next week" and
                        "updated_at" in lead):
                        self.log_test("Update Lead", True, 
                                    f"Successfully updated lead {lead_id}")
                        return True
                    else:
                        self.log_test("Update Lead", False, 
                                    "Lead not properly updated", data)
                else:
                    self.log_test("Update Lead", False, "Invalid response format", data)
            else:
                self.log_test("Update Lead", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Update Lead", False, f"Error: {str(e)}")
        return False
    
    def test_delete_lead(self):
        """Test DELETE /api/leads/{id} → success true then list should not include it"""
        if len(self.created_leads) < 2:
            self.log_test("Delete Lead", False, "Need at least 2 leads to test deletion")
            return False
        
        try:
            lead_id = self.created_leads[-1]  # Delete the last created lead
            
            response = self.session.delete(f"{API_BASE}/leads/{lead_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Verify lead is no longer in list
                    list_response = self.session.get(f"{API_BASE}/leads", timeout=10)
                    if list_response.status_code == 200:
                        list_data = list_response.json()
                        items = list_data.get("items", [])
                        deleted_lead_found = any(item.get("id") == lead_id for item in items)
                        
                        if not deleted_lead_found:
                            self.created_leads.remove(lead_id)
                            self.log_test("Delete Lead", True, 
                                        f"Successfully deleted lead {lead_id}")
                            return True
                        else:
                            self.log_test("Delete Lead", False, 
                                        "Lead still appears in list after deletion")
                    else:
                        self.log_test("Delete Lead", False, 
                                    "Could not verify deletion via list endpoint")
                else:
                    self.log_test("Delete Lead", False, "Delete response missing success flag", data)
            else:
                self.log_test("Delete Lead", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Delete Lead", False, f"Error: {str(e)}")
        return False
    
    def test_create_task(self):
        """Test POST /api/tasks with {title} → success true and id"""
        try:
            task_data = {
                "title": "Schedule product demo",
                "description": "Set up demo call with Sarah Johnson from TechCorp",
                "assignee": "sales@aavana.com",
                "due_date": "2024-12-31T17:00:00Z"
            }
            
            response = self.session.post(
                f"{API_BASE}/tasks",
                json=task_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "task" in data:
                    task = data["task"]
                    # Verify required fields
                    required_fields = ["id", "title", "status", "created_at", "updated_at"]
                    missing_fields = [field for field in required_fields if field not in task]
                    
                    if not missing_fields:
                        # Verify UUID format for id
                        try:
                            uuid.UUID(task["id"])
                            uuid_valid = True
                        except ValueError:
                            uuid_valid = False
                        
                        # Verify default status
                        status_correct = task.get("status") == "Open"
                        
                        if uuid_valid and status_correct:
                            self.created_tasks.append(task["id"])
                            self.log_test("Create Task", True, 
                                        f"Created task with ID: {task['id']}, status: {task['status']}")
                            return True
                        else:
                            issues = []
                            if not uuid_valid: issues.append("invalid UUID")
                            if not status_correct: issues.append(f"wrong status: {task.get('status')}")
                            self.log_test("Create Task", False, 
                                        f"Validation issues: {', '.join(issues)}", data)
                    else:
                        self.log_test("Create Task", False, 
                                    f"Missing fields: {missing_fields}", data)
                else:
                    self.log_test("Create Task", False, "Invalid response format", data)
            else:
                self.log_test("Create Task", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Task", False, f"Error: {str(e)}")
        return False
    
    def test_create_task_minimal(self):
        """Test POST /api/tasks with minimal body {title} only"""
        try:
            task_data = {"title": "Review contract proposal"}
            
            response = self.session.post(
                f"{API_BASE}/tasks",
                json=task_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "task" in data:
                    task = data["task"]
                    if (task.get("title") == "Review contract proposal" and 
                        task.get("status") == "Open" and
                        "id" in task):
                        self.created_tasks.append(task["id"])
                        self.log_test("Create Task (Minimal)", True, 
                                    f"Created minimal task with default status 'Open'")
                        return True
                    else:
                        self.log_test("Create Task (Minimal)", False, 
                                    "Missing required fields or wrong defaults", data)
                else:
                    self.log_test("Create Task (Minimal)", False, "Invalid response format", data)
            else:
                self.log_test("Create Task (Minimal)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Task (Minimal)", False, f"Error: {str(e)}")
        return False
    
    def test_list_tasks(self):
        """Test GET /api/tasks (list) → returns items array without _id"""
        try:
            response = self.session.get(f"{API_BASE}/tasks", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["items", "page", "limit", "total"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    items = data["items"]
                    if isinstance(items, list):
                        # Verify items don't include _id field
                        has_mongo_id = any("_id" in item for item in items if isinstance(item, dict))
                        if not has_mongo_id:
                            self.log_test("List Tasks", True, 
                                        f"Retrieved {len(items)} tasks without _id fields")
                            return True
                        else:
                            self.log_test("List Tasks", False, 
                                        "Response contains _id fields", items[:2])
                    else:
                        self.log_test("List Tasks", False, "Items is not a list", data)
                else:
                    self.log_test("List Tasks", False, f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("List Tasks", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("List Tasks", False, f"Error: {str(e)}")
        return False
    
    def test_update_task(self):
        """Test PUT /api/tasks/{id} set status → reflected"""
        if not self.created_tasks:
            self.log_test("Update Task", False, "No tasks available to update")
            return False
        
        try:
            task_id = self.created_tasks[0]
            update_data = {
                "status": "In Progress",
                "assignee": "support@aavana.com"
            }
            
            response = self.session.put(
                f"{API_BASE}/tasks/{task_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "task" in data:
                    task = data["task"]
                    if (task.get("status") == "In Progress" and 
                        task.get("assignee") == "support@aavana.com" and
                        "updated_at" in task):
                        self.log_test("Update Task", True, 
                                    f"Successfully updated task {task_id}")
                        return True
                    else:
                        self.log_test("Update Task", False, 
                                    "Task not properly updated", data)
                else:
                    self.log_test("Update Task", False, "Invalid response format", data)
            else:
                self.log_test("Update Task", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Update Task", False, f"Error: {str(e)}")
        return False
    
    def test_delete_task(self):
        """Test DELETE /api/tasks/{id} → success true"""
        if len(self.created_tasks) < 2:
            self.log_test("Delete Task", False, "Need at least 2 tasks to test deletion")
            return False
        
        try:
            task_id = self.created_tasks[-1]  # Delete the last created task
            
            response = self.session.delete(f"{API_BASE}/tasks/{task_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Verify task is no longer in list
                    list_response = self.session.get(f"{API_BASE}/tasks", timeout=10)
                    if list_response.status_code == 200:
                        list_data = list_response.json()
                        items = list_data.get("items", [])
                        deleted_task_found = any(item.get("id") == task_id for item in items)
                        
                        if not deleted_task_found:
                            self.created_tasks.remove(task_id)
                            self.log_test("Delete Task", True, 
                                        f"Successfully deleted task {task_id}")
                            return True
                        else:
                            self.log_test("Delete Task", False, 
                                        "Task still appears in list after deletion")
                    else:
                        self.log_test("Delete Task", False, 
                                    "Could not verify deletion via list endpoint")
                else:
                    self.log_test("Delete Task", False, "Delete response missing success flag", data)
            else:
                self.log_test("Delete Task", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Delete Task", False, f"Error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all CRM backend tests in sequence"""
        print("🚀 Starting CRM Backend Endpoints Test Suite")
        print("=" * 60)
        print(f"Testing against: {BASE_URL}")
        print("=" * 60)
        
        # Test 1: Health endpoint
        print("\n1️⃣ Testing Health Endpoint...")
        if not self.test_health_endpoint():
            print("❌ Health check failed - aborting tests")
            return False
        
        # Test 2: Leads CRUD
        print("\n2️⃣ Testing Leads CRUD...")
        self.test_create_lead()
        self.test_create_lead_minimal()
        self.test_list_leads()
        self.test_update_lead()
        self.test_delete_lead()
        
        # Test 3: Tasks CRUD
        print("\n3️⃣ Testing Tasks CRUD...")
        self.test_create_task()
        self.test_create_task_minimal()
        self.test_list_tasks()
        self.test_update_task()
        self.test_delete_task()
        
        # Summary
        self.print_summary()
        
        return self.get_overall_success()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 CRM BACKEND ENDPOINTS TEST SUMMARY")
        print("=" * 60)
        
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
        
        # Show created items
        if self.created_leads:
            print(f"\n📝 Created {len(self.created_leads)} test leads in database")
        if self.created_tasks:
            print(f"📝 Created {len(self.created_tasks)} test tasks in database")
    
    def get_overall_success(self):
        """Get overall test success status"""
        if not self.test_results:
            return False
        
        # Critical tests that must pass for CRM functionality
        critical_tests = [
            "Health Check",
            "Create Lead",
            "List Leads", 
            "Update Lead",
            "Delete Lead",
            "Create Task",
            "List Tasks",
            "Update Task",
            "Delete Task"
        ]
        
        critical_passed = all(
            any(result["test"] == test and result["success"] for result in self.test_results)
            for test in critical_tests
        )
        
        return critical_passed

def main():
    """Main test execution"""
    tester = CRMEndpointsTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CRM Backend endpoints tests completed successfully!")
        exit(0)
    else:
        print("\n❌ CRM Backend endpoints tests had critical failures!")
        exit(1)

if __name__ == "__main__":
    main()