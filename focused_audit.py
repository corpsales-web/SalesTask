#!/usr/bin/env python3
"""
Focused Backend Audit - Critical Endpoints Testing
"""

import requests
import json
import time
from datetime import datetime, timezone, timedelta

class FocusedBackendAudit:
    def __init__(self, base_url="https://aavana-greens.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.results = {}

    def test_endpoint(self, category, name, method, endpoint, data=None, params=None):
        """Test a single endpoint"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        self.tests_run += 1
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} [{category}] {name} - Status: {response.status_code}")
            
            if not success and response.status_code in [500, 502]:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text[:100]}")
            
            self.results[f"{category}-{name}"] = {
                'success': success,
                'status_code': response.status_code,
                'category': category
            }
            
            return success, response.json() if response.content else {}
            
        except Exception as e:
            print(f"❌ FAIL [{category}] {name} - Error: {str(e)}")
            self.results[f"{category}-{name}"] = {
                'success': False,
                'status_code': 0,
                'error': str(e),
                'category': category
            }
            return False, {}

    def run_focused_audit(self):
        """Run focused audit on critical endpoints"""
        print("🚀 FOCUSED BACKEND AUDIT - CRITICAL ENDPOINTS")
        print("="*60)
        
        start_time = time.time()
        
        # 1. CORE CONNECTIVITY
        print("\n🔗 CORE CONNECTIVITY")
        self.test_endpoint("CORE", "Health Check", "GET", "")
        self.test_endpoint("CORE", "Dashboard Stats", "GET", "dashboard/stats")
        
        # 2. AUTHENTICATION
        print("\n🔐 AUTHENTICATION")
        admin_login = {"identifier": "admin", "password": "admin123"}
        success, response = self.test_endpoint("AUTH", "Admin Login", "POST", "auth/login", admin_login)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            print("   🔑 Authentication token obtained")
        
        # 3. LEAD MANAGEMENT
        print("\n👥 LEAD MANAGEMENT")
        self.test_endpoint("LEADS", "Get All Leads", "GET", "leads")
        
        lead_data = {
            "name": "Test Lead",
            "phone": "9876543210",
            "email": "test@example.com",
            "budget": 50000,
            "location": "Mumbai"
        }
        success, response = self.test_endpoint("LEADS", "Create Lead", "POST", "leads", lead_data)
        
        # 4. TASK MANAGEMENT
        print("\n📋 TASK MANAGEMENT")
        self.test_endpoint("TASKS", "Get All Tasks", "GET", "tasks")
        
        task_data = {
            "title": "Test Task",
            "description": "Test task description",
            "priority": "High"
        }
        self.test_endpoint("TASKS", "Create Task", "POST", "tasks", task_data)
        
        # 5. HRMS & CAMERA
        print("\n📷 HRMS & CAMERA")
        checkin_data = {
            "employee_id": "test_employee",
            "image_data": "data:image/jpeg;base64,test",
            "location": {"latitude": 19.0760, "longitude": 72.8777}
        }
        self.test_endpoint("HRMS", "Face Check-in", "POST", "hrms/face-checkin", checkin_data)
        
        # 6. AI STACK (Core endpoints)
        print("\n🤖 AI STACK")
        voice_data = {
            "voice_input": "Create a task to call client tomorrow",
            "context": "lead_management"
        }
        self.test_endpoint("AI", "Voice to Task", "POST", "ai/voice-to-task", voice_data)
        
        insight_data = {"type": "leads", "timeframe": "last_30_days"}
        self.test_endpoint("AI", "AI Insights", "POST", "ai/insights", insight_data)
        
        self.test_endpoint("AI", "Smart Lead Scoring", "POST", "ai/crm/smart-lead-scoring", params={"lead_id": "test"})
        self.test_endpoint("AI", "Deal Prediction", "POST", "ai/sales/deal-prediction")
        
        # 7. WORKFLOW & ROUTING
        print("\n🔄 WORKFLOW & ROUTING")
        self.test_endpoint("WORKFLOW", "Get Routing Rules", "GET", "routing/rules")
        self.test_endpoint("WORKFLOW", "Get Prompt Templates", "GET", "workflows/prompt-templates")
        self.test_endpoint("WORKFLOW", "Get Workflows", "GET", "workflows")
        
        # 8. AAVANA 2.0
        print("\n🌐 AAVANA 2.0")
        self.test_endpoint("AAVANA", "Health Check", "GET", "aavana/health")
        
        conversation_data = {
            "message": "Hello, I need help with plants",
            "channel": "in_app_chat",
            "user_id": "test_user",
            "language": "en"
        }
        self.test_endpoint("AAVANA", "English Conversation", "POST", "aavana/conversation", conversation_data)
        
        # Calculate results
        end_time = time.time()
        duration = end_time - start_time
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        # Analyze results by category
        categories = {}
        for test_name, result in self.results.items():
            category = result['category']
            if category not in categories:
                categories[category] = {'passed': 0, 'total': 0}
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['passed'] += 1
        
        # Print results
        print("\n" + "="*60)
        print("📋 FOCUSED AUDIT RESULTS")
        print("="*60)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🧪 Total Tests: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_run - self.tests_passed}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📈 RESULTS BY CATEGORY:")
        for category, stats in categories.items():
            rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status = "✅" if rate >= 70 else "⚠️" if rate >= 50 else "❌"
            print(f"   {status} {category}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        # Critical issues
        critical_failures = []
        for test_name, result in self.results.items():
            if not result['success'] and result.get('status_code', 0) in [500, 502]:
                critical_failures.append(test_name)
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(critical_failures)}):")
            for failure in critical_failures[:5]:  # Show first 5
                print(f"   • {failure}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL STATUS:")
        if success_rate >= 90:
            print("🏆 EXCELLENT: Backend is production-ready")
        elif success_rate >= 70:
            print("✅ GOOD: Backend is functional with minor issues")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Backend has significant issues")
        else:
            print("🚨 CRITICAL: Backend has major blocking issues")
        
        return {
            'success_rate': success_rate,
            'total_tests': self.tests_run,
            'passed': self.tests_passed,
            'categories': categories,
            'critical_failures': critical_failures
        }

if __name__ == "__main__":
    auditor = FocusedBackendAudit()
    results = auditor.run_focused_audit()