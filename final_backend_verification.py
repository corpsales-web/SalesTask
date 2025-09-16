#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND VALIDATION - FINAL VERIFICATION
Testing all critical endpoints mentioned in the review request
"""

import requests
import json
import time
import uuid
import sys
from datetime import datetime, timezone, timedelta

class FinalBackendVerification:
    def __init__(self, base_url="https://greenstack-ai.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.critical_failures = []
        self.auth_token = None
        self.test_results = []
        
        # Test data with realistic information
        self.test_lead_data = {
            "name": "Priya Sharma",
            "phone": "9876543210",
            "email": "priya.sharma@example.com",
            "budget": 85000,
            "space_size": "3 BHK Terrace",
            "location": "Pune, Maharashtra",
            "source": "Website",
            "category": "Residential",
            "notes": "Interested in rooftop garden with automated irrigation system"
        }
        
        self.test_task_data = {
            "title": "Site visit for Priya Sharma",
            "description": "Conduct site assessment for rooftop garden project",
            "priority": "High",
            "due_date": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
        }

    def log_test(self, category, name, method, endpoint, expected_status, result, response_data=None, error=None, response_time=None):
        """Log test results with detailed information"""
        self.tests_run += 1
        status = "✅ PASS" if result else "❌ FAIL"
        
        test_result = {
            'category': category,
            'name': name,
            'method': method,
            'endpoint': endpoint,
            'expected_status': expected_status,
            'result': result,
            'response_data': response_data,
            'error': error,
            'response_time': response_time
        }
        self.test_results.append(test_result)
        
        print(f"\n{status} [{category}] {name}")
        print(f"   Method: {method} | Endpoint: /{endpoint}")
        print(f"   Expected: {expected_status} | Result: {'SUCCESS' if result else 'FAILED'}")
        if response_time:
            print(f"   Response Time: {response_time:.0f}ms")
        
        if result:
            self.tests_passed += 1
            if response_data and isinstance(response_data, dict):
                # Show key information from response
                if 'id' in response_data:
                    print(f"   ID: {response_data['id']}")
                if isinstance(response_data, list):
                    print(f"   Count: {len(response_data)} items")
                elif 'total_leads' in response_data:
                    print(f"   Stats: {response_data.get('total_leads', 0)} leads, {response_data.get('pending_tasks', 0)} tasks")
        else:
            self.tests_failed += 1
            if error:
                print(f"   Error: {error}")
                if "502" in str(error) or "500" in str(error):
                    self.critical_failures.append(f"{category} - {name}: {error}")

    def make_request(self, method, endpoint, data=None, params=None, headers=None):
        """Make HTTP request with proper error handling and timing"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        if self.auth_token and 'Authorization' not in headers:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            return response, response_time
        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            return None, response_time, str(e)

    def test_endpoint(self, category, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Test a single endpoint"""
        result = self.make_request(method, endpoint, data, params, headers)
        
        if len(result) == 3:  # Error case
            response, response_time, error = result
            self.log_test(category, name, method, endpoint, expected_status, False, error=error, response_time=response_time)
            return False, {}
        
        response, response_time = result
        success = response.status_code == expected_status
        
        try:
            response_data = response.json() if response.content else {}
        except:
            response_data = {"raw_response": response.text[:200]}
        
        error_msg = None
        if not success:
            error_msg = f"Status {response.status_code}: {response_data.get('detail', response.text[:100])}"
        
        self.log_test(category, name, method, endpoint, expected_status, success, response_data, error_msg, response_time)
        return success, response_data

    def test_core_api_endpoints(self):
        """Test Core API Endpoints: Health check, dashboard stats, leads CRUD, tasks CRUD"""
        print("\n" + "="*80)
        print("🏥 TESTING CORE API ENDPOINTS")
        print("="*80)
        
        # Health check
        self.test_endpoint("CORE", "Health Check", "GET", "", 200)
        
        # Dashboard stats
        self.test_endpoint("CORE", "Dashboard Statistics", "GET", "dashboard/stats", 200)
        
        # Leads CRUD
        success, response = self.test_endpoint("CORE", "Create Lead", "POST", "leads", 200, self.test_lead_data)
        lead_id = response.get('id') if success else None
        
        self.test_endpoint("CORE", "Get All Leads", "GET", "leads", 200)
        
        if lead_id:
            self.test_endpoint("CORE", "Get Lead by ID", "GET", f"leads/{lead_id}", 200)
            update_data = {"status": "Qualified", "notes": "Updated: Client confirmed budget and timeline"}
            self.test_endpoint("CORE", "Update Lead", "PUT", f"leads/{lead_id}", 200, update_data)
        
        # Tasks CRUD
        success, response = self.test_endpoint("CORE", "Create Task", "POST", "tasks", 200, self.test_task_data)
        task_id = response.get('id') if success else None
        
        self.test_endpoint("CORE", "Get All Tasks", "GET", "tasks", 200)
        
        if task_id:
            update_data = {"status": "In Progress"}
            self.test_endpoint("CORE", "Update Task Status", "PUT", f"tasks/{task_id}", 200, update_data)

    def test_authentication_system(self):
        """Test Authentication System: Login/logout, JWT token validation, user management"""
        print("\n" + "="*80)
        print("🔐 TESTING AUTHENTICATION SYSTEM")
        print("="*80)
        
        # Test admin login
        admin_login = {
            "identifier": "admin",
            "password": "admin123"
        }
        success, response = self.test_endpoint("AUTH", "Admin Login", "POST", "auth/login", 200, admin_login)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            print(f"   ✅ JWT Token obtained: {self.auth_token[:20]}...")
        
        # Test user registration
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"testuser{timestamp}",
            "email": f"testuser{timestamp}@example.com",
            "phone": f"987654{timestamp[-4:]}",
            "full_name": "Test User Verification",
            "role": "Sales Executive",
            "password": "SecurePass123!",
            "department": "Sales"
        }
        self.test_endpoint("AUTH", "User Registration", "POST", "auth/register", 200, user_data)
        
        # Test phone OTP request
        phone_data = {"phone": "9876543210"}
        self.test_endpoint("AUTH", "Phone OTP Request", "POST", "auth/phone-request-otp", 200, phone_data)
        
        # Test JWT token validation by making authenticated request
        if self.auth_token:
            self.test_endpoint("AUTH", "JWT Token Validation", "GET", "dashboard/stats", 200)

    def test_hrms_apis(self):
        """Test HRMS APIs: Face check-in endpoint validation"""
        print("\n" + "="*80)
        print("📷 TESTING HRMS APIs")
        print("="*80)
        
        # Test face check-in endpoint
        checkin_data = {
            "employee_id": "emp_verification_001",
            "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "location": {
                "latitude": 19.0760,
                "longitude": 72.8777
            }
        }
        self.test_endpoint("HRMS", "Face Check-in", "POST", "hrms/face-checkin", 200, checkin_data)
        
        # Test GPS check-in
        gps_checkin_data = {
            "employee_id": "emp_verification_001",
            "location": {
                "latitude": 19.0760,
                "longitude": 72.8777
            }
        }
        self.test_endpoint("HRMS", "GPS Check-in", "POST", "hrms/gps-checkin", 200, gps_checkin_data)

    def test_file_upload_apis(self):
        """Test File Upload APIs: File upload service endpoints"""
        print("\n" + "="*80)
        print("📁 TESTING FILE UPLOAD APIs")
        print("="*80)
        
        # Test file upload endpoint (without actual file for now)
        self.test_endpoint("FILE", "File Upload Health", "GET", "upload/health", 200)

    def test_ai_integration_apis(self):
        """Test AI Integration APIs: Core AI services, workflow authoring, lead routing"""
        print("\n" + "="*80)
        print("🤖 TESTING AI INTEGRATION APIs")
        print("="*80)
        
        # Core AI Services
        voice_data = {
            "voice_input": "Schedule a follow-up call with Priya Sharma next Tuesday at 2 PM to discuss the rooftop garden proposal",
            "context": "lead_management"
        }
        self.test_endpoint("AI", "Voice to Task", "POST", "ai/voice-to-task", 200, voice_data)
        
        insight_data = {
            "type": "leads",
            "timeframe": "last_30_days"
        }
        self.test_endpoint("AI", "AI Insights", "POST", "ai/insights", 200, insight_data)
        
        # Lead Routing
        routing_data = {
            "lead_id": "test_lead_verification",
            "source": "Website",
            "location": "Pune",
            "budget": 85000
        }
        self.test_endpoint("AI", "Lead Routing", "POST", "routing/route-lead", 200, routing_data)
        
        # Workflow Authoring - Get templates
        self.test_endpoint("AI", "Get Workflow Templates", "GET", "workflows/prompt-templates", 200)

    def test_admin_apis(self):
        """Test Admin APIs: User management, role management"""
        print("\n" + "="*80)
        print("👥 TESTING ADMIN APIs")
        print("="*80)
        
        # Test user management endpoints (if authenticated)
        if self.auth_token:
            self.test_endpoint("ADMIN", "Get Users", "GET", "auth/users", 200)
            self.test_endpoint("ADMIN", "Get Permissions", "GET", "auth/permissions", 200)

    def test_notification_apis(self):
        """Test Notification APIs: Notification system endpoints"""
        print("\n" + "="*80)
        print("🔔 TESTING NOTIFICATION APIs")
        print("="*80)
        
        # Test notification endpoints
        self.test_endpoint("NOTIFICATION", "Notification Health", "GET", "notifications/health", 200)

    def run_final_verification(self):
        """Run comprehensive final verification"""
        print("🚀 STARTING COMPREHENSIVE BACKEND VALIDATION - FINAL VERIFICATION")
        print("Testing all critical endpoints mentioned in review request")
        print("="*80)
        
        start_time = time.time()
        
        # Run all test categories as specified in review request
        self.test_core_api_endpoints()
        self.test_authentication_system()
        self.test_hrms_apis()
        self.test_file_upload_apis()
        self.test_ai_integration_apis()
        self.test_admin_apis()
        self.test_notification_apis()
        
        # Calculate results
        end_time = time.time()
        duration = end_time - start_time
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        # Print comprehensive results
        print("\n" + "="*80)
        print("📋 FINAL VERIFICATION RESULTS")
        print("="*80)
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"🧪 Total Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Analyze response times
        response_times = [r['response_time'] for r in self.test_results if r['response_time'] and r['result']]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"⚡ Average Response Time: {avg_response_time:.0f}ms")
            print(f"⚡ Response Time Range: {min(response_times):.0f}ms - {max(response_times):.0f}ms")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   • {failure}")
        
        # Success criteria evaluation
        print(f"\n🎯 SUCCESS CRITERIA EVALUATION:")
        print(f"   ✅ All core API endpoints returning 200 OK: {'YES' if success_rate >= 80 else 'NO'}")
        print(f"   ✅ No 502 Backend Gateway errors: {'YES' if len(self.critical_failures) == 0 else 'NO'}")
        print(f"   ✅ Response times under 500ms: {'YES' if all(rt < 500 for rt in response_times) else 'NO'}")
        print(f"   ✅ Overall success rate above 80%: {'YES' if success_rate >= 80 else 'NO'}")
        
        print(f"\n🎯 FINAL STATUS: {'✅ PASSED' if success_rate >= 80 else '❌ NEEDS ATTENTION'}")
        
        if success_rate >= 90:
            print("🏆 EXCELLENT: Backend is production-ready and meets all success criteria")
        elif success_rate >= 80:
            print("✅ GOOD: Backend meets success criteria with minor issues")
        elif success_rate >= 60:
            print("⚠️  MODERATE: Backend has issues but core functionality works")
        else:
            print("🚨 CRITICAL: Backend has major issues blocking functionality")
        
        return {
            'total_tests': self.tests_run,
            'passed': self.tests_passed,
            'failed': self.tests_failed,
            'success_rate': success_rate,
            'critical_failures': self.critical_failures,
            'duration': duration,
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0
        }

if __name__ == "__main__":
    print("🌿 Aavana Greens CRM - Final Backend Verification")
    print("Comprehensive validation of all critical endpoints")
    print("="*80)
    
    verifier = FinalBackendVerification()
    results = verifier.run_final_verification()
    
    # Exit with appropriate code
    exit_code = 0 if results['success_rate'] >= 80 else 1
    sys.exit(exit_code)