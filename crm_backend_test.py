#!/usr/bin/env python3
"""
CRM Backend Test Suite
Tests CRM Tasks and Leads endpoints to ensure compatibility with frontend after fixes
"""

import requests
import json
import time
import uuid
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception:
        pass
    return "https://aavana-crm-dmm.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class CRMBackendTester:
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
        """Test GET /api/health - expect 200, JSON with status: ok, service: crm-backend, time ISO"""
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
    
    def test_leads_create(self):
        """Test POST /api/leads with minimal {name}"""
        try:
            lead_data = {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "phone": "+1-555-0123",
                "source": "Website"
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
                        
                        # Verify no _id field
                        no_mongo_id = "_id" not in lead
                        
                        if uuid_valid and status_correct and timestamps_valid and no_mongo_id:
                            self.created_leads.append(lead["id"])
                            self.log_test("Leads Create", True, 
                                        f"Created lead with ID: {lead['id']}, status: {lead['status']}")
                            return True
                        else:
                            issues = []
                            if not uuid_valid: issues.append("invalid UUID")
                            if not status_correct: issues.append("wrong status")
                            if not timestamps_valid: issues.append("invalid timestamps")
                            if not no_mongo_id: issues.append("contains _id")
                            self.log_test("Leads Create", False, 
                                        f"Validation issues: {', '.join(issues)}", data)
                    else:
                        self.log_test("Leads Create", False, 
                                    f"Missing fields: {missing_fields}", data)
                else:
                    self.log_test("Leads Create", False, "Invalid response format", data)
            else:
                self.log_test("Leads Create", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads Create", False, f"Error: {str(e)}")
        return False
    
    def test_leads_create_minimal(self):
        """Test POST /api/leads with minimal {name} only"""
        try:
            lead_data = {"name": "Jane Doe"}
            
            response = self.session.post(
                f"{API_BASE}/leads",
                json=lead_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "lead" in data:
                    lead = data["lead"]
                    if (lead.get("name") == "Jane Doe" and 
                        lead.get("status") == "New" and
                        "id" in lead):
                        self.created_leads.append(lead["id"])
                        self.log_test("Leads Create (Minimal)", True, 
                                    f"Created lead with minimal data, ID: {lead['id']}")
                        return True
                    else:
                        self.log_test("Leads Create (Minimal)", False, "Invalid lead data", data)
                else:
                    self.log_test("Leads Create (Minimal)", False, "Invalid response format", data)
            else:
                self.log_test("Leads Create (Minimal)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads Create (Minimal)", False, f"Error: {str(e)}")
        return False
    
    def test_leads_list(self):
        """Test GET /api/leads list returns {items, page, limit, total}"""
        try:
            response = self.session.get(f"{API_BASE}/leads", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["items", "page", "limit", "total"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify items is a list
                    if isinstance(data["items"], list):
                        # Verify no _id fields in items
                        has_mongo_id = any("_id" in item for item in data["items"] if isinstance(item, dict))
                        if not has_mongo_id:
                            self.log_test("Leads List", True, 
                                        f"Retrieved {len(data['items'])} leads, page {data['page']}, total {data['total']}")
                            return True
                        else:
                            self.log_test("Leads List", False, "Items contain _id fields", data)
                    else:
                        self.log_test("Leads List", False, "Items is not a list", data)
                else:
                    self.log_test("Leads List", False, f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("Leads List", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads List", False, f"Error: {str(e)}")
        return False
    
    def test_leads_update(self):
        """Test PUT /api/leads/{id} updates fields"""
        if not self.created_leads:
            self.log_test("Leads Update", False, "No leads available to update")
            return False
        
        try:
            lead_id = self.created_leads[0]
            update_data = {
                "status": "Qualified",
                "notes": "Updated via automated test"
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
                        lead.get("notes") == "Updated via automated test" and
                        "updated_at" in lead):
                        self.log_test("Leads Update", True, 
                                    f"Updated lead {lead_id} status and notes")
                        return True
                    else:
                        self.log_test("Leads Update", False, "Fields not updated correctly", data)
                else:
                    self.log_test("Leads Update", False, "Invalid response format", data)
            else:
                self.log_test("Leads Update", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads Update", False, f"Error: {str(e)}")
        return False
    
    def test_leads_delete(self):
        """Test DELETE /api/leads/{id}"""
        if not self.created_leads:
            self.log_test("Leads Delete", False, "No leads available to delete")
            return False
        
        try:
            lead_id = self.created_leads[-1]  # Delete the last created lead
            
            response = self.session.delete(f"{API_BASE}/leads/{lead_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Verify lead is actually deleted
                    verify_response = self.session.get(f"{API_BASE}/leads", timeout=10)
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        deleted_lead_exists = any(
                            item.get("id") == lead_id 
                            for item in verify_data.get("items", [])
                        )
                        if not deleted_lead_exists:
                            self.created_leads.remove(lead_id)
                            self.log_test("Leads Delete", True, f"Successfully deleted lead {lead_id}")
                            return True
                        else:
                            self.log_test("Leads Delete", False, "Lead still exists after deletion")
                    else:
                        self.log_test("Leads Delete", False, "Could not verify deletion")
                else:
                    self.log_test("Leads Delete", False, "Invalid response format", data)
            else:
                self.log_test("Leads Delete", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads Delete", False, f"Error: {str(e)}")
        return False
    
    def test_tasks_create(self):
        """Test POST /api/tasks with minimal {title}"""
        try:
            task_data = {
                "title": "Follow up with lead",
                "description": "Call the lead to discuss requirements",
                "assignee": "Sales Team",
                "due_date": "2024-12-31T23:59:59Z"
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
                        
                        # Verify ISO timestamps
                        try:
                            datetime.fromisoformat(task["created_at"].replace('Z', '+00:00'))
                            datetime.fromisoformat(task["updated_at"].replace('Z', '+00:00'))
                            timestamps_valid = True
                        except ValueError:
                            timestamps_valid = False
                        
                        # Verify no _id field
                        no_mongo_id = "_id" not in task
                        
                        if uuid_valid and status_correct and timestamps_valid and no_mongo_id:
                            self.created_tasks.append(task["id"])
                            self.log_test("Tasks Create", True, 
                                        f"Created task with ID: {task['id']}, status: {task['status']}")
                            return True
                        else:
                            issues = []
                            if not uuid_valid: issues.append("invalid UUID")
                            if not status_correct: issues.append("wrong status")
                            if not timestamps_valid: issues.append("invalid timestamps")
                            if not no_mongo_id: issues.append("contains _id")
                            self.log_test("Tasks Create", False, 
                                        f"Validation issues: {', '.join(issues)}", data)
                    else:
                        self.log_test("Tasks Create", False, 
                                    f"Missing fields: {missing_fields}", data)
                else:
                    self.log_test("Tasks Create", False, "Invalid response format", data)
            else:
                self.log_test("Tasks Create", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Tasks Create", False, f"Error: {str(e)}")
        return False
    
    def test_tasks_create_minimal(self):
        """Test POST /api/tasks with minimal {title} only"""
        try:
            task_data = {"title": "Review proposal"}
            
            response = self.session.post(
                f"{API_BASE}/tasks",
                json=task_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "task" in data:
                    task = data["task"]
                    if (task.get("title") == "Review proposal" and 
                        task.get("status") == "Open" and
                        "id" in task):
                        self.created_tasks.append(task["id"])
                        self.log_test("Tasks Create (Minimal)", True, 
                                    f"Created task with minimal data, ID: {task['id']}")
                        return True
                    else:
                        self.log_test("Tasks Create (Minimal)", False, "Invalid task data", data)
                else:
                    self.log_test("Tasks Create (Minimal)", False, "Invalid response format", data)
            else:
                self.log_test("Tasks Create (Minimal)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Tasks Create (Minimal)", False, f"Error: {str(e)}")
        return False
    
    def test_tasks_list(self):
        """Test GET /api/tasks list returns {items, page, limit, total}"""
        try:
            response = self.session.get(f"{API_BASE}/tasks", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["items", "page", "limit", "total"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify items is a list
                    if isinstance(data["items"], list):
                        # Verify no _id fields in items
                        has_mongo_id = any("_id" in item for item in data["items"] if isinstance(item, dict))
                        if not has_mongo_id:
                            self.log_test("Tasks List", True, 
                                        f"Retrieved {len(data['items'])} tasks, page {data['page']}, total {data['total']}")
                            return True
                        else:
                            self.log_test("Tasks List", False, "Items contain _id fields", data)
                    else:
                        self.log_test("Tasks List", False, "Items is not a list", data)
                else:
                    self.log_test("Tasks List", False, f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("Tasks List", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Tasks List", False, f"Error: {str(e)}")
        return False
    
    def test_tasks_update(self):
        """Test PUT /api/tasks/{id} with {status: 'In Progress'}"""
        if not self.created_tasks:
            self.log_test("Tasks Update", False, "No tasks available to update")
            return False
        
        try:
            task_id = self.created_tasks[0]
            update_data = {"status": "In Progress"}
            
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
                        "updated_at" in task):
                        self.log_test("Tasks Update", True, 
                                    f"Updated task {task_id} status to 'In Progress'")
                        return True
                    else:
                        self.log_test("Tasks Update", False, "Status not updated correctly", data)
                else:
                    self.log_test("Tasks Update", False, "Invalid response format", data)
            else:
                self.log_test("Tasks Update", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Tasks Update", False, f"Error: {str(e)}")
        return False
    
    def test_tasks_update_status_endpoint(self):
        """Test PUT /api/tasks/{id}/status with {status: 'Completed'}"""
        if not self.created_tasks:
            self.log_test("Tasks Update Status", False, "No tasks available to update")
            return False
        
        try:
            task_id = self.created_tasks[0]
            update_data = {"status": "Completed"}
            
            response = self.session.put(
                f"{API_BASE}/tasks/{task_id}/status",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "task" in data:
                    task = data["task"]
                    if (task.get("status") == "Completed" and
                        "updated_at" in task):
                        self.log_test("Tasks Update Status", True, 
                                    f"Updated task {task_id} status to 'Completed' via /status endpoint")
                        return True
                    else:
                        self.log_test("Tasks Update Status", False, "Status not updated correctly", data)
                else:
                    self.log_test("Tasks Update Status", False, "Invalid response format", data)
            else:
                self.log_test("Tasks Update Status", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Tasks Update Status", False, f"Error: {str(e)}")
        return False
    
    def test_tasks_delete(self):
        """Test DELETE /api/tasks/{id}"""
        if not self.created_tasks:
            self.log_test("Tasks Delete", False, "No tasks available to delete")
            return False
        
        try:
            task_id = self.created_tasks[-1]  # Delete the last created task
            
            response = self.session.delete(f"{API_BASE}/tasks/{task_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Verify task is actually deleted
                    verify_response = self.session.get(f"{API_BASE}/tasks", timeout=10)
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        deleted_task_exists = any(
                            item.get("id") == task_id 
                            for item in verify_data.get("items", [])
                        )
                        if not deleted_task_exists:
                            self.created_tasks.remove(task_id)
                            self.log_test("Tasks Delete", True, f"Successfully deleted task {task_id}")
                            return True
                        else:
                            self.log_test("Tasks Delete", False, "Task still exists after deletion")
                    else:
                        self.log_test("Tasks Delete", False, "Could not verify deletion")
                else:
                    self.log_test("Tasks Delete", False, "Invalid response format", data)
            else:
                self.log_test("Tasks Delete", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Tasks Delete", False, f"Error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all CRM backend tests in sequence"""
        print("🚀 Starting CRM Backend Test Suite")
        print("=" * 60)
        print(f"🔗 Testing backend at: {BASE_URL}")
        print("=" * 60)
        
        # Test 1: Health endpoint
        print("\n1️⃣ Testing Health Endpoint...")
        if not self.test_health_endpoint():
            print("❌ Health check failed - aborting tests")
            return False
        
        # Test 2: Leads CRUD
        print("\n2️⃣ Testing Leads CRUD...")
        self.test_leads_create()
        self.test_leads_create_minimal()
        self.test_leads_list()
        self.test_leads_update()
        self.test_leads_delete()
        
        # Test 3: Tasks CRUD
        print("\n3️⃣ Testing Tasks CRUD...")
        self.test_tasks_create()
        self.test_tasks_create_minimal()
        self.test_tasks_list()
        self.test_tasks_update()
        self.test_tasks_update_status_endpoint()
        self.test_tasks_delete()
        
        # Summary
        self.print_summary()
        
        return self.get_overall_success()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 CRM BACKEND TEST SUMMARY")
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
        total_created = len(self.created_leads) + len(self.created_tasks)
        if total_created > 0:
            print(f"\n📝 Created {total_created} test items in database ({len(self.created_leads)} leads, {len(self.created_tasks)} tasks)")
    
    def get_overall_success(self):
        """Get overall test success status"""
        if not self.test_results:
            return False
        
        # Critical tests that must pass for CRM functionality
        critical_tests = [
            "Health Check",
            "Leads Create",
            "Leads List", 
            "Tasks Create",
            "Tasks List"
        ]
        
        critical_passed = all(
            any(result["test"] == test and result["success"] for result in self.test_results)
            for test in critical_tests
        )
        
        return critical_passed

def main():
    """Main test execution"""
    tester = CRMBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CRM Backend tests completed successfully!")
        exit(0)
    else:
        print("\n❌ CRM Backend tests had critical failures!")
        exit(1)

if __name__ == "__main__":
    main()