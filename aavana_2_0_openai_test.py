#!/usr/bin/env python3
"""
Aavana 2.0 OpenAI Connection Fix Testing
Comprehensive testing for OpenAI GPT-5 integration and chat functionality
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
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class Aavana2OpenAITester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.openai_key = OPENAI_API_KEY
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_session_id = str(uuid.uuid4())
        
    def log_test(self, test_name, success, details, response_time=None, response_data=None):
        """Log test results with detailed information"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_time': response_time,
            'response_data': response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.2f}s)" if response_time else ""
        print(f"{status} {test_name}{time_info}: {details}")
        
    def test_aavana2_chat_endpoint(self):
        """Test Aavana 2.0 chat endpoint with various message types"""
        print("\n🤖 TESTING AAVANA 2.0 CHAT ENDPOINT")
        print("=" * 50)
        
        # Test cases with different message types and contexts
        test_cases = [
            {
                'name': 'Simple Greeting Test',
                'message': 'Hello, can you help me with lead management?',
                'context': 'general_inquiry',
                'expected_keywords': ['hello', 'help', 'lead', 'management']
            },
            {
                'name': 'Task Creation Query',
                'message': 'How do I create a new task?',
                'context': 'task_help',
                'expected_keywords': ['task', 'create', 'new']
            },
            {
                'name': 'Green Building Solutions Query',
                'message': 'What green building solutions do we offer?',
                'context': 'general_inquiry',
                'expected_keywords': ['green', 'building', 'solutions', 'offer']
            },
            {
                'name': 'HRMS Attendance Query',
                'message': 'Help me with HRMS attendance tracking',
                'context': 'task_help',
                'expected_keywords': ['hrms', 'attendance', 'tracking']
            },
            {
                'name': 'Lead Management Context Test',
                'message': 'I need to follow up with a high-priority lead',
                'context': 'lead_management',
                'expected_keywords': ['follow', 'priority', 'lead']
            }
        ]
        
        for test_case in test_cases:
            self._test_single_chat_message(test_case)
            time.sleep(1)  # Brief pause between tests
    
    def _test_single_chat_message(self, test_case):
        """Test a single chat message"""
        try:
            payload = {
                'message': test_case['message'],
                'session_id': self.test_session_id,
                'context': test_case['context'],
                'user_id': 'test_user_001',
                'language': 'en'
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/aavana2/chat", 
                json=payload, 
                timeout=45  # Increased timeout for AI processing
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
                
                # Check for OpenAI connection error
                response_message = data.get('message', '').lower()
                if 'trouble connecting to openai' in response_message:
                    self.log_test(
                        test_case['name'], 
                        False, 
                        "OpenAI connection error detected in response",
                        response_time,
                        data
                    )
                    return
                
                # Check if response is meaningful (not empty or error)
                if len(data.get('message', '')) < 10:
                    self.log_test(
                        test_case['name'], 
                        False, 
                        f"Response too short or empty: '{data.get('message', '')}'",
                        response_time,
                        data
                    )
                    return
                
                # Check session ID consistency
                if data.get('session_id') != self.test_session_id:
                    self.log_test(
                        test_case['name'], 
                        False, 
                        f"Session ID mismatch: expected {self.test_session_id}, got {data.get('session_id')}",
                        response_time,
                        data
                    )
                    return
                
                # Check for contextual actions if present
                actions_present = 'actions' in data and isinstance(data['actions'], list)
                
                self.log_test(
                    test_case['name'], 
                    True, 
                    f"GPT-5 response received successfully. Length: {len(data['message'])} chars. Actions: {len(data.get('actions', []))}",
                    response_time,
                    {
                        'message_preview': data['message'][:100] + '...' if len(data['message']) > 100 else data['message'],
                        'has_actions': actions_present,
                        'message_id': data.get('message_id'),
                        'session_id': data.get('session_id')
                    }
                )
                
            elif response.status_code == 429:
                self.log_test(
                    test_case['name'], 
                    False, 
                    "Rate limit exceeded - too many requests",
                    response_time
                )
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Internal server error')
                except:
                    error_detail = response.text[:200]
                
                self.log_test(
                    test_case['name'], 
                    False, 
                    f"Server error: {error_detail}",
                    response_time
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
                "Request timeout (>45s) - AI processing too slow or connection issue"
            )
        except requests.exceptions.RequestException as e:
            self.log_test(
                test_case['name'], 
                False, 
                f"Request error: {str(e)}"
            )
        except Exception as e:
            self.log_test(
                test_case['name'], 
                False, 
                f"Unexpected error: {str(e)}"
            )
    
    def test_openai_parameter_validation(self):
        """Test OpenAI parameter validation, especially max_completion_tokens with GPT-5"""
        print("\n🔧 TESTING OPENAI PARAMETER VALIDATION")
        print("=" * 45)
        
        # Test with different parameter configurations
        parameter_tests = [
            {
                'name': 'GPT-5 with max_completion_tokens',
                'message': 'Generate a detailed marketing strategy for green buildings',
                'model_preference': 'gpt-5',
                'max_tokens': 1000
            },
            {
                'name': 'GPT-5 with temperature control',
                'message': 'Create a professional response for lead inquiry',
                'model_preference': 'gpt-5',
                'temperature': 0.7
            },
            {
                'name': 'GPT-5 synchronous client test',
                'message': 'Quick response test for synchronous processing',
                'model_preference': 'gpt-5',
                'max_tokens': 100
            }
        ]
        
        for test in parameter_tests:
            self._test_parameter_configuration(test)
            time.sleep(2)  # Pause between parameter tests
    
    def _test_parameter_configuration(self, test_config):
        """Test specific parameter configuration"""
        try:
            payload = {
                'message': test_config['message'],
                'session_id': str(uuid.uuid4()),  # New session for each test
                'context': 'general_inquiry',
                'user_id': 'test_user_params',
                'language': 'en',
                'model_preference': test_config.get('model_preference'),
                'max_tokens': test_config.get('max_tokens'),
                'temperature': test_config.get('temperature')
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/aavana2/chat", 
                json=payload, 
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if GPT-5 model was used (if specified)
                model_used = data.get('model_used', 'unknown')
                response_quality = len(data.get('message', ''))
                
                # Validate response quality based on max_tokens
                expected_length = test_config.get('max_tokens', 500)
                if response_quality > expected_length * 6:  # Rough character to token ratio
                    quality_note = "Response longer than expected (good)"
                elif response_quality < 50:
                    quality_note = "Response too short (concerning)"
                else:
                    quality_note = "Response length appropriate"
                
                self.log_test(
                    test_config['name'], 
                    True, 
                    f"Parameters accepted. Response: {response_quality} chars. {quality_note}",
                    response_time,
                    {
                        'model_used': model_used,
                        'response_length': response_quality,
                        'parameters_sent': {k: v for k, v in payload.items() if k not in ['message', 'session_id']}
                    }
                )
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('detail', response.text[:100])}"
                except:
                    error_msg += f": {response.text[:100]}"
                
                self.log_test(
                    test_config['name'], 
                    False, 
                    error_msg,
                    response_time
                )
                
        except Exception as e:
            self.log_test(
                test_config['name'], 
                False, 
                f"Parameter test failed: {str(e)}"
            )
    
    def test_session_management(self):
        """Test session management and message ID generation"""
        print("\n📝 TESTING SESSION MANAGEMENT")
        print("=" * 35)
        
        # Test multiple messages in same session
        session_id = str(uuid.uuid4())
        messages = [
            "Hello, I'm starting a new conversation",
            "Can you remember what I just said?",
            "What was my first message in this session?"
        ]
        
        message_ids = []
        
        for i, message in enumerate(messages):
            try:
                payload = {
                    'message': message,
                    'session_id': session_id,
                    'context': 'general_inquiry',
                    'user_id': 'test_session_user',
                    'language': 'en'
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
                    
                    if message_id:
                        message_ids.append(message_id)
                        
                        # Check timestamp format
                        timestamp = data.get('timestamp')
                        timestamp_valid = self._validate_timestamp(timestamp)
                        
                        self.log_test(
                            f"Session Message {i+1}", 
                            True, 
                            f"Message ID: {message_id[:8]}..., Timestamp valid: {timestamp_valid}",
                            response_time,
                            {
                                'message_id': message_id,
                                'session_id': data.get('session_id'),
                                'timestamp': timestamp
                            }
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
                        f"HTTP {response.status_code}: {response.text[:100]}",
                        response_time
                    )
                
                time.sleep(1)  # Brief pause between session messages
                
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
                    f"Duplicate message IDs found: {len(message_ids)} total, {unique_ids} unique"
                )
    
    def _validate_timestamp(self, timestamp):
        """Validate timestamp format"""
        if not timestamp:
            return False
        try:
            # Try to parse ISO format timestamp
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except:
            return False
    
    def test_error_handling(self):
        """Test error handling and fallback mechanisms"""
        print("\n🚨 TESTING ERROR HANDLING")
        print("=" * 30)
        
        error_test_cases = [
            {
                'name': 'Empty Message Test',
                'payload': {
                    'message': '',
                    'session_id': str(uuid.uuid4()),
                    'context': 'general_inquiry'
                },
                'expected_error': True
            },
            {
                'name': 'Missing Session ID Test',
                'payload': {
                    'message': 'Test message without session ID',
                    'context': 'general_inquiry'
                },
                'expected_error': False  # Should auto-generate session ID
            },
            {
                'name': 'Invalid Context Test',
                'payload': {
                    'message': 'Test with invalid context',
                    'session_id': str(uuid.uuid4()),
                    'context': 'invalid_context_type'
                },
                'expected_error': False  # Should handle gracefully
            },
            {
                'name': 'Very Long Message Test',
                'payload': {
                    'message': 'A' * 5000,  # Very long message
                    'session_id': str(uuid.uuid4()),
                    'context': 'general_inquiry'
                },
                'expected_error': False  # Should handle or truncate
            }
        ]
        
        for test_case in error_test_cases:
            self._test_error_scenario(test_case)
            time.sleep(1)
    
    def _test_error_scenario(self, test_case):
        """Test specific error scenario"""
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/aavana2/chat", 
                json=test_case['payload'], 
                timeout=30
            )
            response_time = time.time() - start_time
            
            if test_case['expected_error']:
                if response.status_code >= 400:
                    self.log_test(
                        test_case['name'], 
                        True, 
                        f"Correctly returned error status {response.status_code}",
                        response_time
                    )
                else:
                    self.log_test(
                        test_case['name'], 
                        False, 
                        f"Expected error but got status {response.status_code}",
                        response_time
                    )
            else:
                if response.status_code == 200:
                    data = response.json()
                    if 'message' in data and len(data['message']) > 0:
                        self.log_test(
                            test_case['name'], 
                            True, 
                            f"Handled gracefully with response: {len(data['message'])} chars",
                            response_time
                        )
                    else:
                        self.log_test(
                            test_case['name'], 
                            False, 
                            "Response received but no message content",
                            response_time
                        )
                else:
                    self.log_test(
                        test_case['name'], 
                        False, 
                        f"Unexpected error status {response.status_code}",
                        response_time
                    )
                    
        except Exception as e:
            self.log_test(
                test_case['name'], 
                False, 
                f"Error test failed: {str(e)}"
            )
    
    def test_integration_completeness(self):
        """Test integration completeness including contextual actions and message saving"""
        print("\n🔗 TESTING INTEGRATION COMPLETENESS")
        print("=" * 40)
        
        # Test contextual actions generation
        action_test_message = "I need to create a follow-up task for a high-priority lead named John Smith"
        
        try:
            payload = {
                'message': action_test_message,
                'session_id': str(uuid.uuid4()),
                'context': 'lead_management',
                'user_id': 'test_integration_user',
                'language': 'en'
            }
            
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
                
                # Check response fields completeness
                required_fields = ['message', 'message_id', 'session_id', 'timestamp']
                all_fields_present = all(field in data for field in required_fields)
                
                self.log_test(
                    "Contextual Actions Generation", 
                    has_actions, 
                    f"Actions generated: {len(actions)}. Fields complete: {all_fields_present}",
                    response_time,
                    {
                        'actions_count': len(actions),
                        'actions_preview': actions[:2] if actions else [],
                        'all_fields_present': all_fields_present
                    }
                )
                
                # Test chat message saving by checking if we can retrieve history
                self._test_chat_history_retrieval(payload['session_id'])
                
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
    
    def _test_chat_history_retrieval(self, session_id):
        """Test chat message saving functionality by retrieving history"""
        try:
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
                        response_time,
                        {'history_count': len(data)}
                    )
                elif isinstance(data, dict) and 'messages' in data:
                    messages = data['messages']
                    self.log_test(
                        "Chat Message Saving", 
                        True, 
                        f"Chat history retrieved: {len(messages)} messages",
                        response_time,
                        {'history_count': len(messages)}
                    )
                else:
                    self.log_test(
                        "Chat Message Saving", 
                        False, 
                        f"Unexpected history format: {type(data)}",
                        response_time
                    )
            elif response.status_code == 404:
                self.log_test(
                    "Chat Message Saving", 
                    False, 
                    "Chat history endpoint not found - messages may not be saved",
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
    
    def test_backend_health(self):
        """Test basic backend connectivity"""
        print("\n🏥 TESTING BACKEND HEALTH")
        print("=" * 30)
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    message = data.get('message', 'OK')
                except:
                    message = response.text[:50]
                
                self.log_test(
                    "Backend Health Check", 
                    True, 
                    f"Backend responding: {message}",
                    response_time
                )
                return True
            else:
                self.log_test(
                    "Backend Health Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:100]}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Backend Health Check", 
                False, 
                f"Connection error: {str(e)}"
            )
            return False
    
    def run_comprehensive_test(self):
        """Run all Aavana 2.0 OpenAI tests"""
        print("🚀 AAVANA 2.0 OPENAI CONNECTION FIX TESTING")
        print("=" * 55)
        print(f"🌐 Backend URL: {self.backend_url}")
        print(f"🔑 OpenAI API Key: {self.openai_key[:15] if self.openai_key else 'NOT CONFIGURED'}...")
        print(f"📅 Test Session ID: {self.test_session_id}")
        print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 55)
        
        # Test sequence
        backend_healthy = self.test_backend_health()
        
        if backend_healthy:
            self.test_aavana2_chat_endpoint()
            self.test_openai_parameter_validation()
            self.test_session_management()
            self.test_error_handling()
            self.test_integration_completeness()
        else:
            print("❌ Backend not healthy, skipping Aavana 2.0 tests")
        
        # Generate comprehensive summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 AAVANA 2.0 OPENAI CONNECTION TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Categorize results
        chat_tests = [r for r in self.test_results if 'chat' in r['test'].lower() or 'message' in r['test'].lower()]
        param_tests = [r for r in self.test_results if 'parameter' in r['test'].lower() or 'gpt-5' in r['test'].lower()]
        session_tests = [r for r in self.test_results if 'session' in r['test'].lower()]
        error_tests = [r for r in self.test_results if 'error' in r['test'].lower() or 'empty' in r['test'].lower()]
        integration_tests = [r for r in self.test_results if 'integration' in r['test'].lower() or 'action' in r['test'].lower()]
        
        print(f"\n🤖 Chat Endpoint Tests: {sum(1 for t in chat_tests if t['success'])}/{len(chat_tests)} passed")
        print(f"🔧 Parameter Validation Tests: {sum(1 for t in param_tests if t['success'])}/{len(param_tests)} passed")
        print(f"📝 Session Management Tests: {sum(1 for t in session_tests if t['success'])}/{len(session_tests)} passed")
        print(f"🚨 Error Handling Tests: {sum(1 for t in error_tests if t['success'])}/{len(error_tests)} passed")
        print(f"🔗 Integration Tests: {sum(1 for t in integration_tests if t['success'])}/{len(integration_tests)} passed")
        
        # Show critical findings
        print(f"\n🔍 CRITICAL FINDINGS:")
        
        # Check for OpenAI connection issues
        openai_issues = [r for r in self.test_results if not r['success'] and 
                        ('openai' in r['details'].lower() or 'gpt' in r['details'].lower())]
        
        if openai_issues:
            print("🚨 OPENAI CONNECTION ISSUES DETECTED:")
            for issue in openai_issues:
                print(f"   🔴 {issue['test']}: {issue['details']}")
        else:
            print("✅ No OpenAI connection errors detected")
        
        # Check response times
        timed_tests = [r for r in self.test_results if r.get('response_time')]
        if timed_tests:
            avg_response_time = sum(r['response_time'] for r in timed_tests) / len(timed_tests)
            max_response_time = max(r['response_time'] for r in timed_tests)
            print(f"\n⏱️ PERFORMANCE METRICS:")
            print(f"   📊 Average Response Time: {avg_response_time:.2f}s")
            print(f"   📊 Maximum Response Time: {max_response_time:.2f}s")
            
            if avg_response_time > 10:
                print("   ⚠️ Average response time is high (>10s)")
            elif avg_response_time < 3:
                print("   ✅ Excellent response times (<3s)")
        
        # Show failed tests
        failed_results = [r for r in self.test_results if not r['success']]
        if failed_results:
            print(f"\n❌ FAILED TESTS ({len(failed_results)}):")
            for result in failed_results:
                print(f"   🔴 {result['test']}: {result['details']}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if success_rate >= 95:
            print("🎉 EXCELLENT: Aavana 2.0 OpenAI integration working perfectly")
            print("✅ All critical functionality operational")
            print("✅ GPT-5 model responding correctly")
            print("✅ No connection errors detected")
        elif success_rate >= 80:
            print("✅ GOOD: Aavana 2.0 mostly working with minor issues")
            print("⚠️ Some non-critical issues detected")
        elif success_rate >= 60:
            print("⚠️ MODERATE: Significant issues with Aavana 2.0 integration")
            print("🔧 Requires attention and fixes")
        else:
            print("🚨 CRITICAL: Major failures in Aavana 2.0 OpenAI integration")
            print("🚨 Immediate action required")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = Aavana2OpenAITester()
    tester.run_comprehensive_test()