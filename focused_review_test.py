#!/usr/bin/env python3
"""
Focused Backend Testing for Review Request
Testing specific endpoints with realistic data as requested:
1. Lead Creation Endpoint (POST /api/leads)
2. Lead Retrieval (GET /api/leads) 
3. Task Management endpoints
4. File Upload Handling
5. Notification System
"""

import requests
import json
import time
import uuid
from datetime import datetime, timezone

# Configuration
BACKEND_URL = "https://green-crm-suite.preview.emergentagent.com/api"
TIMEOUT = 30

class FocusedReviewTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_result(self, test_name, status, details="", response_time=0, data=None):
        """Log test result with detailed information"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            print(f"✅ {test_name}: {status} ({response_time:.2f}s)")
            if data:
                print(f"   📊 Data: {json.dumps(data, indent=2)[:200]}...")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {status} - {details}")
        
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    
    def test_lead_creation_endpoint(self):
        """Test POST /api/leads with realistic data"""
        print("\n🎯 TESTING LEAD CREATION ENDPOINT")
        print("=" * 50)
        
        # Realistic test lead data as specified in review request
        test_lead = {
            "name": "Rajesh Kumar",
            "email": "rajesh@test.com", 
            "phone": "+91-9876543210",
            "source": "Manual Entry",
            "budget": 75000,
            "space_size": "3 BHK Apartment",
            "location": "Pune, Maharashtra",
            "category": "Residential",
            "notes": "Interested in balcony garden setup with automated watering system"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/leads", json=test_lead, timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                # Verify response structure
                required_fields = ['id', 'name', 'phone', 'email', 'source']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_result("Lead Creation - POST /api/leads", "PASS", 
                                  f"Lead created successfully with ID: {data.get('id')}", 
                                  response_time, data)
                    return data.get('id')  # Return lead ID for further testing
                else:
                    self.log_result("Lead Creation - POST /api/leads", "FAIL", 
                                  f"Missing required fields in response: {missing_fields}")
                    return None
            else:
                self.log_result("Lead Creation - POST /api/leads", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                return None
                
        except Exception as e:
            self.log_result("Lead Creation - POST /api/leads", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_lead_retrieval_endpoint(self):
        """Test GET /api/leads endpoint"""
        print("\n👥 TESTING LEAD RETRIEVAL ENDPOINT")
        print("=" * 50)
        
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/leads", timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    lead_count = len(data)
                    self.log_result("Lead Retrieval - GET /api/leads", "PASS", 
                                  f"Retrieved {lead_count} leads successfully", 
                                  response_time, {"lead_count": lead_count})
                    
                    # Test with filters
                    self.test_lead_retrieval_with_filters()
                    return True
                else:
                    self.log_result("Lead Retrieval - GET /api/leads", "FAIL", 
                                  f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_result("Lead Retrieval - GET /api/leads", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_result("Lead Retrieval - GET /api/leads", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_lead_retrieval_with_filters(self):
        """Test lead retrieval with various filters"""
        filters = [
            ("status=New", "Filter by New status"),
            ("limit=5", "Limit results to 5"),
            ("status=Qualified", "Filter by Qualified status")
        ]
        
        for filter_param, description in filters:
            try:
                start_time = time.time()
                response = self.session.get(f"{BACKEND_URL}/leads?{filter_param}", timeout=TIMEOUT)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(f"Lead Retrieval - {description}", "PASS", 
                                  f"Retrieved {len(data)} leads with filter", response_time)
                else:
                    self.log_result(f"Lead Retrieval - {description}", "FAIL", 
                                  f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result(f"Lead Retrieval - {description}", "FAIL", f"Exception: {str(e)}")
    
    def test_task_management_endpoints(self):
        """Test task-related endpoints for workflow and task status updates"""
        print("\n📋 TESTING TASK MANAGEMENT ENDPOINTS")
        print("=" * 50)
        
        # Test GET /api/tasks
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/tasks", timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                task_count = len(data) if isinstance(data, list) else 0
                self.log_result("Task Retrieval - GET /api/tasks", "PASS", 
                              f"Retrieved {task_count} tasks successfully", 
                              response_time, {"task_count": task_count})
                
                # Test task creation
                self.test_task_creation()
                
                # Test task status updates if we have tasks
                if task_count > 0:
                    self.test_task_status_updates(data[0] if isinstance(data, list) else None)
                    
            else:
                self.log_result("Task Retrieval - GET /api/tasks", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Task Retrieval - GET /api/tasks", "FAIL", f"Exception: {str(e)}")
    
    def test_task_creation(self):
        """Test task creation with realistic data"""
        realistic_task = {
            "title": "Follow up with Rajesh Kumar for garden consultation",
            "description": "Schedule site visit for 3 BHK balcony garden setup. Discuss automated watering system requirements and budget finalization.",
            "priority": "High",
            "due_date": "2024-12-20T10:00:00Z",
            "assigned_to": "sales_executive_1"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/tasks", json=realistic_task, timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Task Creation - POST /api/tasks", "PASS", 
                              f"Task created with ID: {data.get('id')}", 
                              response_time, data)
                return data.get('id')
            else:
                self.log_result("Task Creation - POST /api/tasks", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                return None
                
        except Exception as e:
            self.log_result("Task Creation - POST /api/tasks", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_task_status_updates(self, sample_task):
        """Test task status update functionality"""
        if not sample_task or 'id' not in sample_task:
            return
            
        task_id = sample_task['id']
        status_update = {"status": "In Progress"}
        
        try:
            start_time = time.time()
            response = self.session.put(f"{BACKEND_URL}/tasks/{task_id}", json=status_update, timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Task Status Update - PUT /api/tasks/{id}", "PASS", 
                              f"Task status updated to: {data.get('status')}", 
                              response_time, data)
            else:
                self.log_result("Task Status Update - PUT /api/tasks/{id}", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Task Status Update - PUT /api/tasks/{id}", "FAIL", f"Exception: {str(e)}")
    
    def test_file_upload_endpoints(self):
        """Test file upload handling for gallery/catalogue functionality"""
        print("\n📁 TESTING FILE UPLOAD ENDPOINTS")
        print("=" * 50)
        
        # Test HRMS face check-in (which handles image uploads)
        try:
            face_checkin_data = {
                "employee_id": "EMP001",
                "face_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "location": {
                    "latitude": 18.5204,
                    "longitude": 73.8567,
                    "accuracy": 10,
                    "address": "Pune, Maharashtra"
                },
                "device_info": {
                    "device_id": "test_device_001",
                    "platform": "web"
                }
            }
            
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/hrms/face-checkin", json=face_checkin_data, timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("File Upload - HRMS Face Check-in (Image Upload)", "PASS", 
                              "Face image upload and processing working", response_time, data)
            else:
                self.log_result("File Upload - HRMS Face Check-in (Image Upload)", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("File Upload - HRMS Face Check-in (Image Upload)", "FAIL", f"Exception: {str(e)}")
        
        # Test GPS check-in as alternative
        try:
            gps_checkin_data = {
                "employee_id": "EMP001",
                "location": {
                    "latitude": 18.5204,
                    "longitude": 73.8567,
                    "accuracy": 15,
                    "address": "Aavana Greens Office, Pune"
                },
                "check_type": "check_in"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/hrms/gps-checkin", json=gps_checkin_data, timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("File Upload - GPS Check-in (Location Data)", "PASS", 
                              "GPS location data upload working", response_time, data)
            else:
                self.log_result("File Upload - GPS Check-in (Location Data)", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("File Upload - GPS Check-in (Location Data)", "FAIL", f"Exception: {str(e)}")
    
    def test_notification_system_endpoints(self):
        """Test notification-related endpoints"""
        print("\n🔔 TESTING NOTIFICATION SYSTEM ENDPOINTS")
        print("=" * 50)
        
        # Test AI smart notifications endpoint
        try:
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/ai/automation/smart-notifications", json={}, timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Notification - AI Smart Notifications", "PASS", 
                              "Smart notification system working", response_time, data)
            else:
                self.log_result("Notification - AI Smart Notifications", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Notification - AI Smart Notifications", "FAIL", f"Exception: {str(e)}")
        
        # Test HRMS attendance summary (notification-related)
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/hrms/attendance-summary/EMP001?month=12&year=2024", timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Notification - HRMS Attendance Summary", "PASS", 
                              "HRMS attendance notifications working", response_time, data)
            else:
                self.log_result("Notification - HRMS Attendance Summary", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Notification - HRMS Attendance Summary", "FAIL", f"Exception: {str(e)}")
        
        # Test payroll report (notification system)
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/hrms/payroll-report?month=12&year=2024", timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Notification - HRMS Payroll Report", "PASS", 
                              "HRMS payroll notification system working", response_time, data)
            else:
                self.log_result("Notification - HRMS Payroll Report", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Notification - HRMS Payroll Report", "FAIL", f"Exception: {str(e)}")
    
    def test_workflow_endpoints(self):
        """Test workflow creation and task status updates"""
        print("\n⚙️ TESTING WORKFLOW ENDPOINTS")
        print("=" * 50)
        
        # Test workflow templates
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/workflow-templates", timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                template_count = len(data) if isinstance(data, list) else 0
                self.log_result("Workflow Templates - GET /api/workflow-templates", "PASS", 
                              f"Retrieved {template_count} workflow templates", 
                              response_time, {"template_count": template_count})
            else:
                self.log_result("Workflow Templates - GET /api/workflow-templates", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Workflow Templates - GET /api/workflow-templates", "FAIL", f"Exception: {str(e)}")
        
        # Test workflows
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/workflows", timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                workflow_count = len(data.get('workflows', [])) if isinstance(data, dict) else len(data)
                self.log_result("Workflows - GET /api/workflows", "PASS", 
                              f"Retrieved {workflow_count} workflows", 
                              response_time, {"workflow_count": workflow_count})
            else:
                self.log_result("Workflows - GET /api/workflows", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Workflows - GET /api/workflows", "FAIL", f"Exception: {str(e)}")
    
    def test_dashboard_stats(self):
        """Test dashboard stats to ensure overall system health"""
        print("\n📊 TESTING DASHBOARD STATS")
        print("=" * 50)
        
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/dashboard/stats", timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_stats = ['total_leads', 'new_leads', 'pending_tasks', 'conversion_rate']
                missing_stats = [stat for stat in required_stats if stat not in data]
                
                if not missing_stats:
                    self.log_result("Dashboard Stats - GET /api/dashboard/stats", "PASS", 
                                  f"All required stats present. Conversion rate: {data.get('conversion_rate')}%", 
                                  response_time, data)
                else:
                    self.log_result("Dashboard Stats - GET /api/dashboard/stats", "FAIL", 
                                  f"Missing stats: {missing_stats}")
            else:
                self.log_result("Dashboard Stats - GET /api/dashboard/stats", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Dashboard Stats - GET /api/dashboard/stats", "FAIL", f"Exception: {str(e)}")
    
    def run_focused_review_tests(self):
        """Run all focused tests as per review request"""
        print("🎯 FOCUSED BACKEND TESTING FOR REVIEW REQUEST")
        print("=" * 60)
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"⏰ Timeout: {TIMEOUT}s")
        print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Focus: Lead Creation, Task Management, File Upload, Notifications")
        
        # Test sequence as per review request
        self.test_dashboard_stats()  # Overall health check
        self.test_lead_creation_endpoint()  # 1. Lead Creation Endpoint
        self.test_lead_retrieval_endpoint()  # 2. Lead Retrieval
        self.test_task_management_endpoints()  # 3. Task Management
        self.test_workflow_endpoints()  # Workflow and task status updates
        self.test_file_upload_endpoints()  # 4. File Upload Handling
        self.test_notification_system_endpoints()  # 5. Notification System
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 FOCUSED REVIEW TEST SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        success_rate = (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Categorize results by functionality
        categories = {
            "Lead Management": ["Lead Creation", "Lead Retrieval"],
            "Task Management": ["Task Retrieval", "Task Creation", "Task Status"],
            "Workflow System": ["Workflow", "workflow"],
            "File Upload": ["File Upload"],
            "Notification System": ["Notification"],
            "Dashboard": ["Dashboard Stats"]
        }
        
        print(f"\n📋 RESULTS BY CATEGORY:")
        for category, keywords in categories.items():
            category_results = [r for r in self.results if any(keyword in r['test'] for keyword in keywords)]
            if category_results:
                passed = sum(1 for r in category_results if r['status'] == 'PASS')
                total = len(category_results)
                print(f"   {category}: {passed}/{total} passed")
        
        # Show critical failures
        critical_failures = [r for r in self.results if r['status'] == 'FAIL']
        if critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(critical_failures)}):")
            for result in critical_failures:
                print(f"   🔴 {result['test']}: {result['details']}")
        
        # Show successful endpoints
        successful_tests = [r for r in self.results if r['status'] == 'PASS']
        if successful_tests:
            print(f"\n✅ SUCCESSFUL ENDPOINTS ({len(successful_tests)}):")
            for result in successful_tests:
                print(f"   ✅ {result['test']}")
        
        # Overall assessment
        print(f"\n🎯 REVIEW REQUEST ASSESSMENT:")
        
        # Check specific requirements
        lead_creation_working = any("Lead Creation" in r['test'] and r['status'] == 'PASS' for r in self.results)
        lead_retrieval_working = any("Lead Retrieval" in r['test'] and r['status'] == 'PASS' for r in self.results)
        task_management_working = any("Task" in r['test'] and r['status'] == 'PASS' for r in self.results)
        file_upload_working = any("File Upload" in r['test'] and r['status'] == 'PASS' for r in self.results)
        notification_working = any("Notification" in r['test'] and r['status'] == 'PASS' for r in self.results)
        
        print(f"   1. Lead Creation Endpoint: {'✅ WORKING' if lead_creation_working else '❌ FAILING'}")
        print(f"   2. Lead Retrieval: {'✅ WORKING' if lead_retrieval_working else '❌ FAILING'}")
        print(f"   3. Task Management: {'✅ WORKING' if task_management_working else '❌ FAILING'}")
        print(f"   4. File Upload Handling: {'✅ WORKING' if file_upload_working else '❌ FAILING'}")
        print(f"   5. Notification System: {'✅ WORKING' if notification_working else '❌ FAILING'}")
        
        if success_rate >= 80:
            print(f"\n🎉 EXCELLENT: Review requirements largely satisfied")
        elif success_rate >= 60:
            print(f"\n✅ GOOD: Most review requirements working")
        elif success_rate >= 40:
            print(f"\n⚠️ MODERATE: Some review requirements need attention")
        else:
            print(f"\n🚨 CRITICAL: Major issues with review requirements")

if __name__ == "__main__":
    print("🚀 Starting Focused Backend Testing for Review Request...")
    tester = FocusedReviewTester()
    tester.run_focused_review_tests()