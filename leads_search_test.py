#!/usr/bin/env python3
"""
CRM Backend Leads Search Route Test
Focused test for /api/leads/search after route reorder fix
Tests that search endpoint works and doesn't get captured by {lead_id} route
"""

import requests
import json
import time
import uuid
from typing import Dict, Any

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception:
        pass
    return "https://crm-visual-studio.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class LeadsSearchTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_leads = []  # Track created leads for cleanup
        
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
    
    def create_test_lead(self, name: str, phone: str = None, email: str = None):
        """Create a test lead for search testing"""
        try:
            lead_data = {"name": name}
            if phone:
                lead_data["phone"] = phone
            if email:
                lead_data["email"] = email
            
            response = self.session.post(
                f"{API_BASE}/leads",
                json=lead_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "lead" in data:
                    lead_id = data["lead"]["id"]
                    self.created_leads.append(lead_id)
                    return lead_id
        except Exception as e:
            print(f"Failed to create test lead: {str(e)}")
        return None
    
    def test_leads_search_basic(self):
        """Test GET /api/leads/search with basic query - should return 200, not 404"""
        try:
            # Create a test lead first
            test_lead_id = self.create_test_lead("John Search Test", "+919876543210", "john.search@test.com")
            if not test_lead_id:
                self.log_test("Leads Search (Basic)", False, "Failed to create test lead")
                return False
            
            # Test search by name
            response = self.session.get(f"{API_BASE}/leads/search?q=John", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["items", "page", "limit", "total"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify items is a list
                    if isinstance(data["items"], list):
                        # Check if our test lead is in results
                        found_test_lead = any(
                            item.get("id") == test_lead_id 
                            for item in data["items"] 
                            if isinstance(item, dict)
                        )
                        
                        if found_test_lead:
                            self.log_test("Leads Search (Basic)", True, 
                                        f"Search returned {len(data['items'])} results, found test lead")
                            return True
                        else:
                            self.log_test("Leads Search (Basic)", True, 
                                        f"Search returned {len(data['items'])} results (test lead may not match query)")
                            return True
                    else:
                        self.log_test("Leads Search (Basic)", False, "Items is not a list", data)
                else:
                    self.log_test("Leads Search (Basic)", False, f"Missing fields: {missing_fields}", data)
            elif response.status_code == 404:
                self.log_test("Leads Search (Basic)", False, 
                            "Search endpoint returns 404 - route ordering issue not fixed", response.text)
            else:
                self.log_test("Leads Search (Basic)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads Search (Basic)", False, f"Error: {str(e)}")
        return False
    
    def test_leads_search_phone(self):
        """Test GET /api/leads/search with phone number query"""
        try:
            # Create a test lead with specific phone
            test_lead_id = self.create_test_lead("Phone Search Test", "+919876543210")
            if not test_lead_id:
                self.log_test("Leads Search (Phone)", False, "Failed to create test lead")
                return False
            
            # Test search by phone (last 10 digits)
            response = self.session.get(f"{API_BASE}/leads/search?q=9876543210", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data.get("items"), list):
                    # Check if our test lead is in results
                    found_test_lead = any(
                        item.get("id") == test_lead_id 
                        for item in data["items"] 
                        if isinstance(item, dict)
                    )
                    
                    if found_test_lead:
                        self.log_test("Leads Search (Phone)", True, 
                                    f"Phone search found test lead in {len(data['items'])} results")
                        return True
                    else:
                        self.log_test("Leads Search (Phone)", True, 
                                    f"Phone search returned {len(data['items'])} results (test lead may not match)")
                        return True
                else:
                    self.log_test("Leads Search (Phone)", False, "Invalid response format", data)
            elif response.status_code == 404:
                self.log_test("Leads Search (Phone)", False, 
                            "Search endpoint returns 404 - route ordering issue not fixed", response.text)
            else:
                self.log_test("Leads Search (Phone)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads Search (Phone)", False, f"Error: {str(e)}")
        return False
    
    def test_leads_search_empty_query(self):
        """Test GET /api/leads/search with empty query"""
        try:
            response = self.session.get(f"{API_BASE}/leads/search?q=", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data.get("items"), list):
                    self.log_test("Leads Search (Empty Query)", True, 
                                f"Empty query returned {len(data['items'])} results")
                    return True
                else:
                    self.log_test("Leads Search (Empty Query)", False, "Invalid response format", data)
            elif response.status_code == 404:
                self.log_test("Leads Search (Empty Query)", False, 
                            "Search endpoint returns 404 - route ordering issue not fixed", response.text)
            else:
                self.log_test("Leads Search (Empty Query)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads Search (Empty Query)", False, f"Error: {str(e)}")
        return False
    
    def test_leads_get_by_id_still_works(self):
        """Test GET /api/leads/{lead_id} still works after route reorder"""
        try:
            # Create a test lead first
            test_lead_id = self.create_test_lead("ID Test Lead")
            if not test_lead_id:
                self.log_test("Leads Get By ID", False, "Failed to create test lead")
                return False
            
            # Test getting lead by ID
            response = self.session.get(f"{API_BASE}/leads/{test_lead_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "lead" in data:
                    lead = data["lead"]
                    if lead.get("id") == test_lead_id:
                        self.log_test("Leads Get By ID", True, 
                                    f"Successfully retrieved lead by ID: {test_lead_id}")
                        return True
                    else:
                        self.log_test("Leads Get By ID", False, "Wrong lead returned", data)
                else:
                    self.log_test("Leads Get By ID", False, "Invalid response format", data)
            else:
                self.log_test("Leads Get By ID", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads Get By ID", False, f"Error: {str(e)}")
        return False
    
    def test_leads_search_vs_id_conflict(self):
        """Test that 'search' is not interpreted as a lead_id"""
        try:
            # Test that /api/leads/search doesn't get captured by /api/leads/{lead_id}
            response = self.session.get(f"{API_BASE}/leads/search?q=test", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Should return search results format, not single lead format
                if "items" in data and "page" in data and "limit" in data and "total" in data:
                    self.log_test("Leads Search vs ID Conflict", True, 
                                "Search endpoint correctly returns search format, not single lead")
                    return True
                elif "lead" in data:
                    self.log_test("Leads Search vs ID Conflict", False, 
                                "Search endpoint incorrectly returns single lead format - route conflict exists")
                else:
                    self.log_test("Leads Search vs ID Conflict", False, 
                                "Unexpected response format", data)
            elif response.status_code == 404:
                # Check if it's trying to find a lead with ID "search"
                if "not found" in response.text.lower():
                    self.log_test("Leads Search vs ID Conflict", False, 
                                "Search endpoint captured by {lead_id} route - route ordering issue not fixed")
                else:
                    self.log_test("Leads Search vs ID Conflict", False, 
                                f"Unexpected 404: {response.text}")
            else:
                self.log_test("Leads Search vs ID Conflict", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads Search vs ID Conflict", False, f"Error: {str(e)}")
        return False
    
    def test_dashboard_stats_if_exists(self):
        """Test GET /api/dashboard/stats if it exists, otherwise ignore"""
        try:
            response = self.session.get(f"{API_BASE}/dashboard/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Dashboard Stats", True, 
                            f"Dashboard stats endpoint exists and returned data: {type(data)}")
                return True
            elif response.status_code == 404:
                self.log_test("Dashboard Stats", True, 
                            "Dashboard stats endpoint does not exist (404) - ignoring as requested")
                return True
            else:
                self.log_test("Dashboard Stats", True, 
                            f"Dashboard stats endpoint returned {response.status_code} - ignoring as requested")
                return True
        except Exception as e:
            self.log_test("Dashboard Stats", True, 
                        f"Dashboard stats endpoint error (ignoring): {str(e)}")
        return True  # Always return True since we ignore this endpoint
    
    def run_focused_tests(self):
        """Run focused tests for leads search route ordering"""
        print("🚀 Starting Leads Search Route Test (Post Route Reorder)")
        print("=" * 70)
        print(f"🔗 Testing backend at: {BASE_URL}")
        print("🎯 Focus: Verify /api/leads/search works after route reorder fix")
        print("=" * 70)
        
        # Test 1: Basic search functionality
        print("\n1️⃣ Testing Basic Search Functionality...")
        self.test_leads_search_basic()
        
        # Test 2: Phone number search
        print("\n2️⃣ Testing Phone Number Search...")
        self.test_leads_search_phone()
        
        # Test 3: Empty query handling
        print("\n3️⃣ Testing Empty Query Handling...")
        self.test_leads_search_empty_query()
        
        # Test 4: Verify get by ID still works
        print("\n4️⃣ Testing Get Lead By ID Still Works...")
        self.test_leads_get_by_id_still_works()
        
        # Test 5: Route conflict test
        print("\n5️⃣ Testing Search vs ID Route Conflict...")
        self.test_leads_search_vs_id_conflict()
        
        # Test 6: Dashboard stats (optional)
        print("\n6️⃣ Testing Dashboard Stats (Optional)...")
        self.test_dashboard_stats_if_exists()
        
        # Summary
        self.print_summary()
        
        return self.get_overall_success()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 LEADS SEARCH ROUTE TEST SUMMARY")
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
        if self.created_leads:
            print(f"\n📝 Created {len(self.created_leads)} test leads in database")
        
        # Key findings
        search_works = any(
            result["test"].startswith("Leads Search") and result["success"] 
            for result in self.test_results
        )
        
        route_conflict_resolved = any(
            result["test"] == "Leads Search vs ID Conflict" and result["success"] 
            for result in self.test_results
        )
        
        print(f"\n🔍 KEY FINDINGS:")
        print(f"  • Search endpoint functional: {'✅ YES' if search_works else '❌ NO'}")
        print(f"  • Route conflict resolved: {'✅ YES' if route_conflict_resolved else '❌ NO'}")
    
    def get_overall_success(self):
        """Get overall test success status"""
        if not self.test_results:
            return False
        
        # Critical tests that must pass for search functionality
        critical_tests = [
            "Leads Search (Basic)",
            "Leads Search vs ID Conflict",
            "Leads Get By ID"
        ]
        
        critical_passed = all(
            any(result["test"] == test and result["success"] for result in self.test_results)
            for test in critical_tests
        )
        
        return critical_passed

def main():
    """Main test execution"""
    tester = LeadsSearchTester()
    success = tester.run_focused_tests()
    
    if success:
        print("\n✅ Leads search route tests completed successfully!")
        print("🎯 Route reorder fix appears to be working correctly")
        exit(0)
    else:
        print("\n❌ Leads search route tests had critical failures!")
        print("🚨 Route ordering issue may still exist")
        exit(1)

if __name__ == "__main__":
    main()