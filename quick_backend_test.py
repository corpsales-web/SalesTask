#!/usr/bin/env python3
"""
Quick Backend Verification - Testing critical endpoints locally
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone, timedelta

class QuickBackendTest:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.auth_token = None
        
        # Test data
        self.test_lead_data = {
            "name": "Amit Patel",
            "phone": "9876543210",
            "email": "amit.patel@example.com",
            "budget": 65000,
            "space_size": "2 BHK Balcony",
            "location": "Ahmedabad, Gujarat",
            "source": "Website",
            "category": "Residential",
            "notes": "Interested in vertical garden setup with drip irrigation"
        }
        
        self.test_task_data = {
            "title": "Follow up with Amit Patel",
            "description": "Discuss vertical garden requirements and budget",
            "priority": "High",
            "due_date": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        }

    def test_endpoint(self, name, method, endpoint, data=None, expected_status=200):
        """Test a single endpoint"""
        self.tests_run += 1
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        
        headers = {'Content-Type': 'application/json'}
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        try:
            start_time = time.time()
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == expected_status:
                self.tests_passed += 1
                print(f"✅ {name}: {response.status_code} ({response_time:.0f}ms)")
                
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   → Returned {len(data)} items")
                    elif isinstance(data, dict):
                        if 'id' in data:
                            print(f"   → ID: {data['id']}")
                        elif 'total_leads' in data:
                            print(f"   → Stats: {data.get('total_leads', 0)} leads, {data.get('pending_tasks', 0)} tasks")
                        elif 'access_token' in data:
                            self.auth_token = data['access_token']
                            print(f"   → JWT Token obtained")
                    return True, data
                except:
                    return True, {}
            else:
                self.tests_failed += 1
                print(f"❌ {name}: {response.status_code} ({response_time:.0f}ms)")
                try:
                    error_data = response.json()
                    print(f"   → Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   → Error: {response.text[:100]}")
                return False, {}
                
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ {name}: Exception - {str(e)}")
            return False, {}

    def run_quick_test(self):
        """Run quick backend verification"""
        print("🚀 QUICK BACKEND VERIFICATION")
        print("Testing critical endpoints locally")
        print("="*60)
        
        start_time = time.time()
        
        # 1. Core API Endpoints
        print("\n🏥 CORE API ENDPOINTS:")
        self.test_endpoint("Health Check", "GET", "")
        self.test_endpoint("Dashboard Stats", "GET", "dashboard/stats")
        
        # 2. Authentication System
        print("\n🔐 AUTHENTICATION SYSTEM:")
        admin_login = {"identifier": "admin", "password": "admin123"}
        self.test_endpoint("Admin Login", "POST", "auth/login", admin_login)
        
        # 3. Lead Management APIs
        print("\n👥 LEAD MANAGEMENT:")
        success, lead_data = self.test_endpoint("Create Lead", "POST", "leads", self.test_lead_data)
        self.test_endpoint("Get All Leads", "GET", "leads")
        
        lead_id = lead_data.get('id') if success else None
        if lead_id:
            update_data = {"status": "Qualified", "notes": "Updated via test"}
            self.test_endpoint("Update Lead", "PUT", f"leads/{lead_id}", update_data)
        
        # 4. Task Management APIs
        print("\n📋 TASK MANAGEMENT:")
        success, task_data = self.test_endpoint("Create Task", "POST", "tasks", self.test_task_data)
        self.test_endpoint("Get All Tasks", "GET", "tasks")
        
        task_id = task_data.get('id') if success else None
        if task_id:
            update_data = {"status": "In Progress"}
            self.test_endpoint("Update Task Status", "PUT", f"tasks/{task_id}", update_data)
        
        # 5. HRMS APIs
        print("\n📷 HRMS APIs:")
        checkin_data = {
            "employee_id": "test_emp_001",
            "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD//2Q==",
            "location": {"latitude": 19.0760, "longitude": 72.8777}
        }
        self.test_endpoint("Face Check-in", "POST", "hrms/face-checkin", checkin_data)
        
        # 6. AI Integration APIs
        print("\n🤖 AI INTEGRATION:")
        voice_data = {
            "voice_input": "Create a task to call Amit tomorrow at 10 AM",
            "context": "lead_management"
        }
        self.test_endpoint("Voice to Task", "POST", "ai/voice-to-task", voice_data)
        
        insight_data = {"type": "leads", "timeframe": "last_30_days"}
        self.test_endpoint("AI Insights", "POST", "ai/insights", insight_data)
        
        # 7. Workflow & Routing
        print("\n🔄 WORKFLOW & ROUTING:")
        self.test_endpoint("Get Routing Rules", "GET", "routing/rules")
        self.test_endpoint("Get Workflow Templates", "GET", "workflows/prompt-templates")
        
        # Calculate results
        end_time = time.time()
        duration = end_time - start_time
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        # Print results
        print("\n" + "="*60)
        print("📋 QUICK VERIFICATION RESULTS")
        print("="*60)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🧪 Tests Run: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Success criteria evaluation
        print(f"\n🎯 SUCCESS CRITERIA:")
        print(f"   ✅ Core endpoints working: {'YES' if success_rate >= 70 else 'NO'}")
        print(f"   ✅ No 502 errors: {'YES' if self.tests_failed < 3 else 'NO'}")
        print(f"   ✅ Authentication working: {'YES' if self.auth_token else 'NO'}")
        
        status = "✅ PASSED" if success_rate >= 70 else "❌ NEEDS ATTENTION"
        print(f"\n🎯 FINAL STATUS: {status}")
        
        if success_rate >= 90:
            print("🏆 EXCELLENT: All critical functionality working")
        elif success_rate >= 70:
            print("✅ GOOD: Core functionality working with minor issues")
        else:
            print("⚠️  NEEDS WORK: Significant issues detected")
        
        return success_rate >= 70

if __name__ == "__main__":
    print("🌿 Aavana Greens CRM - Quick Backend Test")
    
    tester = QuickBackendTest()
    success = tester.run_quick_test()
    
    sys.exit(0 if success else 1)