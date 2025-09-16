#!/usr/bin/env python3
"""
PRIORITY BACKEND HEALTH CHECK - Post Frontend Crisis Validation
Testing 8 critical areas: Health Check, Authentication, Database, API Performance, 
HRMS Endpoints, AI Stack, File Upload, Notification APIs
"""

import requests
import json
import time
import uuid
import sys
from datetime import datetime, timezone, timedelta
import base64
import os

class PriorityBackendHealthCheck:
    def __init__(self, base_url="https://greenstack-ai.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.critical_failures = []
        self.auth_token = None
        self.test_user_id = None
        self.performance_metrics = []
        
        # Test data for health check
        self.test_lead_data = {
            "name": "Health Check Lead",
            "phone": "9876543210",
            "email": "healthcheck@example.com",
            "budget": 50000,
            "space_size": "2 BHK",
            "location": "Mumbai, Maharashtra",
            "source": "Health Check",
            "category": "Test",
            "notes": "Backend health check validation lead"
        }
        
        self.test_task_data = {
            "title": "Health Check Task",
            "description": "Backend validation task",
            "priority": "Medium",
            "ai_generated": False
        }

    def log_test(self, test_name, success, details="", response_time=None):
        """Log test results with performance metrics"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        
        if response_time:
            self.performance_metrics.append({
                'test': test_name,
                'response_time': response_time,
                'success': success
            })
            perf_info = f" ({response_time:.0f}ms)"
        else:
            perf_info = ""
            
        print(f"{status}: {test_name}{perf_info}")
        if details:
            print(f"    Details: {details}")
        
        if success:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            if "critical" in test_name.lower() or "health" in test_name.lower():
                self.critical_failures.append(f"{test_name}: {details}")

    def make_request(self, method, endpoint, data=None, headers=None, timeout=10):
        """Make HTTP request with performance tracking"""
        url = f"{self.base_url}{endpoint}"
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        if self.auth_token and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = (time.time() - start_time) * 1000
            return response, response_time
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return None, response_time

    # 1. HEALTH CHECK - Verify all core endpoints are working
    def test_core_health_check(self):
        """Test basic API health and connectivity"""
        print("\n🏥 1. CORE HEALTH CHECK")
        
        # Basic API root
        response, rt = self.make_request("GET", "/")
        if response and response.status_code == 200:
            self.log_test("API Root Health Check", True, "Backend API responding", rt)
        else:
            self.log_test("API Root Health Check", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Dashboard stats (core business metrics)
        response, rt = self.make_request("GET", "/dashboard/stats")
        if response and response.status_code == 200:
            stats = response.json()
            self.log_test("Dashboard Stats Health", True, f"Leads: {stats.get('total_leads', 0)}, Tasks: {stats.get('pending_tasks', 0)}", rt)
        else:
            self.log_test("Dashboard Stats Health", False, f"Status: {response.status_code if response else 'No response'}", rt)

    # 2. AUTHENTICATION - Test JWT-based login system
    def test_authentication_system(self):
        """Test JWT authentication system"""
        print("\n🔐 2. AUTHENTICATION SYSTEM")
        
        # Test admin login
        login_data = {
            "identifier": "admin",
            "password": "admin123"
        }
        
        response, rt = self.make_request("POST", "/auth/login", login_data)
        if response and response.status_code == 200:
            auth_data = response.json()
            if "access_token" in auth_data:
                self.auth_token = auth_data["access_token"]
                self.test_user_id = auth_data.get("user", {}).get("id")
                self.log_test("JWT Authentication", True, f"Token received, expires in {auth_data.get('expires_in', 'N/A')}s", rt)
            else:
                self.log_test("JWT Authentication", False, "No access token in response", rt)
        else:
            self.log_test("JWT Authentication", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Test token validation by accessing protected endpoint
        if self.auth_token:
            response, rt = self.make_request("GET", "/users/me")
            if response and response.status_code == 200:
                user_data = response.json()
                self.log_test("JWT Token Validation", True, f"User: {user_data.get('username', 'N/A')}", rt)
            else:
                self.log_test("JWT Token Validation", False, f"Status: {response.status_code if response else 'No response'}", rt)

    # 3. DATABASE - Confirm MongoDB connectivity and CRUD operations
    def test_database_operations(self):
        """Test MongoDB CRUD operations"""
        print("\n🗄️ 3. DATABASE CONNECTIVITY & CRUD")
        
        # CREATE - Test lead creation
        response, rt = self.make_request("POST", "/leads", self.test_lead_data)
        if response and response.status_code == 200:
            lead_data = response.json()
            test_lead_id = lead_data.get("id")
            self.log_test("Database CREATE (Lead)", True, f"Lead ID: {test_lead_id}", rt)
        else:
            self.log_test("Database CREATE (Lead)", False, f"Status: {response.status_code if response else 'No response'}", rt)
            return
        
        # READ - Test lead retrieval
        response, rt = self.make_request("GET", f"/leads/{test_lead_id}")
        if response and response.status_code == 200:
            lead = response.json()
            self.log_test("Database READ (Lead)", True, f"Retrieved: {lead.get('name', 'N/A')}", rt)
        else:
            self.log_test("Database READ (Lead)", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # UPDATE - Test lead update
        update_data = {"notes": "Updated during health check", "status": "Qualified"}
        response, rt = self.make_request("PUT", f"/leads/{test_lead_id}", update_data)
        if response and response.status_code == 200:
            updated_lead = response.json()
            self.log_test("Database UPDATE (Lead)", True, f"Status: {updated_lead.get('status', 'N/A')}", rt)
        else:
            self.log_test("Database UPDATE (Lead)", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Test task CRUD
        response, rt = self.make_request("POST", "/tasks", self.test_task_data)
        if response and response.status_code == 200:
            task_data = response.json()
            test_task_id = task_data.get("id")
            self.log_test("Database CREATE (Task)", True, f"Task ID: {test_task_id}", rt)
            
            # Test task status update
            status_update = {"status": "In Progress"}
            response, rt = self.make_request("PUT", f"/tasks/{test_task_id}", status_update)
            if response and response.status_code == 200:
                self.log_test("Database UPDATE (Task Status)", True, "Status updated to In Progress", rt)
            else:
                self.log_test("Database UPDATE (Task Status)", False, f"Status: {response.status_code if response else 'No response'}", rt)
        else:
            self.log_test("Database CREATE (Task)", False, f"Status: {response.status_code if response else 'No response'}", rt)

    # 4. API PERFORMANCE - Validate response times are optimal
    def test_api_performance(self):
        """Test API performance and response times"""
        print("\n⚡ 4. API PERFORMANCE VALIDATION")
        
        # Test multiple endpoints for performance
        performance_tests = [
            ("GET", "/leads", "Leads List Performance"),
            ("GET", "/tasks", "Tasks List Performance"),
            ("GET", "/dashboard/stats", "Dashboard Performance"),
        ]
        
        total_response_time = 0
        performance_passed = 0
        
        for method, endpoint, test_name in performance_tests:
            response, rt = self.make_request(method, endpoint)
            if response and response.status_code == 200:
                # Consider under 1000ms as good performance
                is_fast = rt < 1000
                self.log_test(test_name, is_fast, f"Response time: {rt:.0f}ms {'(Good)' if is_fast else '(Slow)'}", rt)
                if is_fast:
                    performance_passed += 1
                total_response_time += rt
            else:
                self.log_test(test_name, False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Overall performance summary
        avg_response_time = total_response_time / len(performance_tests) if performance_tests else 0
        performance_score = (performance_passed / len(performance_tests)) * 100 if performance_tests else 0
        
        self.log_test("Overall API Performance", performance_score >= 70, 
                     f"Average: {avg_response_time:.0f}ms, Score: {performance_score:.0f}%")

    # 5. HRMS ENDPOINTS - Test face check-in and GPS endpoints for Priority 1
    def test_hrms_endpoints(self):
        """Test HRMS endpoints including face check-in"""
        print("\n👥 5. HRMS ENDPOINTS (Priority 1)")
        
        # Test face check-in endpoint
        face_checkin_data = {
            "employee_id": "test_employee_123",
            "location": {"latitude": 19.0760, "longitude": 72.8777},
            "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        }
        
        response, rt = self.make_request("POST", "/hrms/face-checkin", face_checkin_data)
        if response and response.status_code == 200:
            self.log_test("HRMS Face Check-in", True, "Face check-in endpoint responding", rt)
        else:
            self.log_test("HRMS Face Check-in", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Test GPS check-in endpoint
        gps_checkin_data = {
            "employee_id": "test_employee_123",
            "location": {"latitude": 19.0760, "longitude": 72.8777},
            "address": "Mumbai, Maharashtra"
        }
        
        response, rt = self.make_request("POST", "/hrms/gps-checkin", gps_checkin_data)
        if response and response.status_code == 200:
            self.log_test("HRMS GPS Check-in", True, "GPS check-in endpoint responding", rt)
        else:
            self.log_test("HRMS GPS Check-in", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Test employee attendance retrieval
        response, rt = self.make_request("GET", "/hrms/attendance")
        if response and response.status_code == 200:
            attendance_data = response.json()
            self.log_test("HRMS Attendance Retrieval", True, f"Records found: {len(attendance_data) if isinstance(attendance_data, list) else 'N/A'}", rt)
        else:
            self.log_test("HRMS Attendance Retrieval", False, f"Status: {response.status_code if response else 'No response'}", rt)

    # 6. AI STACK - Quick validation of key AI endpoints
    def test_ai_stack(self):
        """Test key AI endpoints"""
        print("\n🤖 6. AI STACK VALIDATION")
        
        # Test AI insights endpoint
        insights_data = {
            "type": "leads",
            "query": "Provide insights on lead conversion"
        }
        
        response, rt = self.make_request("POST", "/ai/insights", insights_data)
        if response and response.status_code == 200:
            self.log_test("AI Insights", True, "AI insights endpoint responding", rt)
        else:
            self.log_test("AI Insights", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Test AI content generation
        content_data = {
            "type": "email",
            "context": "Follow up with potential client",
            "tone": "professional"
        }
        
        response, rt = self.make_request("POST", "/ai/generate-content", content_data)
        if response and response.status_code == 200:
            self.log_test("AI Content Generation", True, "AI content generation responding", rt)
        else:
            self.log_test("AI Content Generation", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Test AI lead scoring
        response, rt = self.make_request("POST", "/ai/crm/smart-lead-scoring?lead_id=test_lead_123")
        if response and response.status_code == 200:
            self.log_test("AI Lead Scoring", True, "AI lead scoring responding", rt)
        else:
            self.log_test("AI Lead Scoring", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Test Aavana 2.0 AI Assistant
        aavana_data = {
            "message": "Hello, test the AI assistant",
            "language": "english",
            "channel": "web",
            "user_id": "health_check_user"
        }
        
        response, rt = self.make_request("POST", "/ai/aavana-2-0/chat", aavana_data)
        if response and response.status_code == 200:
            self.log_test("Aavana 2.0 AI Assistant", True, "AI assistant responding", rt)
        else:
            self.log_test("Aavana 2.0 AI Assistant", False, f"Status: {response.status_code if response else 'No response'}", rt)

    # 7. FILE UPLOAD - Test file upload functionality
    def test_file_upload(self):
        """Test file upload functionality"""
        print("\n📁 7. FILE UPLOAD FUNCTIONALITY")
        
        # Test file upload endpoint availability
        response, rt = self.make_request("GET", "/upload/status")
        if response and response.status_code == 200:
            self.log_test("File Upload Service Status", True, "Upload service responding", rt)
        else:
            self.log_test("File Upload Service Status", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Test file upload capabilities (without actually uploading)
        upload_data = {
            "file_type": "image",
            "file_size": 1024,
            "file_name": "test_image.jpg"
        }
        
        response, rt = self.make_request("POST", "/upload/validate", upload_data)
        if response and response.status_code == 200:
            self.log_test("File Upload Validation", True, "Upload validation working", rt)
        else:
            self.log_test("File Upload Validation", False, f"Status: {response.status_code if response else 'No response'}", rt)

    # 8. NOTIFICATION APIS - Validate notification system backend
    def test_notification_apis(self):
        """Test notification system backend"""
        print("\n🔔 8. NOTIFICATION SYSTEM")
        
        # Test notification creation
        notification_data = {
            "title": "Health Check Notification",
            "message": "Backend health check notification test",
            "type": "info",
            "user_id": self.test_user_id or "test_user"
        }
        
        response, rt = self.make_request("POST", "/notifications", notification_data)
        if response and response.status_code == 200:
            self.log_test("Notification Creation", True, "Notification created successfully", rt)
        else:
            self.log_test("Notification Creation", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Test notification retrieval
        response, rt = self.make_request("GET", "/notifications")
        if response and response.status_code == 200:
            notifications = response.json()
            self.log_test("Notification Retrieval", True, f"Retrieved {len(notifications) if isinstance(notifications, list) else 'N/A'} notifications", rt)
        else:
            self.log_test("Notification Retrieval", False, f"Status: {response.status_code if response else 'No response'}", rt)
        
        # Test WhatsApp notification capability
        whatsapp_data = {
            "phone": "9876543210",
            "message": "Health check WhatsApp notification",
            "type": "test"
        }
        
        response, rt = self.make_request("POST", "/notifications/whatsapp", whatsapp_data)
        if response and response.status_code == 200:
            self.log_test("WhatsApp Notification", True, "WhatsApp notification endpoint responding", rt)
        else:
            self.log_test("WhatsApp Notification", False, f"Status: {response.status_code if response else 'No response'}", rt)

    def run_health_check(self):
        """Run complete priority backend health check"""
        print("🎯 PRIORITY BACKEND HEALTH CHECK - POST FRONTEND CRISIS VALIDATION")
        print("=" * 80)
        print(f"Testing Backend: {self.base_url}")
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        
        # Run all health check tests
        self.test_core_health_check()
        self.test_authentication_system()
        self.test_database_operations()
        self.test_api_performance()
        self.test_hrms_endpoints()
        self.test_ai_stack()
        self.test_file_upload()
        self.test_notification_apis()
        
        # Generate summary report
        self.generate_health_report()

    def generate_health_report(self):
        """Generate comprehensive health check report"""
        print("\n" + "=" * 80)
        print("🏥 PRIORITY BACKEND HEALTH CHECK REPORT")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Performance metrics summary
        if self.performance_metrics:
            avg_response_time = sum(m['response_time'] for m in self.performance_metrics) / len(self.performance_metrics)
            fast_responses = sum(1 for m in self.performance_metrics if m['response_time'] < 1000)
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.0f}ms")
            print(f"   Fast Responses (<1000ms): {fast_responses}/{len(self.performance_metrics)}")
        
        # Critical failures
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"   ❌ {failure}")
        else:
            print(f"\n✅ NO CRITICAL FAILURES DETECTED")
        
        # Health status determination
        if success_rate >= 90:
            health_status = "🟢 EXCELLENT"
        elif success_rate >= 75:
            health_status = "🟡 GOOD"
        elif success_rate >= 50:
            health_status = "🟠 FAIR"
        else:
            health_status = "🔴 POOR"
        
        print(f"\n🎯 BACKEND HEALTH STATUS: {health_status}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   ✅ Backend is in excellent health - all systems operational")
        elif success_rate >= 75:
            print("   ⚠️ Minor issues detected - monitor and address failed tests")
        else:
            print("   🚨 Significant issues detected - immediate attention required")
            print("   🔧 Review critical failures and fix high-priority issues")
        
        print("=" * 80)
        
        return success_rate >= 75  # Return True if health check passes

if __name__ == "__main__":
    health_checker = PriorityBackendHealthCheck()
    
    try:
        health_passed = health_checker.run_health_check()
        sys.exit(0 if health_passed else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Health check failed with error: {str(e)}")
        sys.exit(1)