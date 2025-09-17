#!/usr/bin/env python3
"""
Aavana 2.0 AI Chat Integration Test
Tests the new AI chat endpoints with emergentintegrations library
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://green-crm-suite.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"
EMERGENT_LLM_KEY = os.getenv('EMERGENT_LLM_KEY')

class Aavana2ChatTester:
    def __init__(self):
        self.session = None
        self.test_session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
    
    async def setup_session(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name, success, details, response_data=None):
        """Log test results"""
        self.results['total_tests'] += 1
        if success:
            self.results['passed_tests'] += 1
            status = "✅ PASS"
        else:
            self.results['failed_tests'] += 1
            status = "❌ FAIL"
        
        test_result = {
            'test_name': test_name,
            'status': status,
            'success': success,
            'details': details,
            'response_data': response_data
        }
        self.results['test_details'].append(test_result)
        print(f"{status}: {test_name} - {details}")
    
    async def test_backend_health(self):
        """Test backend health and basic connectivity"""
        try:
            async with self.session.get(f"{API_BASE}/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test(
                        "Backend Health Check",
                        True,
                        f"Backend responding correctly (200 OK): {data.get('message', 'No message')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Backend Health Check",
                        False,
                        f"Backend health check failed with status {response.status}"
                    )
                    return False
        except Exception as e:
            self.log_test(
                "Backend Health Check",
                False,
                f"Backend connection failed: {str(e)}"
            )
            return False
    
    async def test_emergent_llm_key_configuration(self):
        """Test if EMERGENT_LLM_KEY is properly configured"""
        if EMERGENT_LLM_KEY and EMERGENT_LLM_KEY.startswith('sk-emergent-'):
            self.log_test(
                "EMERGENT_LLM_KEY Configuration",
                True,
                f"LLM key properly configured: {EMERGENT_LLM_KEY[:20]}..."
            )
            return True
        else:
            self.log_test(
                "EMERGENT_LLM_KEY Configuration",
                False,
                f"LLM key not properly configured: {EMERGENT_LLM_KEY}"
            )
            return False
    
    async def test_aavana2_chat_endpoint_basic(self):
        """Test basic Aavana 2.0 chat functionality"""
        test_payload = {
            "message": "Hello, I need help with lead management",
            "session_id": self.test_session_id,
            "language": "en",
            "model": "gpt-4o",
            "provider": "openai"
        }
        
        try:
            async with self.session.post(
                f"{API_BASE}/aavana2/chat",
                json=test_payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ['message', 'message_id', 'session_id', 'timestamp', 'actions']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_test(
                            "Aavana 2.0 Chat - Basic Request",
                            True,
                            f"Chat endpoint working correctly. Response length: {len(data['message'])} chars, Actions: {len(data['actions'])}",
                            data
                        )
                        return True
                    else:
                        self.log_test(
                            "Aavana 2.0 Chat - Basic Request",
                            False,
                            f"Response missing required fields: {missing_fields}",
                            data
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Aavana 2.0 Chat - Basic Request",
                        False,
                        f"Chat endpoint failed with status {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Aavana 2.0 Chat - Basic Request",
                False,
                f"Chat request failed with exception: {str(e)}"
            )
            return False
    
    async def test_aavana2_chat_different_models(self):
        """Test Aavana 2.0 chat with different AI models"""
        models_to_test = [
            {"provider": "openai", "model": "gpt-4o", "name": "GPT-4o"},
            {"provider": "anthropic", "model": "claude-3-7-sonnet-20250219", "name": "Claude Sonnet 4"},
            {"provider": "gemini", "model": "gemini-2.0-flash", "name": "Gemini 2.5 Pro"}
        ]
        
        success_count = 0
        
        for model_config in models_to_test:
            test_payload = {
                "message": f"Test message for {model_config['name']} - help me with CRM tasks",
                "session_id": f"{self.test_session_id}_{model_config['provider']}",
                "language": "en",
                "model": model_config["model"],
                "provider": model_config["provider"]
            }
            
            try:
                async with self.session.post(
                    f"{API_BASE}/aavana2/chat",
                    json=test_payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        self.log_test(
                            f"Aavana 2.0 Chat - {model_config['name']}",
                            True,
                            f"Model {model_config['name']} working correctly. Response: {len(data['message'])} chars"
                        )
                        success_count += 1
                    else:
                        error_text = await response.text()
                        self.log_test(
                            f"Aavana 2.0 Chat - {model_config['name']}",
                            False,
                            f"Model {model_config['name']} failed with status {response.status}: {error_text}"
                        )
                        
            except Exception as e:
                self.log_test(
                    f"Aavana 2.0 Chat - {model_config['name']}",
                    False,
                    f"Model {model_config['name']} failed with exception: {str(e)}"
                )
        
        return success_count > 0
    
    async def test_aavana2_chat_different_message_types(self):
        """Test different types of CRM-related messages"""
        test_messages = [
            {
                "message": "How do I create a new lead in the system?",
                "type": "CRM Training"
            },
            {
                "message": "I need help managing my sales pipeline and tracking deals",
                "type": "Sales Management"
            },
            {
                "message": "Can you help me set up automated follow-up tasks?",
                "type": "Task Management"
            },
            {
                "message": "मुझे लीड मैनेजमेंट में मदद चाहिए",
                "type": "Hindi Language Support"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_messages):
            test_payload = {
                "message": test_case["message"],
                "session_id": f"{self.test_session_id}_type_{i}",
                "language": "hi" if "Hindi" in test_case["type"] else "en",
                "model": "gpt-4o",
                "provider": "openai"
            }
            
            try:
                async with self.session.post(
                    f"{API_BASE}/aavana2/chat",
                    json=test_payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        self.log_test(
                            f"Aavana 2.0 Chat - {test_case['type']}",
                            True,
                            f"Message type '{test_case['type']}' processed correctly. Response: {len(data['message'])} chars, Actions: {len(data['actions'])}"
                        )
                        success_count += 1
                    else:
                        error_text = await response.text()
                        self.log_test(
                            f"Aavana 2.0 Chat - {test_case['type']}",
                            False,
                            f"Message type '{test_case['type']}' failed with status {response.status}: {error_text}"
                        )
                        
            except Exception as e:
                self.log_test(
                    f"Aavana 2.0 Chat - {test_case['type']}",
                    False,
                    f"Message type '{test_case['type']}' failed with exception: {str(e)}"
                )
        
        return success_count > 0
    
    async def test_chat_history_endpoint(self):
        """Test chat history retrieval endpoint"""
        # First, send a few messages to create history
        messages_to_send = [
            "Hello, this is message 1",
            "This is message 2 for history testing",
            "Final message 3 for history test"
        ]
        
        history_session_id = f"{self.test_session_id}_history"
        
        # Send messages to create history
        for i, message in enumerate(messages_to_send):
            test_payload = {
                "message": message,
                "session_id": history_session_id,
                "language": "en",
                "model": "gpt-4o",
                "provider": "openai"
            }
            
            try:
                async with self.session.post(
                    f"{API_BASE}/aavana2/chat",
                    json=test_payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status != 200:
                        self.log_test(
                            "Chat History Setup",
                            False,
                            f"Failed to send message {i+1} for history test"
                        )
                        return False
            except Exception as e:
                self.log_test(
                    "Chat History Setup",
                    False,
                    f"Exception sending message {i+1} for history test: {str(e)}"
                )
                return False
        
        # Wait a moment for messages to be saved
        await asyncio.sleep(2)
        
        # Now test history retrieval
        try:
            async with self.session.get(
                f"{API_BASE}/aavana2/chat/history/{history_session_id}?limit=10"
            ) as response:
                
                if response.status == 200:
                    history_data = await response.json()
                    
                    if isinstance(history_data, list) and len(history_data) >= 6:  # 3 user + 3 assistant messages
                        self.log_test(
                            "Aavana 2.0 Chat History",
                            True,
                            f"Chat history retrieved successfully. Found {len(history_data)} messages in session {history_session_id}",
                            {"message_count": len(history_data), "session_id": history_session_id}
                        )
                        return True
                    else:
                        self.log_test(
                            "Aavana 2.0 Chat History",
                            False,
                            f"Chat history incomplete. Expected at least 6 messages, got {len(history_data) if isinstance(history_data, list) else 0}",
                            history_data
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Aavana 2.0 Chat History",
                        False,
                        f"Chat history endpoint failed with status {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Aavana 2.0 Chat History",
                False,
                f"Chat history request failed with exception: {str(e)}"
            )
            return False
    
    async def test_database_storage(self):
        """Test that chat messages are properly stored in database"""
        test_session_id = f"{self.test_session_id}_db_test"
        test_message = "This is a database storage test message"
        
        # Send a message
        test_payload = {
            "message": test_message,
            "session_id": test_session_id,
            "language": "en",
            "model": "gpt-4o",
            "provider": "openai"
        }
        
        try:
            # Send message
            async with self.session.post(
                f"{API_BASE}/aavana2/chat",
                json=test_payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status != 200:
                    self.log_test(
                        "Database Storage Test",
                        False,
                        f"Failed to send test message for database storage test"
                    )
                    return False
            
            # Wait for database write
            await asyncio.sleep(2)
            
            # Retrieve history to verify storage
            async with self.session.get(
                f"{API_BASE}/aavana2/chat/history/{test_session_id}"
            ) as response:
                
                if response.status == 200:
                    history_data = await response.json()
                    
                    # Check if our test message is in the history
                    user_messages = [msg for msg in history_data if msg.get('role') == 'user']
                    test_message_found = any(test_message in msg.get('content', '') for msg in user_messages)
                    
                    if test_message_found:
                        self.log_test(
                            "Database Storage Verification",
                            True,
                            f"Chat messages properly stored and retrieved from database. Found test message in {len(history_data)} total messages"
                        )
                        return True
                    else:
                        self.log_test(
                            "Database Storage Verification",
                            False,
                            f"Test message not found in database. Retrieved {len(history_data)} messages but test message missing"
                        )
                        return False
                else:
                    self.log_test(
                        "Database Storage Verification",
                        False,
                        f"Failed to retrieve history for database verification"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Database Storage Verification",
                False,
                f"Database storage test failed with exception: {str(e)}"
            )
            return False
    
    async def test_response_structure_validation(self):
        """Test that responses have proper structure and required fields"""
        test_payload = {
            "message": "Test response structure validation",
            "session_id": f"{self.test_session_id}_structure",
            "language": "en",
            "model": "gpt-4o",
            "provider": "openai"
        }
        
        try:
            async with self.session.post(
                f"{API_BASE}/aavana2/chat",
                json=test_payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    validation_results = []
                    
                    # Check required fields
                    required_fields = {
                        'message': str,
                        'message_id': str,
                        'session_id': str,
                        'timestamp': str,
                        'actions': list
                    }
                    
                    for field, expected_type in required_fields.items():
                        if field in data:
                            if isinstance(data[field], expected_type):
                                validation_results.append(f"✅ {field}: {expected_type.__name__}")
                            else:
                                validation_results.append(f"❌ {field}: expected {expected_type.__name__}, got {type(data[field]).__name__}")
                        else:
                            validation_results.append(f"❌ {field}: missing")
                    
                    # Check if session_id matches
                    if data.get('session_id') == test_payload['session_id']:
                        validation_results.append("✅ session_id matches request")
                    else:
                        validation_results.append("❌ session_id doesn't match request")
                    
                    # Check if message is not empty
                    if data.get('message') and len(data['message'].strip()) > 0:
                        validation_results.append("✅ message content is not empty")
                    else:
                        validation_results.append("❌ message content is empty")
                    
                    # Check if timestamp is valid
                    try:
                        datetime.fromisoformat(data.get('timestamp', '').replace('Z', '+00:00'))
                        validation_results.append("✅ timestamp is valid ISO format")
                    except:
                        validation_results.append("❌ timestamp is not valid ISO format")
                    
                    all_valid = all('✅' in result for result in validation_results)
                    
                    self.log_test(
                        "Response Structure Validation",
                        all_valid,
                        f"Response structure validation: {'; '.join(validation_results)}",
                        data
                    )
                    return all_valid
                else:
                    self.log_test(
                        "Response Structure Validation",
                        False,
                        f"Failed to get response for structure validation (status {response.status})"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Response Structure Validation",
                False,
                f"Response structure validation failed with exception: {str(e)}"
            )
            return False
    
    async def run_all_tests(self):
        """Run all Aavana 2.0 AI Chat Integration tests"""
        print("🚀 Starting Aavana 2.0 AI Chat Integration Tests")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print(f"🔑 LLM Key: {EMERGENT_LLM_KEY[:20]}..." if EMERGENT_LLM_KEY else "❌ No LLM Key")
        print(f"🆔 Test Session ID: {self.test_session_id}")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Run all tests
            await self.test_backend_health()
            await self.test_emergent_llm_key_configuration()
            await self.test_aavana2_chat_endpoint_basic()
            await self.test_aavana2_chat_different_models()
            await self.test_aavana2_chat_different_message_types()
            await self.test_chat_history_endpoint()
            await self.test_database_storage()
            await self.test_response_structure_validation()
            
        finally:
            await self.cleanup_session()
        
        # Print summary
        print("=" * 80)
        print("📊 AAVANA 2.0 AI CHAT INTEGRATION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed_tests']}")
        print(f"❌ Failed: {self.results['failed_tests']}")
        print(f"Success Rate: {(self.results['passed_tests']/self.results['total_tests']*100):.1f}%")
        
        if self.results['failed_tests'] > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.results['test_details']:
                if not test['success']:
                    print(f"  • {test['test_name']}: {test['details']}")
        
        print("\n✅ SUCCESSFUL TESTS:")
        for test in self.results['test_details']:
            if test['success']:
                print(f"  • {test['test_name']}: {test['details']}")
        
        return self.results

async def main():
    """Main test execution"""
    tester = Aavana2ChatTester()
    results = await tester.run_all_tests()
    
    # Return appropriate exit code
    if results['failed_tests'] == 0:
        print("\n🎉 ALL TESTS PASSED! Aavana 2.0 AI Chat Integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {results['failed_tests']} TESTS FAILED. Please check the issues above.")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)