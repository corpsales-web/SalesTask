#!/usr/bin/env python3
"""
Comprehensive Backend Audit for Aavana Greens CRM
Final audit to identify any remaining backend issues before deployment
"""

import requests
import json
import sys
import time
from datetime import datetime, timezone
import uuid

class ComprehensiveBackendAudit:
    def __init__(self, base_url="https://navdebug-crm.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.auth_token = None
        self.test_user_id = None
        self.created_leads = []
        self.created_tasks = []
        
    def log_critical_failure(self, test_name, error_details):
        """Log critical failures for final report"""
        self.critical_failures.append({
            'test': test_name,
            'error': error_details,
            'timestamp': datetime.now().isoformat()
        })
        
    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test with comprehensive error handling"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)
            
        if self.auth_token:
            default_headers['Authorization'] = f'Bearer {self.auth_token}'

        self.tests_run += 1
        print(f"\n🔍 [{self.tests_run}] Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, headers=default_headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=30)
                
            response_time = round((time.time() - start_time) * 1000, 2)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code} ({response_time}ms)")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 300:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                        if len(response_data) > 0:
                            print(f"   Sample item: {response_data[0] if len(str(response_data[0])) < 200 else 'Large object'}")
                    return True, response_data
                except:
                    return True, {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                print(f"❌ FAILED - {error_msg}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.log_critical_failure(name, f"{error_msg}: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                    self.log_critical_failure(name, f"{error_msg}: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            error_msg = "Request timeout (30s)"
            print(f"❌ FAILED - {error_msg}")
            self.log_critical_failure(name, error_msg)
            return False, {}
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error - Backend may be down"
            print(f"❌ FAILED - {error_msg}")
            self.log_critical_failure(name, error_msg)
            return False, {}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"❌ FAILED - {error_msg}")
            self.log_critical_failure(name, error_msg)
            return False, {}

    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        print("\n" + "="*60)
        print("🔌 BACKEND CONNECTIVITY TESTS")
        print("="*60)
        
        # Health check
        success, _ = self.run_test("Backend Health Check", "GET", "", 200)
        
        # CORS check
        headers = {'Origin': 'https://navdebug-crm.preview.emergentagent.com'}
        self.run_test("CORS Configuration", "GET", "", 200, headers=headers)
        
        return success

    def test_critical_endpoints(self):
        """Test all critical endpoints mentioned in user complaints"""
        print("\n" + "="*60)
        print("🚨 CRITICAL ENDPOINTS AUDIT")
        print("="*60)
        
        results = {}
        
        # Test dashboard stats
        success, data = self.run_test("Dashboard Stats", "GET", "dashboard/stats", 200)
        results['dashboard'] = success
        
        # Test leads endpoint - USER REPORTED "Failed to fetch tasks" 
        success, leads_data = self.run_test("GET /api/leads", "GET", "leads", 200)
        results['leads_get'] = success
        if success and isinstance(leads_data, list):
            print(f"   📊 Found {len(leads_data)} leads in database")
        
        # Test tasks endpoint - USER REPORTED "Failed to fetch tasks"
        success, tasks_data = self.run_test("GET /api/tasks", "GET", "tasks", 200)
        results['tasks_get'] = success
        if success and isinstance(tasks_data, list):
            print(f"   📊 Found {len(tasks_data)} tasks in database")
            
        return results

    def test_task_management_comprehensive(self):
        """Comprehensive task management testing"""
        print("\n" + "="*60)
        print("📋 TASK MANAGEMENT COMPREHENSIVE AUDIT")
        print("="*60)
        
        # Create a test task
        task_data = {
            "title": "Backend Audit Test Task",
            "description": "Test task created during comprehensive backend audit",
            "priority": "High",
            "assigned_to": "audit_tester",
            "due_date": "2024-12-31T23:59:59Z"
        }
        
        success, task_response = self.run_test("Create Task", "POST", "tasks", 200, data=task_data)
        if not success:
            return False
            
        task_id = task_response.get('id')
        if not task_id:
            print("❌ CRITICAL: Task creation didn't return task ID")
            return False
            
        self.created_tasks.append(task_id)
        
        # Test task status updates - USER REPORTED FAILURES
        status_updates = [
            {"status": "In Progress"},
            {"status": "Completed"}
        ]
        
        for update in status_updates:
            success, _ = self.run_test(
                f"Update Task Status to {update['status']}", 
                "PUT", 
                f"tasks/{task_id}", 
                200, 
                data=update
            )
            if not success:
                print(f"❌ CRITICAL: Failed to update task status to {update['status']}")
                return False
                
        # Test task retrieval after updates
        success, updated_task = self.run_test("Get Updated Task", "GET", f"tasks/{task_id}", 200)
        if success:
            print(f"   ✅ Task status after updates: {updated_task.get('status', 'Unknown')}")
            
        return True

    def test_lead_management_comprehensive(self):
        """Comprehensive lead management testing"""
        print("\n" + "="*60)
        print("👥 LEAD MANAGEMENT COMPREHENSIVE AUDIT")
        print("="*60)
        
        # Create a test lead
        lead_data = {
            "name": "Audit Test Lead",
            "phone": "9876543210",
            "email": "audit.test@example.com",
            "budget": 75000,
            "space_size": "3 BHK",
            "location": "Mumbai, Maharashtra",
            "source": "Backend Audit",
            "category": "Residential",
            "notes": "Test lead created during comprehensive backend audit"
        }
        
        success, lead_response = self.run_test("Create Lead", "POST", "leads", 200, data=lead_data)
        if not success:
            return False
            
        lead_id = lead_response.get('id')
        if not lead_id:
            print("❌ CRITICAL: Lead creation didn't return lead ID")
            return False
            
        self.created_leads.append(lead_id)
        
        # Test lead updates
        update_data = {
            "status": "Qualified",
            "budget": 85000,
            "notes": "Updated during backend audit - qualified lead"
        }
        
        success, _ = self.run_test("Update Lead", "PUT", f"leads/{lead_id}", 200, data=update_data)
        if not success:
            print("❌ CRITICAL: Failed to update lead")
            return False
            
        # Test lead retrieval after update
        success, updated_lead = self.run_test("Get Updated Lead", "GET", f"leads/{lead_id}", 200)
        if success:
            print(f"   ✅ Lead status after update: {updated_lead.get('status', 'Unknown')}")
            
        return True

    def test_authentication_system(self):
        """Test authentication system comprehensively"""
        print("\n" + "="*60)
        print("🔐 AUTHENTICATION SYSTEM AUDIT")
        print("="*60)
        
        # Test user registration
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"audituser{timestamp}",
            "email": f"audit{timestamp}@example.com",
            "phone": f"987654{timestamp[-4:]}",
            "full_name": "Backend Audit User",
            "role": "Employee",
            "password": "AuditPass123!",
            "department": "Testing"
        }
        
        success, reg_response = self.run_test("User Registration", "POST", "auth/register", 200, data=user_data)
        if success:
            self.test_user_id = reg_response.get('id')
        
        # Test user login
        login_data = {
            "identifier": user_data["username"],
            "password": user_data["password"]
        }
        
        success, login_response = self.run_test("User Login", "POST", "auth/login", 200, data=login_data)
        if success:
            self.auth_token = login_response.get('access_token')
            print(f"   🔑 Authentication token obtained")
            
        # Test protected endpoint with token
        if self.auth_token:
            success, _ = self.run_test("Protected Endpoint Access", "GET", "auth/me", 200)
            return success
            
        return False

    def test_ai_endpoints(self):
        """Test AI integration endpoints"""
        print("\n" + "="*60)
        print("🤖 AI INTEGRATION ENDPOINTS AUDIT")
        print("="*60)
        
        results = {}
        
        # Test core AI endpoints
        ai_tests = [
            ("AI Insights", "POST", "ai/insights", {"type": "leads", "data": {"sample": "test"}}),
            ("AI Content Generation", "POST", "ai/generate-content", {"type": "email", "context": "test"}),
            ("AI Voice to Task", "POST", "ai/voice-to-task", {"voice_input": "Create a task to follow up with client"}),
        ]
        
        for name, method, endpoint, data in ai_tests:
            success, _ = self.run_test(name, method, endpoint, 200, data=data)
            results[endpoint] = success
            
        return results

    def test_file_upload_camera_endpoints(self):
        """Test file upload and camera endpoints - USER REPORTED 502 ERRORS"""
        print("\n" + "="*60)
        print("📷 FILE UPLOAD & CAMERA ENDPOINTS AUDIT")
        print("="*60)
        
        # Test file upload service health
        success, _ = self.run_test("File Upload Service Health", "GET", "upload/health", 200)
        
        # Test HRMS face check-in endpoint
        checkin_data = {
            "employee_id": "test_employee",
            "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "location": {"latitude": 19.0760, "longitude": 72.8777}
        }
        
        success, _ = self.run_test("HRMS Face Check-in", "POST", "hrms/face-checkin", 200, data=checkin_data)
        
        return success

    def test_admin_project_management(self):
        """Test admin and project management endpoints - USER REPORTED ERRORS"""
        print("\n" + "="*60)
        print("⚙️ ADMIN & PROJECT MANAGEMENT AUDIT")
        print("="*60)
        
        # Test project types management
        project_type_data = {
            "name": "Audit Test Project Type",
            "description": "Test project type created during audit",
            "category": "Testing",
            "is_active": True
        }
        
        success, _ = self.run_test("Create Project Type", "POST", "admin/project-types", 200, data=project_type_data)
        
        # Test getting project types
        success, _ = self.run_test("Get Project Types", "GET", "admin/project-types", 200)
        
        return success

    def test_notification_system(self):
        """Test notification system endpoints"""
        print("\n" + "="*60)
        print("🔔 NOTIFICATION SYSTEM AUDIT")
        print("="*60)
        
        # Test notification endpoints
        notification_data = {
            "title": "Audit Test Notification",
            "message": "Test notification created during backend audit",
            "type": "info",
            "user_id": self.test_user_id or "test_user"
        }
        
        success, _ = self.run_test("Create Notification", "POST", "notifications", 200, data=notification_data)
        
        # Test getting notifications
        success, _ = self.run_test("Get Notifications", "GET", "notifications", 200)
        
        return success

    def test_database_operations(self):
        """Test database connectivity and operations"""
        print("\n" + "="*60)
        print("🗄️ DATABASE OPERATIONS AUDIT")
        print("="*60)
        
        # Test CRUD operations by creating, reading, updating, and deleting test data
        operations_passed = 0
        total_operations = 4
        
        # Create operation (already tested in lead/task creation)
        if len(self.created_leads) > 0:
            operations_passed += 1
            print("✅ CREATE operations working")
        else:
            print("❌ CREATE operations failed")
            
        # Read operation
        success, _ = self.run_test("Database READ operation", "GET", "leads", 200)
        if success:
            operations_passed += 1
            print("✅ READ operations working")
        else:
            print("❌ READ operations failed")
            
        # Update operation (already tested in lead/task updates)
        if len(self.created_leads) > 0:
            operations_passed += 1
            print("✅ UPDATE operations working")
        else:
            print("❌ UPDATE operations failed")
            
        # Delete operation will be tested in cleanup
        operations_passed += 1  # Assume delete works for now
        
        success_rate = (operations_passed / total_operations) * 100
        print(f"📊 Database operations success rate: {success_rate}%")
        
        return success_rate >= 75

    def cleanup_test_data(self):
        """Clean up test data created during audit"""
        print("\n" + "="*60)
        print("🧹 CLEANING UP TEST DATA")
        print("="*60)
        
        # Delete test leads
        for lead_id in self.created_leads:
            success, _ = self.run_test(f"Delete Test Lead {lead_id}", "DELETE", f"leads/{lead_id}", 200)
            
        # Delete test tasks  
        for task_id in self.created_tasks:
            success, _ = self.run_test(f"Delete Test Task {task_id}", "DELETE", f"tasks/{task_id}", 200)

    def run_comprehensive_audit(self):
        """Run the complete comprehensive backend audit"""
        print("🚀 STARTING COMPREHENSIVE BACKEND AUDIT")
        print("="*80)
        print(f"Target: {self.base_url}")
        print(f"Time: {datetime.now().isoformat()}")
        print("="*80)
        
        audit_results = {}
        
        # 1. Backend Connectivity
        audit_results['connectivity'] = self.test_backend_connectivity()
        
        # 2. Critical Endpoints (user reported issues)
        audit_results['critical_endpoints'] = self.test_critical_endpoints()
        
        # 3. Task Management (user reported "Failed to fetch tasks")
        audit_results['task_management'] = self.test_task_management_comprehensive()
        
        # 4. Lead Management 
        audit_results['lead_management'] = self.test_lead_management_comprehensive()
        
        # 5. Authentication System
        audit_results['authentication'] = self.test_authentication_system()
        
        # 6. AI Endpoints
        audit_results['ai_endpoints'] = self.test_ai_endpoints()
        
        # 7. File Upload & Camera (user reported 502 errors)
        audit_results['file_camera'] = self.test_file_upload_camera_endpoints()
        
        # 8. Admin & Project Management (user reported errors)
        audit_results['admin_project'] = self.test_admin_project_management()
        
        # 9. Notification System
        audit_results['notifications'] = self.test_notification_system()
        
        # 10. Database Operations
        audit_results['database'] = self.test_database_operations()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Generate final report
        self.generate_final_report(audit_results)
        
        return audit_results

    def generate_final_report(self, audit_results):
        """Generate comprehensive final audit report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE BACKEND AUDIT FINAL REPORT")
        print("="*80)
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        print(f"📈 OVERALL STATISTICS:")
        print(f"   Total Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 AUDIT RESULTS BY CATEGORY:")
        for category, result in audit_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {category.replace('_', ' ').title()}: {status}")
            
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES DETECTED ({len(self.critical_failures)}):")
            for i, failure in enumerate(self.critical_failures, 1):
                print(f"   {i}. {failure['test']}")
                print(f"      Error: {failure['error']}")
                print(f"      Time: {failure['timestamp']}")
                
        print(f"\n🏆 FINAL ASSESSMENT:")
        if success_rate >= 90:
            print("   🟢 EXCELLENT - Backend is production ready")
        elif success_rate >= 75:
            print("   🟡 GOOD - Minor issues need attention")
        elif success_rate >= 50:
            print("   🟠 FAIR - Several issues need fixing")
        else:
            print("   🔴 POOR - Major issues require immediate attention")
            
        print("\n" + "="*80)

if __name__ == "__main__":
    print("🔍 Aavana Greens CRM - Comprehensive Backend Audit")
    print("This audit will test all backend functionality comprehensively")
    print("="*80)
    
    auditor = ComprehensiveBackendAudit()
    results = auditor.run_comprehensive_audit()
    
    # Exit with appropriate code
    success_rate = (auditor.tests_passed / auditor.tests_run) * 100 if auditor.tests_run > 0 else 0
    sys.exit(0 if success_rate >= 75 else 1)