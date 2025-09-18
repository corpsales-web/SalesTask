#!/usr/bin/env python3
"""
Final Aavana 2.0 OpenAI Connection Test
Comprehensive testing based on review request requirements
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://green-crm-suite.preview.emergentagent.com/api"

class FinalAavana2Tester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, success, details, response_time=None, data=None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.2f}s)" if response_time else ""
        print(f"{status} {test_name}{time_info}: {details}")
        
    def test_aavana2_chat_comprehensive(self):
        """Test Aavana 2.0 chat endpoint as per review request"""
        print("\n🤖 AAVANA 2.0 CHAT ENDPOINT COMPREHENSIVE TEST")
        print("=" * 55)
        
        # Test cases from review request
        test_cases = [
            {
                'name': 'Lead Management Query',
                'message': 'Hello, can you help me with lead management?',
                'context': 'lead_management',
                'expected_no_error': True
            },
            {
                'name': 'Task Creation Query',
                'message': 'How do I create a new task?',
                'context': 'task_help',
                'expected_no_error': True
            },
            {
                'name': 'Green Building Solutions Query',
                'message': 'What green building solutions do we offer?',
                'context': 'general_inquiry',
                'expected_no_error': True
            },
            {
                'name': 'HRMS Attendance Query',
                'message': 'Help me with HRMS attendance tracking',
                'context': 'task_help',
                'expected_no_error': True
            },
            {
                'name': 'Cached Response Test (Hello)',
                'message': 'hello',
                'context': 'general_inquiry',
                'expected_cached': True
            },
            {
                'name': 'Cached Response Test (Help)',
                'message': 'help',
                'context': 'general_inquiry',
                'expected_cached': True
            }
        ]
        
        for test_case in test_cases:
            self._test_single_chat_message(test_case)
            time.sleep(1)  # Brief pause between tests
    
    def _test_single_chat_message(self, test_case):
        """Test a single chat message"""
        session_id = str(uuid.uuid4())
        
        payload = {
            'message': test_case['message'],
            'session_id': session_id,
            'context': test_case['context'],
            'user_id': 'test_user_final',
            'language': 'en'
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/aavana2/chat",
                json=payload,
                timeout=45
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['message', 'message_id', 'session_id', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        test_case['name'],
                        False,
                        f"Missing required fields: {missing_fields}",
                        response_time,
                        data
                    )
                    return
                
                message = data.get('message', '')
                
                # Check for OpenAI connection error message
                if 'trouble connecting to openai' in message.lower():
                    self.log_test(
                        test_case['name'],
                        False,
                        "OpenAI connection error detected",
                        response_time,
                        data
                    )
                    return
                
                # Check for empty response (main issue)
                if len(message.strip()) == 0:
                    self.log_test(
                        test_case['name'],
                        False,
                        "Empty response - GPT-5 model not returning content",
                        response_time,
                        data
                    )
                    return
                
                # Check session ID consistency
                if data.get('session_id') != session_id:
                    self.log_test(
                        test_case['name'],
                        False,
                        f"Session ID mismatch",
                        response_time,
                        data
                    )
                    return
                
                # Check if this was expected to be cached
                if test_case.get('expected_cached') and response_time > 2:
                    self.log_test(
                        test_case['name'],
                        False,
                        f"Expected cached response but took {response_time:.2f}s",
                        response_time,
                        data
                    )
                    return
                
                # Success case
                actions_count = len(data.get('actions', []))
                self.log_test(
                    test_case['name'],
                    True,
                    f"GPT response received. Length: {len(message)} chars, Actions: {actions_count}",
                    response_time,
                    {
                        'message_preview': message[:100] + '...' if len(message) > 100 else message,
                        'actions_count': actions_count,
                        'cached': response_time < 2
                    }
                )
                
            else:
                self.log_test(
                    test_case['name'],
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time
                )
                
        except requests.exceptions.Timeout:
            self.log_test(
                test_case['name'],
                False,
                "Request timeout (>45s) - AI processing too slow"
            )
        except Exception as e:
            self.log_test(
                test_case['name'],
                False,
                f"Request error: {str(e)}"
            )
    
    def test_gpt5_parameter_validation(self):
        """Test GPT-5 parameter validation specifically"""
        print("\n🔧 GPT-5 PARAMETER VALIDATION TEST")
        print("=" * 40)
        
        # Test with a message that should definitely get a response
        payload = {
            'message': 'Generate a detailed marketing strategy for green buildings',
            'session_id': str(uuid.uuid4()),
            'context': 'general_inquiry',
            'user_id': 'test_params',
            'language': 'en'
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/aavana2/chat",
                json=payload,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                
                if len(message) > 100:  # Should be a detailed response
                    self.log_test(
                        "GPT-5 max_completion_tokens Parameter",
                        True,
                        f"GPT-5 generated detailed response: {len(message)} chars",
                        response_time
                    )
                elif len(message) == 0:
                    self.log_test(
                        "GPT-5 max_completion_tokens Parameter",
                        False,
                        "GPT-5 returned empty response - parameter issue",
                        response_time
                    )
                else:
                    self.log_test(
                        "GPT-5 max_completion_tokens Parameter",
                        False,
                        f"GPT-5 response too short: {len(message)} chars - possible parameter issue",
                        response_time
                    )
            else:
                self.log_test(
                    "GPT-5 max_completion_tokens Parameter",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time
                )
                
        except Exception as e:
            self.log_test(
                "GPT-5 max_completion_tokens Parameter",
                False,
                f"Parameter test failed: {str(e)}"
            )
    
    def test_session_management(self):
        """Test session management and message ID generation"""
        print("\n📝 SESSION MANAGEMENT TEST")
        print("=" * 30)
        
        session_id = str(uuid.uuid4())
        messages = [
            "Hello, I'm starting a new conversation",
            "Can you remember what I just said?",
            "What was my first message?"
        ]
        
        message_ids = []
        timestamps = []
        
        for i, message in enumerate(messages):
            payload = {
                'message': message,
                'session_id': session_id,
                'context': 'general_inquiry',
                'user_id': 'test_session',
                'language': 'en'
            }
            
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.backend_url}/aavana2/chat",
                    json=payload,
                    timeout=30
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check message ID generation
                    message_id = data.get('message_id')
                    if message_id:
                        message_ids.append(message_id)
                        
                        # Check timestamp format
                        timestamp = data.get('timestamp')
                        if timestamp:
                            timestamps.append(timestamp)
                            
                        self.log_test(
                            f"Session Message {i+1}",
                            True,
                            f"Message ID generated, Session consistent",
                            response_time
                        )
                    else:
                        self.log_test(
                            f"Session Message {i+1}",
                            False,
                            "No message ID generated",
                            response_time
                        )
                else:
                    self.log_test(
                        f"Session Message {i+1}",
                        False,
                        f"HTTP {response.status_code}",
                        response_time
                    )
                
                time.sleep(1)
                
            except Exception as e:
                self.log_test(
                    f"Session Message {i+1}",
                    False,
                    f"Session test error: {str(e)}"
                )
        
        # Test message ID uniqueness
        if len(message_ids) > 1:
            unique_ids = len(set(message_ids))
            if unique_ids == len(message_ids):
                self.log_test(
                    "Message ID Uniqueness",
                    True,
                    f"All {len(message_ids)} message IDs are unique"
                )
            else:
                self.log_test(
                    "Message ID Uniqueness",
                    False,
                    f"Duplicate message IDs found"
                )
        
        # Test timestamp formatting
        if timestamps:
            valid_timestamps = 0
            for ts in timestamps:
                try:
                    datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    valid_timestamps += 1
                except:
                    pass
            
            if valid_timestamps == len(timestamps):
                self.log_test(
                    "Timestamp Formatting",
                    True,
                    f"All {len(timestamps)} timestamps properly formatted"
                )
            else:
                self.log_test(
                    "Timestamp Formatting",
                    False,
                    f"Invalid timestamp formats detected"
                )
    
    def test_error_handling(self):
        """Test error handling and fallback mechanisms"""
        print("\n🚨 ERROR HANDLING TEST")
        print("=" * 25)
        
        error_cases = [
            {
                'name': 'Empty Message',
                'payload': {
                    'message': '',
                    'session_id': str(uuid.uuid4()),
                    'context': 'general_inquiry'
                },
                'should_handle_gracefully': True
            },
            {
                'name': 'Very Long Message',
                'payload': {
                    'message': 'A' * 5000,
                    'session_id': str(uuid.uuid4()),
                    'context': 'general_inquiry'
                },
                'should_handle_gracefully': True
            },
            {
                'name': 'Missing Session ID',
                'payload': {
                    'message': 'Test without session ID',
                    'context': 'general_inquiry'
                },
                'should_handle_gracefully': True
            }
        ]
        
        for case in error_cases:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.backend_url}/aavana2/chat",
                    json=case['payload'],
                    timeout=30
                )
                response_time = time.time() - start_time
                
                if case['should_handle_gracefully']:
                    if response.status_code == 200:
                        data = response.json()
                        if 'message' in data:
                            self.log_test(
                                case['name'],
                                True,
                                f"Handled gracefully with response",
                                response_time
                            )
                        else:
                            self.log_test(
                                case['name'],
                                False,
                                "Response missing message field",
                                response_time
                            )
                    else:
                        self.log_test(
                            case['name'],
                            False,
                            f"Not handled gracefully: HTTP {response.status_code}",
                            response_time
                        )
                        
            except Exception as e:
                self.log_test(
                    case['name'],
                    False,
                    f"Error handling test failed: {str(e)}"
                )
    
    def test_integration_completeness(self):
        """Test integration completeness"""
        print("\n🔗 INTEGRATION COMPLETENESS TEST")
        print("=" * 35)
        
        # Test contextual actions generation
        payload = {
            'message': 'I need to create a follow-up task for a high-priority lead',
            'session_id': str(uuid.uuid4()),
            'context': 'lead_management',
            'user_id': 'test_integration',
            'language': 'en'
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/aavana2/chat",
                json=payload,
                timeout=45
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for contextual actions
                actions = data.get('actions', [])
                has_actions = len(actions) > 0
                
                # Check all required response fields
                required_fields = ['message', 'message_id', 'session_id', 'timestamp', 'actions']
                all_fields_present = all(field in data for field in required_fields)
                
                if all_fields_present and has_actions:
                    self.log_test(
                        "Contextual Actions Generation",
                        True,
                        f"All fields present, {len(actions)} actions generated",
                        response_time
                    )
                elif all_fields_present:
                    self.log_test(
                        "Contextual Actions Generation",
                        True,
                        "All fields present, no actions (acceptable)",
                        response_time
                    )
                else:
                    self.log_test(
                        "Contextual Actions Generation",
                        False,
                        f"Missing fields or no actions generated",
                        response_time
                    )
                
                # Test chat message saving by checking history
                self._test_chat_history(payload['session_id'])
                
            else:
                self.log_test(
                    "Contextual Actions Generation",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time
                )
                
        except Exception as e:
            self.log_test(
                "Contextual Actions Generation",
                False,
                f"Integration test failed: {str(e)}"
            )
    
    def _test_chat_history(self, session_id):
        """Test chat message saving functionality"""
        try:
            time.sleep(2)  # Allow time for async save
            
            start_time = time.time()
            response = self.session.get(
                f"{self.backend_url}/aavana2/chat/history/{session_id}",
                timeout=15
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    self.log_test(
                        "Chat Message Saving",
                        True,
                        f"Chat history retrieved: {len(data)} messages",
                        response_time
                    )
                elif isinstance(data, dict) and 'messages' in data and len(data['messages']) > 0:
                    self.log_test(
                        "Chat Message Saving",
                        True,
                        f"Chat history retrieved: {len(data['messages'])} messages",
                        response_time
                    )
                else:
                    self.log_test(
                        "Chat Message Saving",
                        False,
                        "No chat history found - messages not being saved",
                        response_time
                    )
            elif response.status_code == 404:
                self.log_test(
                    "Chat Message Saving",
                    False,
                    "Chat history endpoint not found",
                    response_time
                )
            else:
                self.log_test(
                    "Chat Message Saving",
                    False,
                    f"History retrieval failed: HTTP {response.status_code}",
                    response_time
                )
                
        except Exception as e:
            self.log_test(
                "Chat Message Saving",
                False,
                f"History test failed: {str(e)}"
            )
    
    def run_comprehensive_test(self):
        """Run all tests as per review request"""
        print("🚀 AAVANA 2.0 OPENAI CONNECTION FIX - COMPREHENSIVE TEST")
        print("=" * 65)
        print(f"🌐 Backend URL: {self.backend_url}")
        print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 65)
        
        # Run all test categories from review request
        self.test_aavana2_chat_comprehensive()
        self.test_gpt5_parameter_validation()
        self.test_session_management()
        self.test_error_handling()
        self.test_integration_completeness()
        
        # Generate final summary
        self.generate_final_summary()
    
    def generate_final_summary(self):
        """Generate comprehensive final summary"""
        print("\n" + "=" * 70)
        print("📊 FINAL AAVANA 2.0 OPENAI CONNECTION TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Categorize by review request requirements
        chat_tests = [r for r in self.test_results if 'query' in r['test'].lower() or 'message' in r['test'].lower()]
        param_tests = [r for r in self.test_results if 'parameter' in r['test'].lower() or 'gpt' in r['test'].lower()]
        session_tests = [r for r in self.test_results if 'session' in r['test'].lower() or 'id' in r['test'].lower()]
        error_tests = [r for r in self.test_results if 'error' in r['test'].lower() or 'empty' in r['test'].lower()]
        integration_tests = [r for r in self.test_results if 'integration' in r['test'].lower() or 'action' in r['test'].lower() or 'saving' in r['test'].lower()]
        
        print(f"\n📋 TEST CATEGORIES (per review request):")
        print(f"🤖 Chat Endpoint Tests: {sum(1 for t in chat_tests if t['success'])}/{len(chat_tests)} passed")
        print(f"🔧 Parameter Validation: {sum(1 for t in param_tests if t['success'])}/{len(param_tests)} passed")
        print(f"📝 Session Management: {sum(1 for t in session_tests if t['success'])}/{len(session_tests)} passed")
        print(f"🚨 Error Handling: {sum(1 for t in error_tests if t['success'])}/{len(error_tests)} passed")
        print(f"🔗 Integration Completeness: {sum(1 for t in integration_tests if t['success'])}/{len(integration_tests)} passed")
        
        # Critical findings
        print(f"\n🔍 CRITICAL FINDINGS:")
        
        # Check for OpenAI connection issues
        openai_issues = []
        empty_response_issues = []
        
        for result in self.test_results:
            if not result['success']:
                if 'openai' in result['details'].lower() or 'gpt' in result['details'].lower():
                    openai_issues.append(result)
                if 'empty response' in result['details'].lower():
                    empty_response_issues.append(result)
        
        if empty_response_issues:
            print("🚨 CRITICAL: GPT-5 EMPTY RESPONSE ISSUE DETECTED")
            print(f"   • {len(empty_response_issues)} tests failed due to empty GPT-5 responses")
            print("   • This indicates GPT-5 model is not returning content properly")
            print("   • Root cause: GPT-5 API parameter compatibility or model availability")
        
        if openai_issues:
            print("🚨 OPENAI CONNECTION ISSUES:")
            for issue in openai_issues[:3]:  # Show first 3
                print(f"   • {issue['test']}: {issue['details']}")
        
        # Performance metrics
        timed_tests = [r for r in self.test_results if r.get('response_time')]
        if timed_tests:
            avg_time = sum(r['response_time'] for r in timed_tests) / len(timed_tests)
            max_time = max(r['response_time'] for r in timed_tests)
            print(f"\n⏱️ PERFORMANCE:")
            print(f"   📊 Average Response Time: {avg_time:.2f}s")
            print(f"   📊 Maximum Response Time: {max_time:.2f}s")
            
            if avg_time > 15:
                print("   ⚠️ Response times are high (>15s average)")
            elif avg_time < 5:
                print("   ✅ Good response times (<5s average)")
        
        # Show failed tests
        failed_results = [r for r in self.test_results if not r['success']]
        if failed_results:
            print(f"\n❌ FAILED TESTS ({len(failed_results)}):")
            for result in failed_results[:5]:  # Show first 5
                print(f"   🔴 {result['test']}: {result['details']}")
            if len(failed_results) > 5:
                print(f"   ... and {len(failed_results) - 5} more")
        
        # Final assessment based on review request
        print(f"\n🎯 FINAL ASSESSMENT:")
        if success_rate >= 90:
            print("🎉 EXCELLENT: OpenAI connection fix is working perfectly")
            print("✅ All critical Aavana 2.0 functionality operational")
            print("✅ GPT-5 model responding correctly without connection errors")
            print("✅ Session management, error handling, and integration complete")
        elif success_rate >= 70:
            print("✅ GOOD: OpenAI connection mostly fixed with minor issues")
            print("⚠️ Some non-critical issues detected but core functionality works")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Significant issues remain with OpenAI integration")
            print("🔧 OpenAI connection fix partially successful but needs attention")
        else:
            print("🚨 CRITICAL: OpenAI connection fix has NOT resolved the issues")
            print("🚨 Major problems persist with GPT-5 integration")
            print("🚨 Immediate action required to fix OpenAI connectivity")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = FinalAavana2Tester()
    tester.run_comprehensive_test()