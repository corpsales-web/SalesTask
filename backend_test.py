import requests
import sys
import json
from datetime import datetime, timezone
import uuid

class AavanaGreensCRMTester:
    def __init__(self, base_url="https://greenworks.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_leads = []
        self.created_tasks = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

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

    def test_health_check(self):
        """Test basic health check"""
        return self.run_test("Health Check", "GET", "", 200)

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        return self.run_test("Dashboard Stats", "GET", "dashboard/stats", 200)

    def test_create_lead(self, lead_data):
        """Test creating a new lead"""
        success, response = self.run_test("Create Lead", "POST", "leads", 200, data=lead_data)
        if success and 'id' in response:
            self.created_leads.append(response['id'])
            return True, response
        return False, {}

    def test_get_leads(self):
        """Test getting all leads"""
        return self.run_test("Get All Leads", "GET", "leads", 200)

    def test_get_lead_by_id(self, lead_id):
        """Test getting a specific lead"""
        return self.run_test("Get Lead by ID", "GET", f"leads/{lead_id}", 200)

    def test_update_lead(self, lead_id, update_data):
        """Test updating a lead"""
        return self.run_test("Update Lead", "PUT", f"leads/{lead_id}", 200, data=update_data)

    def test_delete_lead(self, lead_id):
        """Test deleting a lead"""
        return self.run_test("Delete Lead", "DELETE", f"leads/{lead_id}", 200)

    def test_create_task(self, task_data):
        """Test creating a new task"""
        success, response = self.run_test("Create Task", "POST", "tasks", 200, data=task_data)
        if success and 'id' in response:
            self.created_tasks.append(response['id'])
            return True, response
        return False, {}

    def test_get_tasks(self):
        """Test getting all tasks"""
        return self.run_test("Get All Tasks", "GET", "tasks", 200)

    def test_update_task(self, task_id, update_data):
        """Test updating a task"""
        return self.run_test("Update Task", "PUT", f"tasks/{task_id}", 200, data=update_data)

def main():
    print("🚀 Starting Aavana Greens CRM API Tests")
    print("=" * 50)
    
    tester = AavanaGreensCRMTester()

    # Test 1: Health Check
    success, _ = tester.test_health_check()
    if not success:
        print("❌ Health check failed, stopping tests")
        return 1

    # Test 2: Dashboard Stats (initial state)
    print("\n📊 Testing Dashboard Stats...")
    tester.test_dashboard_stats()

    # Test 3: Create multiple leads with different data
    print("\n👥 Testing Lead Management...")
    
    test_leads = [
        {
            "name": "Rajesh Kumar",
            "phone": "9876543210",
            "email": "rajesh@example.com",
            "budget": 500000,
            "space_size": "2 BHK",
            "location": "Bangalore",
            "notes": "Interested in green building features",
            "tags": ["premium", "eco-friendly"],
            "assigned_to": "Sales Team A"
        },
        {
            "name": "Priya Sharma",
            "phone": "8765432109",
            "email": "priya@example.com",
            "budget": 750000,
            "space_size": "3 BHK",
            "location": "Mumbai",
            "notes": "Looking for immediate possession",
            "tags": ["urgent", "high-value"],
            "assigned_to": "Sales Team B"
        },
        {
            "name": "Amit Patel",
            "phone": "7654321098",
            "budget": 300000,
            "location": "Pune",
            "notes": "First-time buyer, needs guidance"
        }
    ]

    created_lead_ids = []
    for i, lead_data in enumerate(test_leads):
        success, response = tester.test_create_lead(lead_data)
        if success:
            created_lead_ids.append(response['id'])

    # Test 4: Get all leads
    tester.test_get_leads()

    # Test 5: Get specific lead
    if created_lead_ids:
        tester.test_get_lead_by_id(created_lead_ids[0])

    # Test 6: Update lead status (simulate pipeline progression)
    if created_lead_ids:
        print("\n🔄 Testing Lead Status Updates...")
        statuses = ["Qualified", "Proposal", "Negotiation", "Won"]
        
        for i, status in enumerate(statuses):
            if i < len(created_lead_ids):
                tester.test_update_lead(created_lead_ids[i], {"status": status})

    # Test 7: Create tasks
    print("\n📋 Testing Task Management...")
    
    test_tasks = [
        {
            "title": "Follow up with Rajesh Kumar",
            "description": "Call to discuss green building features and pricing",
            "priority": "High",
            "assigned_to": "Sales Team A",
            "lead_id": created_lead_ids[0] if created_lead_ids else None,
            "due_date": "2024-12-31T10:00:00Z"
        },
        {
            "title": "Prepare proposal for Priya Sharma",
            "description": "Create detailed proposal with floor plans",
            "priority": "Urgent",
            "assigned_to": "Sales Team B",
            "lead_id": created_lead_ids[1] if len(created_lead_ids) > 1 else None,
            "due_date": "2024-12-30T15:00:00Z"
        },
        {
            "title": "Site visit coordination",
            "description": "Arrange site visit for interested customers",
            "priority": "Medium",
            "assigned_to": "Operations Team"
        }
    ]

    created_task_ids = []
    for task_data in test_tasks:
        success, response = tester.test_create_task(task_data)
        if success:
            created_task_ids.append(response['id'])

    # Test 8: Get all tasks
    tester.test_get_tasks()

    # Test 9: Update task status
    if created_task_ids:
        print("\n✅ Testing Task Status Updates...")
        tester.test_update_task(created_task_ids[0], {"status": "In Progress"})
        if len(created_task_ids) > 1:
            tester.test_update_task(created_task_ids[1], {"status": "Completed"})

    # Test 10: Dashboard stats after changes
    print("\n📊 Testing Dashboard Stats After Changes...")
    tester.test_dashboard_stats()

    # Test 11: Error handling - invalid lead ID
    print("\n🚫 Testing Error Handling...")
    tester.run_test("Get Invalid Lead", "GET", "leads/invalid-id", 404)

    # Test 12: Delete a lead
    if created_lead_ids:
        print("\n🗑️ Testing Lead Deletion...")
        tester.test_delete_lead(created_lead_ids[-1])

    # Final Results
    print("\n" + "=" * 50)
    print(f"📊 FINAL TEST RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the backend implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())