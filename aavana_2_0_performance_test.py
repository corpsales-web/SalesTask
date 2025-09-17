#!/usr/bin/env python3
"""
Aavana 2.0 Performance and API Issues Testing
Focus: Debug chat API performance, LLM integration, and response times
"""

import requests
import sys
import json
import time
from datetime import datetime, timezone
import uuid

class Aavana2PerformanceTester:
    def __init__(self, base_url="https://aavana-greens.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.performance_data = []
        self.session_id = str(uuid.uuid4())
        
    def log_performance(self, test_name, response_time, status_code, success):
        """Log performance metrics for analysis"""
        self.performance_data.append({
            'test_name': test_name,
            'response_time': response_time,
            'status_code': status_code,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
    
    def run_timed_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=30):
        """Run a timed API test with performance monitoring"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            response_time = time.time() - start_time
            success = response.status_code == expected_status
            
            self.log_performance(name, response_time, response.status_code, success)
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}, Time: {response_time:.2f}s")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    else:
                        print(f"   Response: Large response ({len(str(response_data))} chars)")
                    return True, response_data, response_time
                except:
                    return True, {}, response_time
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}, Time: {response_time:.2f}s")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}, response_time

        except requests.exceptions.Timeout:
            response_time = timeout
            print(f"⏰ Timeout - Request exceeded {timeout}s")
            self.log_performance(name, response_time, 0, False)
            return False, {}, response_time
        except Exception as e:
            response_time = time.time() - start_time
            print(f"❌ Failed - Error: {str(e)}, Time: {response_time:.2f}s")
            self.log_performance(name, response_time, 0, False)
            return False, {}, response_time

    def test_backend_health(self):
        """Test basic backend health and connectivity"""
        print("\n🏥 BACKEND HEALTH CHECK")
        print("=" * 50)
        
        success, _, response_time = self.run_timed_test("Backend Health Check", "GET", "", 200, timeout=10)
        if not success:
            print("❌ Backend is not responding - stopping tests")
            return False
        
        if response_time > 5:
            print(f"⚠️ Slow backend response: {response_time:.2f}s")
        
        return True

    def test_aavana2_chat_simple(self):
        """Test Aavana 2.0 chat with simple message"""
        print("\n💬 AAVANA 2.0 CHAT API - SIMPLE MESSAGE")
        print("=" * 50)
        
        chat_data = {
            "message": "Hello",
            "session_id": self.session_id,
            "user_id": "test_user_001",
            "language": "en"
        }
        
        success, response, response_time = self.run_timed_test(
            "Aavana 2.0 Chat - Simple Hello", 
            "POST", 
            "aavana2/chat", 
            200, 
            data=chat_data,
            timeout=15
        )
        
        if success:
            print(f"✅ Chat API working - Response time: {response_time:.2f}s")
            if response_time > 10:
                print(f"⚠️ PERFORMANCE ISSUE: Response time {response_time:.2f}s exceeds 10s threshold")
        else:
            print("❌ Chat API failed")
            
        return success, response_time

    def test_aavana2_chat_providers(self):
        """Test different AI providers (openai, anthropic, gemini)"""
        print("\n🤖 AAVANA 2.0 CHAT API - DIFFERENT PROVIDERS")
        print("=" * 50)
        
        providers = ["openai", "anthropic", "gemini"]
        provider_results = {}
        
        for provider in providers:
            chat_data = {
                "message": f"Test message for {provider}",
                "session_id": f"{self.session_id}_{provider}",
                "user_id": "test_user_002",
                "language": "en",
                "provider": provider
            }
            
            success, response, response_time = self.run_timed_test(
                f"Aavana 2.0 Chat - {provider.upper()}", 
                "POST", 
                "aavana2/chat", 
                200, 
                data=chat_data,
                timeout=20
            )
            
            provider_results[provider] = {
                'success': success,
                'response_time': response_time
            }
            
            if success and response_time > 10:
                print(f"⚠️ PERFORMANCE ISSUE: {provider} response time {response_time:.2f}s exceeds 10s threshold")
        
        return provider_results

    def test_aavana2_chat_history(self):
        """Test chat history endpoint"""
        print("\n📚 AAVANA 2.0 CHAT HISTORY")
        print("=" * 50)
        
        success, response, response_time = self.run_timed_test(
            "Aavana 2.0 Chat History", 
            "GET", 
            f"aavana2/chat/history/{self.session_id}", 
            200,
            timeout=10
        )
        
        if success:
            print(f"✅ Chat history working - Response time: {response_time:.2f}s")
            if isinstance(response, list):
                print(f"   Found {len(response)} chat messages in history")
        
        return success, response_time

    def test_emergent_llm_integration(self):
        """Test EMERGENT_LLM_KEY integration"""
        print("\n🔑 EMERGENT LLM KEY INTEGRATION TEST")
        print("=" * 50)
        
        # Test AI generation endpoint that uses EMERGENT_LLM_KEY
        ai_data = {
            "prompt": "Test EMERGENT_LLM_KEY integration",
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        }
        
        success, response, response_time = self.run_timed_test(
            "EMERGENT LLM Key Integration", 
            "POST", 
            "ai/generate", 
            200, 
            data=ai_data,
            timeout=20
        )
        
        if success:
            print(f"✅ EMERGENT_LLM_KEY working - Response time: {response_time:.2f}s")
            if 'content' in response:
                print(f"   AI Response generated successfully")
        else:
            print("❌ EMERGENT_LLM_KEY integration failed")
            
        return success, response_time

    def test_database_connection(self):
        """Test database connection for chat storage"""
        print("\n🗄️ DATABASE CONNECTION TEST")
        print("=" * 50)
        
        # Test dashboard stats to verify database connectivity
        success, response, response_time = self.run_timed_test(
            "Database Connection (Dashboard Stats)", 
            "GET", 
            "dashboard/stats", 
            200,
            timeout=10
        )
        
        if success:
            print(f"✅ Database connection working - Response time: {response_time:.2f}s")
        else:
            print("❌ Database connection failed")
            
        return success, response_time

    def test_session_management(self):
        """Test session management in chat"""
        print("\n🔄 SESSION MANAGEMENT TEST")
        print("=" * 50)
        
        # Send multiple messages with same session ID
        messages = [
            "Hello, I'm interested in green building solutions",
            "What services do you offer?",
            "Can you tell me about pricing?"
        ]
        
        session_results = []
        
        for i, message in enumerate(messages):
            chat_data = {
                "message": message,
                "session_id": f"session_test_{self.session_id}",
                "user_id": "test_user_session",
                "language": "en"
            }
            
            success, response, response_time = self.run_timed_test(
                f"Session Message {i+1}", 
                "POST", 
                "aavana2/chat", 
                200, 
                data=chat_data,
                timeout=15
            )
            
            session_results.append({
                'message_num': i+1,
                'success': success,
                'response_time': response_time
            })
        
        # Check if session context is maintained
        successful_messages = sum(1 for r in session_results if r['success'])
        print(f"   Session messages: {successful_messages}/{len(messages)} successful")
        
        return session_results

    def check_backend_logs(self):
        """Check backend logs for errors"""
        print("\n📋 BACKEND LOG ANALYSIS")
        print("=" * 50)
        
        try:
            import subprocess
            
            # Check supervisor backend logs
            result = subprocess.run(
                ['tail', '-n', '50', '/var/log/supervisor/backend.err.log'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                log_content = result.stdout
                if log_content.strip():
                    print("📋 Recent backend error logs:")
                    print(log_content)
                    
                    # Check for specific errors
                    if "emergentintegrations" in log_content.lower():
                        print("⚠️ Found emergentintegrations related errors")
                    if "timeout" in log_content.lower():
                        print("⚠️ Found timeout related errors")
                    if "llm" in log_content.lower():
                        print("⚠️ Found LLM related errors")
                else:
                    print("✅ No recent error logs found")
            else:
                print("❌ Could not access backend logs")
                
        except Exception as e:
            print(f"❌ Error checking logs: {str(e)}")

    def analyze_performance(self):
        """Analyze performance data and provide recommendations"""
        print("\n📊 PERFORMANCE ANALYSIS")
        print("=" * 50)
        
        if not self.performance_data:
            print("❌ No performance data collected")
            return
        
        # Calculate statistics
        response_times = [p['response_time'] for p in self.performance_data if p['success']]
        failed_tests = [p for p in self.performance_data if not p['success']]
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            print(f"📈 Response Time Statistics:")
            print(f"   Average: {avg_response_time:.2f}s")
            print(f"   Maximum: {max_response_time:.2f}s")
            print(f"   Minimum: {min_response_time:.2f}s")
            
            # Performance thresholds
            slow_tests = [p for p in self.performance_data if p['response_time'] > 10 and p['success']]
            if slow_tests:
                print(f"\n⚠️ SLOW RESPONSES (>10s):")
                for test in slow_tests:
                    print(f"   {test['test_name']}: {test['response_time']:.2f}s")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   {test['test_name']}: Status {test['status_code']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if avg_response_time > 5:
            print("   - Consider optimizing AI model response times")
            print("   - Check EMERGENT_LLM_KEY rate limits")
            print("   - Monitor database query performance")
        
        if failed_tests:
            print("   - Check backend logs for specific error details")
            print("   - Verify EMERGENT_LLM_KEY is valid and has sufficient credits")
            print("   - Test individual AI provider endpoints")

def main():
    print("🚀 AAVANA 2.0 PERFORMANCE AND API ISSUES TESTING")
    print("=" * 60)
    print("Focus: Chat API Performance, LLM Integration, Response Times")
    print("=" * 60)
    
    tester = Aavana2PerformanceTester()
    
    # Step 1: Backend Health Check
    if not tester.test_backend_health():
        print("❌ Backend health check failed - stopping tests")
        return 1
    
    # Step 2: Test Aavana 2.0 Chat API with simple message
    print("\n" + "="*60)
    chat_success, chat_time = tester.test_aavana2_chat_simple()
    
    # Step 3: Test different AI providers
    print("\n" + "="*60)
    provider_results = tester.test_aavana2_chat_providers()
    
    # Step 4: Test chat history
    print("\n" + "="*60)
    history_success, history_time = tester.test_aavana2_chat_history()
    
    # Step 5: Test EMERGENT_LLM_KEY integration
    print("\n" + "="*60)
    llm_success, llm_time = tester.test_emergent_llm_integration()
    
    # Step 6: Test database connection
    print("\n" + "="*60)
    db_success, db_time = tester.test_database_connection()
    
    # Step 7: Test session management
    print("\n" + "="*60)
    session_results = tester.test_session_management()
    
    # Step 8: Check backend logs
    print("\n" + "="*60)
    tester.check_backend_logs()
    
    # Step 9: Performance analysis
    print("\n" + "="*60)
    tester.analyze_performance()
    
    # Final Results
    print("\n" + "=" * 60)
    print(f"📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    # Critical Issues Summary
    print(f"\n🔍 CRITICAL ISSUES SUMMARY:")
    print("=" * 60)
    
    critical_issues = []
    
    if not chat_success:
        critical_issues.append("❌ Aavana 2.0 Chat API not working")
    elif chat_time > 10:
        critical_issues.append(f"⚠️ Aavana 2.0 Chat API slow ({chat_time:.2f}s > 10s)")
    
    if not llm_success:
        critical_issues.append("❌ EMERGENT_LLM_KEY integration failed")
    
    if not db_success:
        critical_issues.append("❌ Database connection issues")
    
    # Check provider results
    failed_providers = [p for p, r in provider_results.items() if not r['success']]
    if failed_providers:
        critical_issues.append(f"❌ AI Providers failed: {', '.join(failed_providers)}")
    
    slow_providers = [p for p, r in provider_results.items() if r['success'] and r['response_time'] > 10]
    if slow_providers:
        critical_issues.append(f"⚠️ Slow AI Providers (>10s): {', '.join(slow_providers)}")
    
    if critical_issues:
        print("CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"  {issue}")
    else:
        print("✅ No critical issues found")
    
    print(f"\n🎯 ROOT CAUSE ANALYSIS:")
    print("=" * 60)
    
    if not chat_success or not llm_success:
        print("🔍 Possible causes for API failures:")
        print("  - EMERGENT_LLM_KEY invalid or expired")
        print("  - emergentintegrations library not installed properly")
        print("  - Network connectivity issues")
        print("  - Backend service configuration problems")
    
    if chat_time > 10 or any(r['response_time'] > 10 for r in provider_results.values() if r['success']):
        print("🔍 Possible causes for slow responses:")
        print("  - AI model processing complexity")
        print("  - EMERGENT_LLM_KEY rate limiting")
        print("  - Network latency to AI providers")
        print("  - Database query performance issues")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 All tests passed! Aavana 2.0 is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {tester.tests_run - tester.tests_passed} tests failed. Issues need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())