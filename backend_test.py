#!/usr/bin/env python3
"""
OpenAI API Integration and Digital Marketing Backend Test
Testing OpenAI API connection and comprehensive digital marketing endpoints
"""

import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://green-crm-suite.preview.emergentagent.com/api"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class OpenAIDigitalMarketingTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.openai_key = OPENAI_API_KEY
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, success, details, response_time=None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_time': response_time
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.2f}s)" if response_time else ""
        print(f"{status} {test_name}{time_info}: {details}")
        
    def test_openai_api_connection(self):
        """Test OpenAI API key and GPT-4o model access"""
        print("\n🔑 TESTING OPENAI API CONNECTION")
        
        try:
            # Test 1: Check if API key is configured
            if not self.openai_key:
                self.log_test("OpenAI API Key Configuration", False, "OPENAI_API_KEY not found in environment")
                return False
                
            if not self.openai_key.startswith('sk-'):
                self.log_test("OpenAI API Key Format", False, f"Invalid API key format: {self.openai_key[:10]}...")
                return False
                
            self.log_test("OpenAI API Key Configuration", True, f"API key configured: {self.openai_key[:10]}...")
            
            # Test 2: Direct OpenAI API call to test GPT-4o
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                
                start_time = time.time()
                response = client.chat.completions.create(
                    model='gpt-4o',
                    messages=[{'role': 'user', 'content': 'Test connection - respond with "OpenAI GPT-4o working"'}],
                    max_tokens=50,
                    temperature=0.1
                )
                response_time = time.time() - start_time
                
                if response.choices and response.choices[0].message.content:
                    content = response.choices[0].message.content.strip()
                    self.log_test("OpenAI GPT-4o Direct API Test", True, 
                                f"GPT-4o responded: '{content}'", response_time)
                    return True
                else:
                    self.log_test("OpenAI GPT-4o Direct API Test", False, "No response content received")
                    return False
                    
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower():
                    self.log_test("OpenAI GPT-4o Direct API Test", False, f"QUOTA EXCEEDED: {error_msg}")
                elif "invalid" in error_msg.lower():
                    self.log_test("OpenAI GPT-4o Direct API Test", False, f"INVALID API KEY: {error_msg}")
                else:
                    self.log_test("OpenAI GPT-4o Direct API Test", False, f"API Error: {error_msg}")
                return False
                
        except ImportError:
            self.log_test("OpenAI Library Import", False, "OpenAI library not installed")
            return False
        except Exception as e:
            self.log_test("OpenAI API Connection Test", False, f"Unexpected error: {str(e)}")
            return False
    
    def test_digital_marketing_endpoints(self):
        """Test comprehensive digital marketing AI endpoints"""
        print("\n🎯 TESTING DIGITAL MARKETING AI ENDPOINTS")
        
        # Test data for marketing endpoints
        test_data = {
            'comprehensive_strategy': {
                'business_data': {
                    'company': 'Aavana Greens',
                    'industry': 'Green Building & Landscaping',
                    'target_audience': 'Eco-conscious homeowners',
                    'budget': 100000,
                    'goals': ['Brand awareness', 'Lead generation', 'Customer engagement']
                },
                'current_performance': {
                    'monthly_leads': 45,
                    'conversion_rate': 12.5,
                    'social_followers': 2500,
                    'website_traffic': 8000
                }
            },
            'reel_content': {
                'specifications': {
                    'topic': 'Indoor Plant Care Tips',
                    'duration': '30_seconds',
                    'style': 'educational',
                    'target_audience': 'plant_enthusiasts',
                    'call_to_action': 'Visit our nursery'
                }
            },
            'ugc_campaign': {
                'specifications': {
                    'campaign_theme': 'My Green Home Transformation',
                    'duration': '3_months',
                    'incentive_type': 'contest',
                    'target_submissions': 200
                }
            },
            'ai_influencer': {
                'specifications': {
                    'persona': 'EcoGuru Maya',
                    'niche': 'sustainable_living',
                    'personality': 'friendly_expert',
                    'content_focus': 'plant_care_tips'
                }
            },
            'crossplatform_campaign': {
                'campaign_data': {
                    'name': 'Green Living Revolution',
                    'objective': 'brand_awareness',
                    'budget': 50000,
                    'duration': '2_months'
                },
                'platform_allocation': {
                    'google_ads': 35,
                    'instagram': 25,
                    'facebook': 20,
                    'youtube': 15,
                    'linkedin': 5
                }
            }
        }
        
        # Test each digital marketing endpoint
        endpoints = [
            ('Comprehensive Marketing Strategy', '/ai/marketing/comprehensive-strategy', test_data['comprehensive_strategy']),
            ('AI Reel Content Creation', '/ai/content/create-reel', test_data['reel_content']),
            ('UGC Campaign Generation', '/ai/content/create-ugc', test_data['ugc_campaign']),
            ('AI Influencer Creation', '/ai/content/create-influencer', test_data['ai_influencer']),
            ('Cross-Platform Campaign Launch', '/ai/campaigns/launch-crossplatform', test_data['crossplatform_campaign'])
        ]
        
        for test_name, endpoint, payload in endpoints:
            try:
                start_time = time.time()
                response = self.session.post(f"{self.backend_url}{endpoint}", json=payload, timeout=30)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        # Check for specific response structure based on endpoint
                        if 'strategy' in endpoint:
                            has_content = 'strategy' in data and 'comprehensive_plan' in data['strategy']
                        elif 'create-reel' in endpoint:
                            has_content = 'content' in data and 'concept' in data['content']
                        elif 'create-ugc' in endpoint:
                            has_content = 'campaign' in data and 'concept' in data['campaign']
                        elif 'create-influencer' in endpoint:
                            has_content = 'influencer' in data and 'personality' in data['influencer']
                        elif 'launch-crossplatform' in endpoint:
                            has_content = 'campaign_launch' in data and 'launch_plan' in data['campaign_launch']
                        else:
                            has_content = True
                            
                        if has_content:
                            self.log_test(test_name, True, 
                                        f"AI content generated successfully with proper structure", response_time)
                        else:
                            self.log_test(test_name, False, 
                                        f"Response missing expected content structure: {list(data.keys())}")
                    else:
                        self.log_test(test_name, False, f"API returned success=false: {data}")
                else:
                    self.log_test(test_name, False, 
                                f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                self.log_test(test_name, False, "Request timeout (>30s) - AI processing too slow")
            except requests.exceptions.RequestException as e:
                self.log_test(test_name, False, f"Request error: {str(e)}")
            except Exception as e:
                self.log_test(test_name, False, f"Unexpected error: {str(e)}")
    
    def test_workflow_endpoints(self):
        """Test existing workflow endpoints"""
        print("\n⚙️ TESTING WORKFLOW ENDPOINTS")
        
        workflow_endpoints = [
            ('Get Workflows', 'GET', '/workflows', None),
            ('Get Workflow Templates', 'GET', '/workflow-templates', None),
            ('Create Workflow Test', 'POST', '/workflows', {
                'name': 'Test OpenAI Integration Workflow',
                'description': 'Testing workflow creation with OpenAI integration',
                'category': 'lead_nurturing',
                'steps': [
                    {
                        'type': 'ai_response',
                        'name': 'Generate Welcome Message',
                        'config': {
                            'model': 'gpt-4o',
                            'prompt': 'Generate a welcome message for new leads'
                        }
                    }
                ],
                'is_active': True
            })
        ]
        
        for test_name, method, endpoint, payload in workflow_endpoints:
            try:
                start_time = time.time()
                if method == 'GET':
                    response = self.session.get(f"{self.backend_url}{endpoint}", timeout=15)
                else:
                    response = self.session.post(f"{self.backend_url}{endpoint}", json=payload, timeout=15)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if method == 'GET' and endpoint == '/workflows':
                        # Check if workflows data is returned
                        if 'workflows' in data or isinstance(data, list):
                            count = len(data.get('workflows', data)) if isinstance(data, dict) else len(data)
                            self.log_test(test_name, True, f"Retrieved {count} workflows", response_time)
                        else:
                            self.log_test(test_name, False, f"Unexpected response structure: {list(data.keys())}")
                    elif method == 'GET' and endpoint == '/workflow-templates':
                        # Check if templates data is returned
                        if isinstance(data, list) or 'templates' in data:
                            count = len(data) if isinstance(data, list) else len(data.get('templates', []))
                            self.log_test(test_name, True, f"Retrieved {count} workflow templates", response_time)
                        else:
                            self.log_test(test_name, False, f"Unexpected response structure: {list(data.keys())}")
                    elif method == 'POST':
                        # Check workflow creation response
                        if data.get('success') or 'id' in data:
                            self.log_test(test_name, True, "Workflow created successfully", response_time)
                        else:
                            self.log_test(test_name, False, f"Workflow creation failed: {data}")
                    else:
                        self.log_test(test_name, True, f"Endpoint accessible", response_time)
                else:
                    self.log_test(test_name, False, 
                                f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                self.log_test(test_name, False, "Request timeout (>15s)")
            except requests.exceptions.RequestException as e:
                self.log_test(test_name, False, f"Request error: {str(e)}")
            except Exception as e:
                self.log_test(test_name, False, f"Unexpected error: {str(e)}")
    
    def test_backend_health(self):
        """Test basic backend connectivity"""
        print("\n🏥 TESTING BACKEND HEALTH")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    self.log_test("Backend Health Check", True, 
                                f"Backend responding: {data['message']}", response_time)
                    return True
                else:
                    self.log_test("Backend Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Backend Health Check", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 STARTING OPENAI API INTEGRATION AND DIGITAL MARKETING BACKEND TESTS")
        print(f"Backend URL: {self.backend_url}")
        print(f"OpenAI API Key: {self.openai_key[:10] if self.openai_key else 'NOT CONFIGURED'}...")
        print("=" * 80)
        
        # Test sequence
        backend_healthy = self.test_backend_health()
        
        if backend_healthy:
            openai_working = self.test_openai_api_connection()
            self.test_digital_marketing_endpoints()
            self.test_workflow_endpoints()
        else:
            print("❌ Backend not healthy, skipping other tests")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Categorize results
        openai_tests = [r for r in self.test_results if 'openai' in r['test'].lower() or 'gpt' in r['test'].lower()]
        marketing_tests = [r for r in self.test_results if any(keyword in r['test'].lower() 
                          for keyword in ['marketing', 'reel', 'ugc', 'influencer', 'campaign'])]
        workflow_tests = [r for r in self.test_results if 'workflow' in r['test'].lower()]
        
        print(f"\n🔑 OpenAI API Tests: {sum(1 for t in openai_tests if t['success'])}/{len(openai_tests)} passed")
        print(f"🎯 Digital Marketing Tests: {sum(1 for t in marketing_tests if t['success'])}/{len(marketing_tests)} passed")
        print(f"⚙️ Workflow Tests: {sum(1 for t in workflow_tests if t['success'])}/{len(workflow_tests)} passed")
        
        # Show failed tests
        failed_results = [r for r in self.test_results if not r['success']]
        if failed_results:
            print(f"\n❌ FAILED TESTS ({len(failed_results)}):")
            for result in failed_results:
                print(f"  • {result['test']}: {result['details']}")
        
        # Show critical issues
        critical_issues = []
        for result in self.test_results:
            if not result['success']:
                if 'quota' in result['details'].lower():
                    critical_issues.append("OpenAI API quota exceeded - billing issue")
                elif 'invalid' in result['details'].lower() and 'key' in result['details'].lower():
                    critical_issues.append("OpenAI API key invalid - configuration issue")
                elif 'timeout' in result['details'].lower():
                    critical_issues.append("API timeouts - performance issue")
                elif result['test'] == 'Backend Health Check':
                    critical_issues.append("Backend connectivity failure - infrastructure issue")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in set(critical_issues):  # Remove duplicates
                print(f"  • {issue}")
        
        print("\n" + "=" * 80)
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: All systems operational, OpenAI integration working perfectly")
        elif success_rate >= 75:
            print("✅ GOOD: Most systems working, minor issues detected")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Significant issues detected, requires attention")
        else:
            print("🚨 CRITICAL: Major system failures, immediate action required")

if __name__ == "__main__":
    tester = OpenAIDigitalMarketingTester()
    tester.run_comprehensive_test()
"""
Backend API Testing for 502 Error Resolution
Focus: Testing specific endpoints reported with 502 errors by user
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://green-crm-suite.preview.emergentagent.com/api"
TIMEOUT = 30

class BackendTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, test_name, status, details="", response_time=0):
        """Log test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            print(f"✅ {test_name}: {status} ({response_time:.2f}s)")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {status} - {details}")
        
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
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
                self.log_result(test_name, "PASS", f"Status: {response.status_code}", response_time)
                return response
            else:
                error_detail = f"Expected {expected_status}, got {response.status_code}"
                if response.status_code == 502:
                    error_detail += " - BACKEND GATEWAY ERROR"
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
    
    def test_critical_endpoints(self):
        """Test the specific endpoints mentioned in review request"""
        print("🎯 TESTING CRITICAL ENDPOINTS FOR 502 ERROR RESOLUTION")
        print("=" * 60)
        
        # 1. Dashboard Stats (should be working)
        print("\n📊 Testing Dashboard Stats...")
        self.test_endpoint("GET", "/dashboard/stats", "Dashboard Stats API")
        
        # 2. Leads Endpoint (reported 502 error)
        print("\n👥 Testing Leads Endpoints...")
        self.test_endpoint("GET", "/leads", "Get All Leads")
        self.test_endpoint("GET", "/leads?limit=10", "Get Leads with Limit")
        
        # 3. Tasks Endpoint (reported 502 error)  
        print("\n📋 Testing Tasks Endpoints...")
        self.test_endpoint("GET", "/tasks", "Get All Tasks")
        self.test_endpoint("GET", "/tasks?limit=10", "Get Tasks with Limit")
        
        # 4. Workflow Templates (should be working)
        print("\n🔄 Testing Workflow Templates...")
        self.test_endpoint("GET", "/workflow-templates", "Get Workflow Templates")
        
        # 5. Workflows Endpoint (reported 502 error)
        print("\n⚙️ Testing Workflows Endpoints...")
        self.test_endpoint("GET", "/workflows", "Get All Workflows")
        
        # Additional critical endpoints
        print("\n🔍 Testing Additional Critical Endpoints...")
        self.test_endpoint("GET", "/", "Root API Endpoint")
        
    def test_backend_health(self):
        """Test overall backend health"""
        print("\n🏥 BACKEND HEALTH CHECK")
        print("=" * 30)
        
        # Test basic connectivity
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                print("✅ Backend is responding")
                print(f"📡 Response: {response.json()}")
            else:
                print(f"⚠️ Backend responding with status: {response.status_code}")
        except Exception as e:
            print(f"❌ Backend connectivity failed: {str(e)}")
    
    def test_specific_502_scenarios(self):
        """Test scenarios that commonly cause 502 errors"""
        print("\n🚨 TESTING 502 ERROR SCENARIOS")
        print("=" * 35)
        
        # Test with different HTTP methods
        endpoints_to_test = [
            ("/leads", "GET"),
            ("/tasks", "GET"), 
            ("/workflows", "GET"),
            ("/dashboard/stats", "GET")
        ]
        
        for endpoint, method in endpoints_to_test:
            print(f"\n🔍 Testing {method} {endpoint} for 502 errors...")
            response = self.test_endpoint(method, endpoint, f"{method} {endpoint} - 502 Check")
            
            if response and response.status_code == 502:
                print(f"🚨 CONFIRMED: 502 error on {endpoint}")
                print(f"Response headers: {dict(response.headers)}")
                print(f"Response body: {response.text[:500]}")
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🎯 BACKEND API TESTING FOR 502 ERROR RESOLUTION")
        print("=" * 55)
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"⏰ Timeout: {TIMEOUT}s")
        print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test backend health first
        self.test_backend_health()
        
        # Test critical endpoints
        self.test_critical_endpoints()
        
        # Test specific 502 scenarios
        self.test_specific_502_scenarios()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📈 Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        if self.failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        print("\n🎯 CRITICAL FINDINGS:")
        
        # Check for 502 errors specifically
        has_502_errors = any("502" in result["details"] for result in self.results if result["status"] == "FAIL")
        
        if has_502_errors:
            print("🚨 502 BACKEND GATEWAY ERRORS DETECTED:")
            for result in self.results:
                if result["status"] == "FAIL" and "502" in result["details"]:
                    print(f"   🔴 {result['test']}")
            print("\n💡 RECOMMENDED ACTIONS:")
            print("   1. Check if backend service is running")
            print("   2. Verify supervisor backend logs")
            print("   3. Check for missing dependencies")
            print("   4. Restart backend service if needed")
        else:
            print("✅ No 502 errors detected in tested endpoints")
        
        # Check for working endpoints
        working_endpoints = [result["test"] for result in self.results if result["status"] == "PASS"]
        if working_endpoints:
            print(f"\n✅ WORKING ENDPOINTS ({len(working_endpoints)}):")
            for endpoint in working_endpoints:
                print(f"   ✅ {endpoint}")

if __name__ == "__main__":
    print("🚀 Starting Backend API Testing for 502 Error Resolution...")
    tester = BackendTester()
    tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if tester.failed_tests > 0:
        print(f"\n⚠️ Testing completed with {tester.failed_tests} failures")
        sys.exit(1)
    else:
        print(f"\n🎉 All tests passed successfully!")
        sys.exit(0)