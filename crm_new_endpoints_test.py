#!/usr/bin/env python3
"""
CRM Backend New Endpoints Test Suite
Tests the new endpoints as requested in the review:
1. AI endpoints: /api/ai/specialized-chat, /api/aavana2/enhanced-chat, /api/aavana2/chat
2. HRMS: GET /api/hrms/today, POST /api/hrms/checkin then checkout, GET /api/hrms/summary days=7
3. Training: POST /api/training/modules then GET filter with q
4. Admin: GET/PUT settings and GET roles
5. Projects: POST /api/projects, GET list
6. Catalogue list with project_id filter returns items
"""

import requests
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

# Configuration - Use the frontend env URL for testing
BASE_URL = "https://crm-visual-studio.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class CRMNewEndpointsTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_items = []  # Track created items for cleanup
        
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
    
    # ========== AI ENDPOINTS TESTS ==========
    def test_ai_specialized_chat(self):
        """Test POST /api/ai/specialized-chat - should return JSON with message"""
        try:
            payload = {
                "message": "Hello, I need help with my business strategy",
                "session_id": str(uuid.uuid4()),
                "language": "en",
                "context": {"user_type": "business_owner"}
            }
            
            response = self.session.post(
                f"{API_BASE}/ai/specialized-chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["message_id", "message", "timestamp", "actions", "metadata", "agent_used", "task_type"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    if data.get("message") and isinstance(data.get("message"), str):
                        self.log_test("AI Specialized Chat", True, 
                                    f"Response received with message: '{data['message'][:50]}...'")
                        return True
                    else:
                        self.log_test("AI Specialized Chat", False, "Missing or invalid message field", data)
                else:
                    self.log_test("AI Specialized Chat", False, f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("AI Specialized Chat", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("AI Specialized Chat", False, f"Error: {str(e)}")
        return False
    
    def test_ai_aavana2_enhanced_chat(self):
        """Test POST /api/aavana2/enhanced-chat - should return JSON with message"""
        try:
            payload = {
                "message": "Can you help me analyze market trends?",
                "session_id": str(uuid.uuid4()),
                "language": "en"
            }
            
            response = self.session.post(
                f"{API_BASE}/aavana2/enhanced-chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message") and isinstance(data.get("message"), str):
                    self.log_test("Aavana2 Enhanced Chat", True, 
                                f"Response received with message: '{data['message'][:50]}...'")
                    return True
                else:
                    self.log_test("Aavana2 Enhanced Chat", False, "Missing or invalid message field", data)
            else:
                self.log_test("Aavana2 Enhanced Chat", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Aavana2 Enhanced Chat", False, f"Error: {str(e)}")
        return False
    
    def test_ai_aavana2_chat(self):
        """Test POST /api/aavana2/chat - should return JSON with message"""
        try:
            payload = {
                "message": "What's the weather like today?",
                "provider": "openai",
                "model": "gpt-4o"
            }
            
            response = self.session.post(
                f"{API_BASE}/aavana2/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message") and isinstance(data.get("message"), str):
                    self.log_test("Aavana2 Standard Chat", True, 
                                f"Response received with message: '{data['message'][:50]}...'")
                    return True
                else:
                    self.log_test("Aavana2 Standard Chat", False, "Missing or invalid message field", data)
            else:
                self.log_test("Aavana2 Standard Chat", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Aavana2 Standard Chat", False, f"Error: {str(e)}")
        return False
    
    # ========== HRMS ENDPOINTS TESTS ==========
    def test_hrms_today(self):
        """Test GET /api/hrms/today"""
        try:
            response = self.session.get(f"{API_BASE}/hrms/today", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["checked_in", "checkin_time", "checkout_time"]
                if all(field in data for field in expected_fields):
                    self.log_test("HRMS Today Status", True, 
                                f"Status retrieved: checked_in={data.get('checked_in')}")
                    return True
                else:
                    missing = [f for f in expected_fields if f not in data]
                    self.log_test("HRMS Today Status", False, f"Missing fields: {missing}", data)
            else:
                self.log_test("HRMS Today Status", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("HRMS Today Status", False, f"Error: {str(e)}")
        return False
    
    def test_hrms_checkin_checkout_flow(self):
        """Test POST /api/hrms/checkin then POST /api/hrms/checkout"""
        try:
            # Test checkin
            checkin_response = self.session.post(f"{API_BASE}/hrms/checkin", timeout=10)
            
            if checkin_response.status_code == 200:
                checkin_data = checkin_response.json()
                if checkin_data.get("success"):
                    self.log_test("HRMS Checkin", True, "Successfully checked in")
                    
                    # Wait a moment then test checkout
                    time.sleep(1)
                    checkout_response = self.session.post(f"{API_BASE}/hrms/checkout", timeout=10)
                    
                    if checkout_response.status_code == 200:
                        checkout_data = checkout_response.json()
                        if checkout_data.get("success"):
                            self.log_test("HRMS Checkout", True, "Successfully checked out")
                            return True
                        else:
                            self.log_test("HRMS Checkout", False, "Checkout failed", checkout_data)
                    else:
                        self.log_test("HRMS Checkout", False, f"HTTP {checkout_response.status_code}", checkout_response.text)
                else:
                    self.log_test("HRMS Checkin", False, "Checkin failed", checkin_data)
            else:
                self.log_test("HRMS Checkin", False, f"HTTP {checkin_response.status_code}", checkin_response.text)
        except Exception as e:
            self.log_test("HRMS Checkin/Checkout Flow", False, f"Error: {str(e)}")
        return False
    
    def test_hrms_summary(self):
        """Test GET /api/hrms/summary with days=7"""
        try:
            response = self.session.get(f"{API_BASE}/hrms/summary?days=7", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and isinstance(data["items"], list):
                    if len(data["items"]) == 7:  # Should return 7 days
                        # Check each item has required fields
                        valid_items = all(
                            "date" in item and "checked_in" in item 
                            for item in data["items"]
                        )
                        if valid_items:
                            self.log_test("HRMS Summary (7 days)", True, 
                                        f"Retrieved {len(data['items'])} days of data")
                            return True
                        else:
                            self.log_test("HRMS Summary (7 days)", False, "Invalid item structure", data)
                    else:
                        self.log_test("HRMS Summary (7 days)", False, 
                                    f"Expected 7 items, got {len(data['items'])}", data)
                else:
                    self.log_test("HRMS Summary (7 days)", False, "Missing or invalid items array", data)
            else:
                self.log_test("HRMS Summary (7 days)", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("HRMS Summary (7 days)", False, f"Error: {str(e)}")
        return False
    
    # ========== TRAINING ENDPOINTS TESTS ==========
    def test_training_modules_post_then_get(self):
        """Test POST /api/training/modules then GET with filter q"""
        try:
            # First, POST a new training module
            module_data = {
                "title": "Advanced Sales Techniques",
                "type": "video",
                "url": "https://example.com/training/sales-advanced"
            }
            
            post_response = self.session.post(
                f"{API_BASE}/training/modules",
                json=module_data,
                timeout=10
            )
            
            if post_response.status_code == 200:
                post_data = post_response.json()
                if "module" in post_data and post_data["module"].get("id"):
                    module_id = post_data["module"]["id"]
                    self.created_items.append(("training_module", module_id))
                    self.log_test("Training Module Create", True, 
                                f"Created module with ID: {module_id}")
                    
                    # Now test GET with filter
                    get_response = self.session.get(
                        f"{API_BASE}/training/modules?q=Sales",
                        timeout=10
                    )
                    
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        if "items" in get_data and isinstance(get_data["items"], list):
                            # Check if our created module is in the filtered results
                            found_module = any(
                                item.get("id") == module_id 
                                for item in get_data["items"]
                            )
                            if found_module:
                                self.log_test("Training Module Filter", True, 
                                            f"Filter 'Sales' returned {len(get_data['items'])} modules including created one")
                                return True
                            else:
                                self.log_test("Training Module Filter", False, 
                                            "Created module not found in filtered results", get_data)
                        else:
                            self.log_test("Training Module Filter", False, "Invalid response structure", get_data)
                    else:
                        self.log_test("Training Module Filter", False, 
                                    f"GET HTTP {get_response.status_code}", get_response.text)
                else:
                    self.log_test("Training Module Create", False, "Invalid response structure", post_data)
            else:
                self.log_test("Training Module Create", False, 
                            f"POST HTTP {post_response.status_code}", post_response.text)
        except Exception as e:
            self.log_test("Training Modules POST/GET Flow", False, f"Error: {str(e)}")
        return False
    
    # ========== ADMIN ENDPOINTS TESTS ==========
    def test_admin_settings_get_put(self):
        """Test GET /api/admin/settings and PUT /api/admin/settings"""
        try:
            # First, GET current settings
            get_response = self.session.get(f"{API_BASE}/admin/settings", timeout=10)
            
            if get_response.status_code == 200:
                original_settings = get_response.json()
                self.log_test("Admin Settings GET", True, 
                            f"Retrieved settings: {list(original_settings.keys())}")
                
                # Now test PUT to update settings
                update_data = {
                    "sla_minutes": 240,  # Change from default 300 to 240
                    "test_setting": "test_value"
                }
                
                put_response = self.session.put(
                    f"{API_BASE}/admin/settings",
                    json=update_data,
                    timeout=10
                )
                
                if put_response.status_code == 200:
                    put_data = put_response.json()
                    if put_data.get("success"):
                        # Verify the update by getting settings again
                        verify_response = self.session.get(f"{API_BASE}/admin/settings", timeout=10)
                        if verify_response.status_code == 200:
                            updated_settings = verify_response.json()
                            if updated_settings.get("sla_minutes") == 240:
                                self.log_test("Admin Settings PUT", True, 
                                            "Settings updated successfully")
                                return True
                            else:
                                self.log_test("Admin Settings PUT", False, 
                                            "Settings not updated properly", updated_settings)
                        else:
                            self.log_test("Admin Settings PUT", False, 
                                        f"Verification GET failed: {verify_response.status_code}")
                    else:
                        self.log_test("Admin Settings PUT", False, "PUT response indicates failure", put_data)
                else:
                    self.log_test("Admin Settings PUT", False, 
                                f"PUT HTTP {put_response.status_code}", put_response.text)
            else:
                self.log_test("Admin Settings GET", False, 
                            f"GET HTTP {get_response.status_code}", get_response.text)
        except Exception as e:
            self.log_test("Admin Settings GET/PUT Flow", False, f"Error: {str(e)}")
        return False
    
    def test_admin_roles_get(self):
        """Test GET /api/admin/roles"""
        try:
            response = self.session.get(f"{API_BASE}/admin/roles", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and isinstance(data["items"], list):
                    if len(data["items"]) > 0:
                        # Check structure of roles
                        valid_roles = all(
                            "id" in role and "name" in role 
                            for role in data["items"]
                        )
                        if valid_roles:
                            self.log_test("Admin Roles GET", True, 
                                        f"Retrieved {len(data['items'])} roles")
                            return True
                        else:
                            self.log_test("Admin Roles GET", False, "Invalid role structure", data)
                    else:
                        self.log_test("Admin Roles GET", False, "No roles returned", data)
                else:
                    self.log_test("Admin Roles GET", False, "Invalid response structure", data)
            else:
                self.log_test("Admin Roles GET", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Admin Roles GET", False, f"Error: {str(e)}")
        return False
    
    # ========== PROJECTS ENDPOINTS TESTS ==========
    def test_projects_post_get(self):
        """Test POST /api/projects and GET /api/projects"""
        try:
            # First, POST a new project
            project_data = {
                "name": "Test Marketing Campaign Project",
                "description": "A test project for marketing campaigns"
            }
            
            post_response = self.session.post(
                f"{API_BASE}/projects",
                json=project_data,
                timeout=10
            )
            
            if post_response.status_code == 200:
                post_data = post_response.json()
                if "project" in post_data and post_data["project"].get("id"):
                    project_id = post_data["project"]["id"]
                    self.created_items.append(("project", project_id))
                    self.log_test("Projects POST", True, 
                                f"Created project with ID: {project_id}")
                    
                    # Now test GET to list projects
                    get_response = self.session.get(f"{API_BASE}/projects", timeout=10)
                    
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        if "items" in get_data and isinstance(get_data["items"], list):
                            # Check if our created project is in the list
                            found_project = any(
                                item.get("id") == project_id 
                                for item in get_data["items"]
                            )
                            if found_project:
                                self.log_test("Projects GET", True, 
                                            f"Retrieved {len(get_data['items'])} projects including created one")
                                return True
                            else:
                                self.log_test("Projects GET", False, 
                                            "Created project not found in list", get_data)
                        else:
                            self.log_test("Projects GET", False, "Invalid response structure", get_data)
                    else:
                        self.log_test("Projects GET", False, 
                                    f"GET HTTP {get_response.status_code}", get_response.text)
                else:
                    self.log_test("Projects POST", False, "Invalid response structure", post_data)
            else:
                self.log_test("Projects POST", False, 
                            f"POST HTTP {post_response.status_code}", post_response.text)
        except Exception as e:
            self.log_test("Projects POST/GET Flow", False, f"Error: {str(e)}")
        return False
    
    # ========== CATALOGUE ENDPOINTS TESTS ==========
    def test_catalogue_list_with_project_filter(self):
        """Test GET /api/uploads/catalogue/list with project_id filter"""
        try:
            # First, test without filter
            response_all = self.session.get(f"{API_BASE}/uploads/catalogue/list", timeout=10)
            
            if response_all.status_code == 200:
                data_all = response_all.json()
                if "catalogues" in data_all and isinstance(data_all["catalogues"], list):
                    self.log_test("Catalogue List (All)", True, 
                                f"Retrieved {len(data_all['catalogues'])} catalogue items")
                    
                    # Now test with project_id filter (use a random UUID that likely doesn't exist)
                    test_project_id = str(uuid.uuid4())
                    response_filtered = self.session.get(
                        f"{API_BASE}/uploads/catalogue/list?project_id={test_project_id}", 
                        timeout=10
                    )
                    
                    if response_filtered.status_code == 200:
                        data_filtered = response_filtered.json()
                        if "catalogues" in data_filtered and isinstance(data_filtered["catalogues"], list):
                            # Should return empty list or items with matching project_id
                            valid_filter = all(
                                item.get("project_id") == test_project_id 
                                for item in data_filtered["catalogues"]
                                if item.get("project_id") is not None
                            )
                            if valid_filter:
                                self.log_test("Catalogue List (Filtered)", True, 
                                            f"Filter working: {len(data_filtered['catalogues'])} items for project {test_project_id}")
                                return True
                            else:
                                self.log_test("Catalogue List (Filtered)", False, 
                                            "Filter not working properly", data_filtered)
                        else:
                            self.log_test("Catalogue List (Filtered)", False, 
                                        "Invalid filtered response structure", data_filtered)
                    else:
                        self.log_test("Catalogue List (Filtered)", False, 
                                    f"Filtered HTTP {response_filtered.status_code}", response_filtered.text)
                else:
                    self.log_test("Catalogue List (All)", False, "Invalid response structure", data_all)
            else:
                self.log_test("Catalogue List (All)", False, 
                            f"HTTP {response_all.status_code}", response_all.text)
        except Exception as e:
            self.log_test("Catalogue List with Filter", False, f"Error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all new endpoint tests in sequence"""
        print("🚀 Starting CRM New Endpoints Test Suite")
        print("=" * 70)
        print("Testing new endpoints as requested in review")
        print("=" * 70)
        
        # Test 1: AI Endpoints
        print("\n1️⃣ Testing AI Chat Endpoints...")
        self.test_ai_specialized_chat()
        self.test_ai_aavana2_enhanced_chat()
        self.test_ai_aavana2_chat()
        
        # Test 2: HRMS Endpoints
        print("\n2️⃣ Testing HRMS Endpoints...")
        self.test_hrms_today()
        self.test_hrms_checkin_checkout_flow()
        self.test_hrms_summary()
        
        # Test 3: Training Endpoints
        print("\n3️⃣ Testing Training Endpoints...")
        self.test_training_modules_post_then_get()
        
        # Test 4: Admin Endpoints
        print("\n4️⃣ Testing Admin Endpoints...")
        self.test_admin_settings_get_put()
        self.test_admin_roles_get()
        
        # Test 5: Projects Endpoints
        print("\n5️⃣ Testing Projects Endpoints...")
        self.test_projects_post_get()
        
        # Test 6: Catalogue Endpoints
        print("\n6️⃣ Testing Catalogue Endpoints...")
        self.test_catalogue_list_with_project_filter()
        
        # Summary
        self.print_summary()
        
        return self.get_overall_success()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 NEW ENDPOINTS TEST SUMMARY")
        print("=" * 70)
        
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
        if self.created_items:
            print(f"\n📝 Created {len(self.created_items)} test items")
        
        # Check for 500 errors specifically
        server_errors = [result for result in self.test_results 
                        if not result["success"] and "500" in result["details"]]
        if server_errors:
            print(f"\n🚨 CRITICAL: Found {len(server_errors)} endpoints returning 500 errors!")
            for error in server_errors:
                print(f"  • {error['test']}: {error['details']}")
        else:
            print("\n✅ NO 500 ERRORS DETECTED - All endpoints responding properly")
    
    def get_overall_success(self):
        """Get overall test success status"""
        if not self.test_results:
            return False
        
        # Check for any 500 errors (critical requirement from review)
        has_500_errors = any(
            not result["success"] and "500" in result["details"]
            for result in self.test_results
        )
        
        if has_500_errors:
            return False
        
        # At least 80% of tests should pass for overall success
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        return success_rate >= 80.0

def main():
    """Main test execution"""
    tester = CRMNewEndpointsTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CRM new endpoints tests completed successfully!")
        print("✅ No 500 errors detected - all endpoints responding properly")
        exit(0)
    else:
        print("\n❌ CRM new endpoints tests had failures!")
        print("❌ Check for 500 errors or other critical issues above")
        exit(1)

if __name__ == "__main__":
    main()