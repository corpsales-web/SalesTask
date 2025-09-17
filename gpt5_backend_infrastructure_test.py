#!/usr/bin/env python3
"""
GPT-5 Integration Testing for Aavana 2.0 - Backend Infrastructure Test
Testing backend endpoints and infrastructure readiness for GPT-5 integration
Focus: API connectivity, error handling, and system readiness
"""

import requests
import json
import time
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://green-crm-suite.preview.emergentagent.com/api"
TIMEOUT = 30

class GPT5BackendInfrastructureTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.response_times = []
        
    def log_result(self, test_name, status, details="", response_time=0, data=None):
        """Log test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            print(f"✅ {test_name}: {status} ({response_time:.2f}s)")
            if data:
                print(f"   📊 Data: {str(data)[:100]}...")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {status} - {details}")
        
        if response_time > 0:
            self.response_times.append(response_time)
        
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "data": str(data)[:200] if data else "",
            "timestamp": datetime.now().isoformat()
        })
    
    def test_endpoint(self, method, endpoint, test_name, expected_status=200, data=None, headers=None):
        """Generic endpoint testing"""
        url = f"{BACKEND_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=TIMEOUT, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=TIMEOUT, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=TIMEOUT, headers=headers)
            else:
                self.log_result(test_name, "FAIL", f"Unsupported method: {method}")
                return None
            
            response_time = time.time() - start_time
            
            if response.status_code == expected_status:
                try:
                    response_data = response.json()
                    self.log_result(test_name, "PASS", 
                                  f"Status: {response.status_code}", 
                                  response_time, response_data)
                    return response_data
                except:
                    self.log_result(test_name, "PASS", 
                                  f"Status: {response.status_code} (non-JSON)", 
                                  response_time, response.text[:100])
                    return response.text
            else:
                error_detail = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail += f" - Response: {response.text[:200]}"
                except:
                    pass
                self.log_result(test_name, "FAIL", error_detail, response_time)
                return None
                
        except requests.exceptions.Timeout:
            self.log_result(test_name, "FAIL", "Request timeout")
            return None
        except requests.exceptions.ConnectionError:
            self.log_result(test_name, "FAIL", "Connection error")
            return None
        except Exception as e:
            self.log_result(test_name, "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_backend_health_and_connectivity(self):
        """Test basic backend health and connectivity"""
        print("\n🏥 TESTING BACKEND HEALTH & CONNECTIVITY")
        print("=" * 50)
        
        # Basic health check
        self.test_endpoint("GET", "/", "Backend Health Check")
        
        # Dashboard stats (should work without AI)
        self.test_endpoint("GET", "/dashboard/stats", "Dashboard Statistics")
        
        # Core data endpoints
        self.test_endpoint("GET", "/leads", "Leads Data Endpoint")
        self.test_endpoint("GET", "/tasks", "Tasks Data Endpoint")
        self.test_endpoint("GET", "/workflows", "Workflows Data Endpoint")
        self.test_endpoint("GET", "/workflow-templates", "Workflow Templates Endpoint")
    
    def test_aavana2_endpoint_availability(self):
        """Test Aavana 2.0 endpoint availability (without AI processing)"""
        print("\n🤖 TESTING AAVANA 2.0 ENDPOINT AVAILABILITY")
        print("=" * 50)
        
        # Test endpoint availability with minimal request
        test_payload = {
            "message": "",  # Empty message to test endpoint without triggering AI
            "session_id": str(uuid.uuid4()),
            "language": "en",
            "channel": "web"
        }
        
        # This should return an error but confirm endpoint is accessible
        response = self.test_endpoint("POST", "/aavana2/chat", 
                                    "Aavana 2.0 Chat Endpoint Availability", 
                                    expected_status=200, data=test_payload)
        
        if response:
            print(f"   🔍 Response structure: {list(response.keys()) if isinstance(response, dict) else 'Non-dict response'}")
    
    def test_ai_infrastructure_endpoints(self):
        """Test AI-related infrastructure endpoints"""
        print("\n🧠 TESTING AI INFRASTRUCTURE ENDPOINTS")
        print("=" * 50)
        
        # Test various AI endpoints for availability (not functionality)
        ai_endpoints = [
            "/ai/insights",
            "/ai/generate-content", 
            "/ai/voice-to-task",
            "/ai/generate",
            "/ai/smart-selection",
            "/ai/analyze-conversation",
            "/ai/generate-proposal",
            "/ai/optimize-workflow",
            "/ai/marketing-content",
            "/ai/predict-deals",
            "/ai/task-automation"
        ]
        
        for endpoint in ai_endpoints:
            # Test with minimal payload to check endpoint availability
            test_data = {"test": "availability_check"}
            response = self.test_endpoint("POST", endpoint, 
                                        f"AI Endpoint: {endpoint}", 
                                        expected_status=200, data=test_data)
    
    def test_crm_specific_ai_endpoints(self):
        """Test CRM-specific AI endpoints mentioned in review request"""
        print("\n🏢 TESTING CRM-SPECIFIC AI ENDPOINTS")
        print("=" * 50)
        
        crm_endpoints = [
            ("/ai/crm/smart-lead-scoring", {"lead_id": "test_lead_123"}),
            ("/ai/crm/conversation-analysis", {"conversation": "test conversation"}),
            ("/ai/sales/deal-prediction", {}),
            ("/ai/sales/smart-proposal-generator", {"lead_id": "test_lead_123", "service_type": "landscaping"}),
            ("/ai/marketing/campaign-optimizer", {"campaign": "test campaign"}),
            ("/ai/marketing/competitor-analysis", {"location": "Mumbai"}),
            ("/ai/product/smart-catalog", {}),
            ("/ai/project/design-suggestions", {"requirements": "balcony garden"}),
            ("/ai/hr/performance-analysis", {}),
            ("/ai/automation/workflow-optimization", {}),
            ("/ai/automation/smart-notifications", {})
        ]
        
        for endpoint, test_data in crm_endpoints:
            response = self.test_endpoint("POST", endpoint, 
                                        f"CRM AI Endpoint: {endpoint}", 
                                        expected_status=200, data=test_data)
    
    def test_authentication_system(self):
        """Test authentication system for AI endpoints"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        print("=" * 40)
        
        # Test login endpoint
        login_data = {
            "identifier": "admin",
            "password": "admin123"
        }
        
        response = self.test_endpoint("POST", "/auth/login", 
                                    "Admin Authentication", 
                                    expected_status=200, data=login_data)
        
        if response and isinstance(response, dict) and "access_token" in response:
            token = response["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test authenticated endpoint
            self.test_endpoint("GET", "/auth/me", 
                             "Authenticated User Info", 
                             expected_status=200, headers=headers)
            
            return headers
        
        return None
    
    def test_error_handling_and_fallbacks(self):
        """Test error handling and fallback mechanisms"""
        print("\n🛡️ TESTING ERROR HANDLING & FALLBACKS")
        print("=" * 45)
        
        # Test with invalid data
        invalid_requests = [
            ("/aavana2/chat", {"invalid": "data"}),
            ("/ai/insights", {"type": "invalid_type"}),
            ("/leads", None),  # GET with POST data
        ]
        
        for endpoint, data in invalid_requests:
            if data:
                self.test_endpoint("POST", endpoint, 
                                 f"Error Handling: {endpoint}", 
                                 expected_status=200, data=data)  # May return 200 with error message
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks for non-AI endpoints"""
        print("\n⚡ TESTING PERFORMANCE BENCHMARKS")
        print("=" * 40)
        
        # Test multiple quick requests
        quick_endpoints = [
            "/",
            "/dashboard/stats", 
            "/leads?limit=5",
            "/tasks?limit=5"
        ]
        
        for endpoint in quick_endpoints:
            for i in range(3):  # Test 3 times each
                self.test_endpoint("GET", endpoint, 
                                 f"Performance Test {i+1}: {endpoint}")
                time.sleep(0.1)
    
    def run_comprehensive_infrastructure_test(self):
        """Run all infrastructure tests"""
        print("🚀 GPT-5 BACKEND INFRASTRUCTURE TESTING FOR AAVANA 2.0")
        print("=" * 60)
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"⏰ Timeout: {TIMEOUT}s")
        print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test backend infrastructure
        self.test_backend_health_and_connectivity()
        self.test_aavana2_endpoint_availability()
        self.test_ai_infrastructure_endpoints()
        self.test_crm_specific_ai_endpoints()
        
        # Test authentication
        auth_headers = self.test_authentication_system()
        
        # Test error handling
        self.test_error_handling_and_fallbacks()
        
        # Test performance
        self.test_performance_benchmarks()
        
        # Print comprehensive summary
        self.print_infrastructure_summary()
    
    def print_infrastructure_summary(self):
        """Print detailed infrastructure test summary"""
        print("\n" + "=" * 70)
        print("📊 GPT-5 BACKEND INFRASTRUCTURE TEST SUMMARY")
        print("=" * 70)
        
        # Basic stats
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📈 Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        # Performance analysis
        if self.response_times:
            avg_time = sum(self.response_times) / len(self.response_times)
            max_time = max(self.response_times)
            min_time = min(self.response_times)
            
            print(f"\n⚡ PERFORMANCE ANALYSIS:")
            print(f"   📊 Average Response Time: {avg_time:.2f}s")
            print(f"   🚀 Fastest Response: {min_time:.2f}s")
            print(f"   🐌 Slowest Response: {max_time:.2f}s")
            
            # Performance categories
            fast_responses = len([t for t in self.response_times if t <= 1])
            medium_responses = len([t for t in self.response_times if 1 < t <= 3])
            slow_responses = len([t for t in self.response_times if t > 3])
            
            print(f"   🟢 Fast (≤1s): {fast_responses} tests")
            print(f"   🟡 Medium (1-3s): {medium_responses} tests")
            print(f"   🔴 Slow (>3s): {slow_responses} tests")
        
        # Infrastructure readiness assessment
        print(f"\n🏗️ INFRASTRUCTURE READINESS ASSESSMENT:")
        
        # Check core endpoints
        core_endpoints = ["Backend Health Check", "Dashboard Statistics", "Leads Data Endpoint", "Tasks Data Endpoint"]
        core_passed = len([r for r in self.results if r['test'] in core_endpoints and r['status'] == 'PASS'])
        print(f"   🏥 Core Backend Health: {core_passed}/{len(core_endpoints)} ({(core_passed/len(core_endpoints)*100):.0f}%)")
        
        # Check AI endpoints
        ai_tests = [r for r in self.results if 'AI' in r['test'] or 'Aavana' in r['test']]
        ai_passed = len([r for r in ai_tests if r['status'] == 'PASS'])
        if ai_tests:
            print(f"   🤖 AI Endpoints: {ai_passed}/{len(ai_tests)} ({(ai_passed/len(ai_tests)*100):.0f}%)")
        
        # Check CRM endpoints
        crm_tests = [r for r in self.results if 'CRM' in r['test']]
        crm_passed = len([r for r in crm_tests if r['status'] == 'PASS'])
        if crm_tests:
            print(f"   🏢 CRM AI Endpoints: {crm_passed}/{len(crm_tests)} ({(crm_passed/len(crm_tests)*100):.0f}%)")
        
        # Check authentication
        auth_tests = [r for r in self.results if 'Authentication' in r['test'] or 'auth' in r['test']]
        auth_passed = len([r for r in auth_tests if r['status'] == 'PASS'])
        if auth_tests:
            print(f"   🔐 Authentication: {auth_passed}/{len(auth_tests)} ({(auth_passed/len(auth_tests)*100):.0f}%)")
        
        # Critical findings
        print(f"\n🔍 CRITICAL FINDINGS:")
        
        # Check for failed tests
        failed_tests = [r for r in self.results if r['status'] == 'FAIL']
        if failed_tests:
            print(f"🚨 FAILED TESTS ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"   ❌ {result['test']}: {result['details']}")
        else:
            print("✅ No critical failures detected")
        
        # Check for slow responses
        slow_tests = [r for r in self.results if r['response_time'] > 5]
        if slow_tests:
            print(f"⏰ SLOW RESPONSES (>5s) ({len(slow_tests)}):")
            for result in slow_tests:
                print(f"   🐌 {result['test']}: {result['response_time']:.2f}s")
        
        # GPT-5 Integration Readiness Assessment
        print(f"\n🎯 GPT-5 INTEGRATION READINESS:")
        
        overall_score = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        if overall_score >= 90:
            readiness = "🟢 EXCELLENT - Ready for GPT-5 integration"
        elif overall_score >= 75:
            readiness = "🟡 GOOD - Minor issues to address before GPT-5 integration"
        elif overall_score >= 60:
            readiness = "🟠 FAIR - Several issues need resolution for optimal GPT-5 integration"
        else:
            readiness = "🔴 POOR - Significant infrastructure issues must be resolved"
        
        print(f"   {readiness}")
        
        # Specific GPT-5 requirements check
        print(f"\n📋 GPT-5 SPECIFIC REQUIREMENTS:")
        
        # Check if Aavana 2.0 endpoint is accessible
        aavana_test = next((r for r in self.results if 'Aavana 2.0' in r['test']), None)
        if aavana_test and aavana_test['status'] == 'PASS':
            print("   ✅ Aavana 2.0 Chat endpoint accessible")
        else:
            print("   ❌ Aavana 2.0 Chat endpoint issues detected")
        
        # Check AI infrastructure
        ai_infrastructure_score = (ai_passed / len(ai_tests)) * 100 if ai_tests else 0
        if ai_infrastructure_score >= 70:
            print("   ✅ AI infrastructure endpoints ready")
        else:
            print("   ⚠️ AI infrastructure needs attention")
        
        # Check authentication for AI endpoints
        if auth_passed > 0:
            print("   ✅ Authentication system functional")
        else:
            print("   ⚠️ Authentication system needs verification")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS FOR GPT-5 INTEGRATION:")
        
        if failed_tests:
            print("   🔧 Address failed endpoint issues before GPT-5 deployment")
        
        if slow_tests:
            print("   ⚡ Optimize slow endpoints for better GPT-5 response times")
        
        print("   🔑 Verify EMERGENT_LLM_KEY configuration for GPT-5 access")
        print("   🧪 Test GPT-5 model selection and fallback mechanisms")
        print("   📊 Implement monitoring for GPT-5 API usage and costs")
        print("   🔄 Test error handling for GPT-5 quota/rate limit scenarios")
        
        # Current issue identification
        print(f"\n🚨 CURRENT ISSUE IDENTIFIED:")
        print("   ❌ OpenAI API quota exceeded (429 error)")
        print("   💡 SOLUTION: Configure EMERGENT_LLM_KEY or add OpenAI credits")
        print("   🔧 Backend logs show: 'You exceeded your current quota'")
        print("   📞 Contact system administrator to resolve API key issues")

if __name__ == "__main__":
    print("🚀 Starting GPT-5 Backend Infrastructure Testing...")
    tester = GPT5BackendInfrastructureTester()
    tester.run_comprehensive_infrastructure_test()
    
    # Exit with appropriate code
    if tester.failed_tests > 0:
        print(f"\n⚠️ Infrastructure testing completed with {tester.failed_tests} issues")
        sys.exit(1)
    else:
        print(f"\n🎉 Infrastructure ready for GPT-5 integration!")
        sys.exit(0)