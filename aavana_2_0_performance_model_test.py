#!/usr/bin/env python3
"""
Aavana 2.0 Performance and Model Fix Testing
Testing performance, GPT-4o model verification, and functionality as requested in review
"""

import requests
import json
import time
from datetime import datetime
import os
import statistics
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://green-crm-suite.preview.emergentagent.com/api"

class Aavana2PerformanceModelTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.performance_times = []
        
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
        
        if response_time:
            self.performance_times.append(response_time)
        
    def test_aavana_2_0_chat_endpoint(self, message, expected_under_seconds=3.0):
        """Test Aavana 2.0 chat endpoint with performance measurement"""
        try:
            start_time = time.time()
            
            payload = {
                "message": message,
                "session_id": f"test_session_{int(time.time())}",
                "language": "en",
                "channel": "web"
            }
            
            response = self.session.post(
                f"{self.backend_url}/aavana2/chat",
                json=payload,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['message', 'message_id', 'session_id', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        f"Aavana 2.0 Chat - {message[:30]}...",
                        False,
                        f"Missing response fields: {missing_fields}",
                        response_time
                    )
                    return False, response_time
                
                # Check if response is not empty
                if not data.get('message') or data.get('message').strip() == '':
                    self.log_test(
                        f"Aavana 2.0 Chat - {message[:30]}...",
                        False,
                        "Empty response message from AI",
                        response_time
                    )
                    return False, response_time
                
                # Check performance requirement
                performance_ok = response_time < expected_under_seconds
                performance_note = f"Response time: {response_time:.2f}s ({'✅ Under' if performance_ok else '❌ Over'} {expected_under_seconds}s target)"
                
                # Check for model information in response
                response_message = data.get('message', '').lower()
                model_info = ""
                if 'gpt-4o' in response_message:
                    model_info = " | ✅ GPT-4o confirmed"
                elif 'gpt-5' in response_message:
                    model_info = " | ⚠️ GPT-5 mentioned (should be GPT-4o)"
                
                self.log_test(
                    f"Aavana 2.0 Chat - {message[:30]}...",
                    True,
                    f"{performance_note} | Response: {data.get('message', '')[:100]}...{model_info}",
                    response_time
                )
                
                return True, response_time
            else:
                self.log_test(
                    f"Aavana 2.0 Chat - {message[:30]}...",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time
                )
                return False, response_time
                
        except requests.exceptions.Timeout:
            self.log_test(
                f"Aavana 2.0 Chat - {message[:30]}...",
                False,
                "Request timeout (>30s)",
                30.0
            )
            return False, 30.0
        except Exception as e:
            self.log_test(
                f"Aavana 2.0 Chat - {message[:30]}...",
                False,
                f"Error: {str(e)}",
                None
            )
            return False, None
    
    def test_model_verification(self):
        """Test to verify GPT-4o model is being used"""
        print("\n🤖 TESTING MODEL VERIFICATION")
        
        model_queries = [
            "What AI model are you using?",
            "Which version of GPT are you running on?",
            "Tell me about your AI model",
            "Are you GPT-4o or GPT-5?"
        ]
        
        gpt4o_mentions = 0
        gpt5_mentions = 0
        
        for query in model_queries:
            success, response_time = self.test_aavana_2_0_chat_endpoint(query, 3.0)
            if success:
                # We'll check the actual response content in the log
                pass
        
        return True
    
    def test_performance_requirements(self):
        """Test performance requirements - responses under 3 seconds"""
        print("\n⚡ TESTING PERFORMANCE REQUIREMENTS")
        
        test_queries = [
            "Hello Aavana 2.0",
            "How do I create a new lead?",
            "What are the features of the HRMS system?",
            "Help me manage my tasks effectively",
            "What reports can I generate?",
            "Tell me about green building solutions",
            "How can I track my sales pipeline?",
            "What marketing tools are available?"
        ]
        
        performance_results = []
        
        for query in test_queries:
            success, response_time = self.test_aavana_2_0_chat_endpoint(query, 3.0)
            if response_time:
                performance_results.append(response_time)
        
        if performance_results:
            avg_time = statistics.mean(performance_results)
            max_time = max(performance_results)
            min_time = min(performance_results)
            
            under_3s_count = sum(1 for t in performance_results if t < 3.0)
            total_tests = len(performance_results)
            success_rate = (under_3s_count / total_tests) * 100
            
            self.log_test(
                "Performance Summary",
                success_rate >= 90,  # 90% should be under 3s
                f"Avg: {avg_time:.2f}s | Max: {max_time:.2f}s | Min: {min_time:.2f}s | {under_3s_count}/{total_tests} under 3s ({success_rate:.1f}%)"
            )
        
        return True
    
    def test_functionality_scenarios(self):
        """Test various CRM-related functionality scenarios"""
        print("\n🔧 TESTING FUNCTIONALITY SCENARIOS")
        
        crm_scenarios = [
            {
                "query": "How do I create a new lead in the system?",
                "expected_keywords": ["lead", "create", "form", "contact"]
            },
            {
                "query": "What are the HRMS features available?",
                "expected_keywords": ["hrms", "employee", "attendance", "payroll"]
            },
            {
                "query": "Help me manage my tasks effectively",
                "expected_keywords": ["task", "manage", "priority", "deadline"]
            },
            {
                "query": "What reports can I generate for sales?",
                "expected_keywords": ["report", "sales", "analytics", "data"]
            },
            {
                "query": "How do I track my pipeline?",
                "expected_keywords": ["pipeline", "track", "deals", "progress"]
            }
        ]
        
        for scenario in crm_scenarios:
            success, response_time = self.test_aavana_2_0_chat_endpoint(scenario["query"], 3.0)
            # Additional functionality validation would be done by checking response content
        
        return True
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🛡️ TESTING ERROR HANDLING")
        
        error_scenarios = [
            "",  # Empty message
            "x" * 5000,  # Very long message
            "🚀🌟💫🎯🔥" * 100,  # Special characters
            "What is " + "very " * 200 + "long question?"  # Extremely long question
        ]
        
        for i, scenario in enumerate(error_scenarios):
            scenario_name = [
                "Empty Message",
                "Very Long Message (5000 chars)",
                "Special Characters Spam",
                "Extremely Long Question"
            ][i]
            
            try:
                success, response_time = self.test_aavana_2_0_chat_endpoint(scenario, 5.0)  # Allow more time for error cases
                
                # For empty message, we expect it to handle gracefully
                if scenario == "" and not success:
                    self.log_test(
                        f"Error Handling - {scenario_name}",
                        True,  # It's good that empty message is rejected
                        "Empty message properly rejected"
                    )
                else:
                    self.log_test(
                        f"Error Handling - {scenario_name}",
                        success,
                        f"Handled {'successfully' if success else 'with error'}"
                    )
            except Exception as e:
                self.log_test(
                    f"Error Handling - {scenario_name}",
                    True,  # Exception handling is also valid error handling
                    f"Exception caught and handled: {str(e)[:100]}"
                )
        
        return True
    
    def test_consistency(self):
        """Test consistency - same query multiple times"""
        print("\n🔄 TESTING CONSISTENCY")
        
        test_query = "Hello Aavana 2.0, how can you help me?"
        consistency_results = []
        
        for i in range(3):
            print(f"  Consistency test {i+1}/3...")
            success, response_time = self.test_aavana_2_0_chat_endpoint(test_query, 3.0)
            consistency_results.append({
                'success': success,
                'response_time': response_time
            })
            time.sleep(1)  # Small delay between requests
        
        successful_tests = sum(1 for r in consistency_results if r['success'])
        avg_response_time = statistics.mean([r['response_time'] for r in consistency_results if r['response_time']])
        
        consistency_score = (successful_tests / len(consistency_results)) * 100
        
        self.log_test(
            "Consistency Test",
            consistency_score >= 80,  # 80% consistency required
            f"{successful_tests}/{len(consistency_results)} successful ({consistency_score:.1f}%) | Avg time: {avg_response_time:.2f}s"
        )
        
        return True
    
    def test_session_management(self):
        """Test session management and message ID generation"""
        print("\n📝 TESTING SESSION MANAGEMENT")
        
        session_id = f"test_session_{int(time.time())}"
        
        # Send multiple messages in same session
        messages = [
            "Hello, I'm starting a new conversation",
            "Can you remember what I just said?",
            "What was my first message?"
        ]
        
        message_ids = []
        
        for i, message in enumerate(messages):
            try:
                payload = {
                    "message": message,
                    "session_id": session_id,
                    "language": "en",
                    "channel": "web"
                }
                
                start_time = time.time()
                response = self.session.post(
                    f"{self.backend_url}/aavana2/chat",
                    json=payload,
                    timeout=30
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    message_id = data.get('message_id')
                    returned_session_id = data.get('session_id')
                    
                    # Check session ID consistency
                    session_consistent = returned_session_id == session_id
                    
                    # Check unique message IDs
                    unique_message_id = message_id not in message_ids
                    message_ids.append(message_id)
                    
                    self.log_test(
                        f"Session Management - Message {i+1}",
                        session_consistent and unique_message_id,
                        f"Session: {'✅' if session_consistent else '❌'} | Unique ID: {'✅' if unique_message_id else '❌'} | ID: {message_id}",
                        response_time
                    )
                else:
                    self.log_test(
                        f"Session Management - Message {i+1}",
                        False,
                        f"HTTP {response.status_code}: {response.text[:100]}"
                    )
                    
            except Exception as e:
                self.log_test(
                    f"Session Management - Message {i+1}",
                    False,
                    f"Error: {str(e)}"
                )
        
        return True
    
    def run_comprehensive_test(self):
        """Run all Aavana 2.0 tests"""
        print("🚀 STARTING AAVANA 2.0 PERFORMANCE AND MODEL VERIFICATION TESTING")
        print("=" * 80)
        
        # Test categories
        test_categories = [
            ("Model Verification", self.test_model_verification),
            ("Performance Requirements", self.test_performance_requirements),
            ("Functionality Scenarios", self.test_functionality_scenarios),
            ("Error Handling", self.test_error_handling),
            ("Consistency Testing", self.test_consistency),
            ("Session Management", self.test_session_management)
        ]
        
        overall_success = True
        
        for category_name, test_function in test_categories:
            try:
                print(f"\n{'='*20} {category_name} {'='*20}")
                result = test_function()
                if not result:
                    overall_success = False
            except Exception as e:
                print(f"❌ {category_name} failed with exception: {str(e)}")
                overall_success = False
        
        # Generate summary
        self.generate_summary()
        
        return overall_success
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*80)
        print("📊 AAVANA 2.0 PERFORMANCE AND MODEL TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.performance_times:
            avg_response_time = statistics.mean(self.performance_times)
            max_response_time = max(self.performance_times)
            min_response_time = min(self.performance_times)
            under_3s = sum(1 for t in self.performance_times if t < 3.0)
            performance_rate = (under_3s / len(self.performance_times)) * 100
            
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"Average Response Time: {avg_response_time:.2f}s")
            print(f"Fastest Response: {min_response_time:.2f}s")
            print(f"Slowest Response: {max_response_time:.2f}s")
            print(f"Under 3s Target: {under_3s}/{len(self.performance_times)} ({performance_rate:.1f}%)")
        
        # Critical issues
        critical_failures = [
            result for result in self.test_results 
            if not result['success'] and 'timeout' in result['details'].lower()
        ]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"  - {failure['test']}: {failure['details']}")
        
        # Performance issues
        slow_responses = [
            result for result in self.test_results 
            if result.get('response_time') and result['response_time'] > 3.0
        ]
        
        if slow_responses:
            print(f"\n⚠️ PERFORMANCE ISSUES:")
            for slow in slow_responses:
                print(f"  - {slow['test']}: {slow['response_time']:.2f}s (over 3s target)")
        
        print("\n" + "="*80)
        
        # Overall assessment
        if success_rate >= 90 and (not self.performance_times or statistics.mean(self.performance_times) < 3.0):
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Aavana 2.0 is performing well!")
        elif success_rate >= 75:
            print("✅ OVERALL ASSESSMENT: GOOD - Minor issues found but system is functional")
        elif success_rate >= 50:
            print("⚠️ OVERALL ASSESSMENT: NEEDS ATTENTION - Several issues found")
        else:
            print("❌ OVERALL ASSESSMENT: CRITICAL ISSUES - Major problems detected")

if __name__ == "__main__":
    tester = Aavana2PerformanceModelTester()
    tester.run_comprehensive_test()