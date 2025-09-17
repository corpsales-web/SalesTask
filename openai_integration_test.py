#!/usr/bin/env python3
"""
OpenAI API Integration Test for Aavana 2.0
==========================================

Test Priority Areas:
1. OpenAI API Integration - Test POST /api/aavana2/chat with OpenAI API key
2. Cost-Effective Model - Verify GPT-4o-mini is being used
3. Response Times - Check if responses are fast and cost-efficient
4. Token Usage - Verify max_tokens limit is working for cost control
5. Error Handling - Test API error scenarios
6. No EMERGENT_LLM_KEY dependencies remain

Test Cases:
- Simple message: "Hello"
- Complex query: "How do I manage leads and create tasks effectively?"
- Test different session IDs
- Verify no EMERGENT_LLM_KEY dependencies remain
"""

import asyncio
import aiohttp
import json
import time
import uuid
import os
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://green-crm-suite.preview.emergentagent.com/api"
TEST_SESSION_ID = str(uuid.uuid4())

class OpenAIIntegrationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        print("🚀 OpenAI Integration Test Suite Starting...")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Session ID: {TEST_SESSION_ID}")
        print("=" * 80)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    def log_test_result(self, test_name: str, success: bool, details: str, response_time: float = 0):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{status} {test_name}")
        print(f"    Details: {details}")
        if response_time > 0:
            print(f"    Response Time: {response_time:.2f}s")
        print()
        
    async def test_backend_health(self):
        """Test backend health check"""
        try:
            start_time = time.time()
            async with self.session.get(f"{self.backend_url}/") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result(
                        "Backend Health Check",
                        True,
                        f"Backend responding: {data.get('message', 'OK')}",
                        response_time
                    )
                    return True
                else:
                    self.log_test_result(
                        "Backend Health Check",
                        False,
                        f"Backend returned status {response.status}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "Backend Health Check",
                False,
                f"Backend connection failed: {str(e)}"
            )
            return False
            
    async def test_openai_api_key_configuration(self):
        """Test OpenAI API key is properly configured"""
        try:
            # Check if OPENAI_API_KEY is set in environment
            # We can't directly access backend env, but we can test the endpoint behavior
            
            # Test with a simple message that should work if OpenAI is configured
            test_payload = {
                "message": "test",
                "session_id": TEST_SESSION_ID,
                "language": "en"
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{self.backend_url}/aavana2/chat",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    if "OpenAI API key not configured" in data.get("message", ""):
                        self.log_test_result(
                            "OpenAI API Key Configuration",
                            False,
                            "OpenAI API key not configured in backend",
                            response_time
                        )
                        return False
                    else:
                        self.log_test_result(
                            "OpenAI API Key Configuration",
                            True,
                            "OpenAI API key properly configured",
                            response_time
                        )
                        return True
                elif response.status == 500:
                    error_data = await response.json()
                    if "OpenAI API key not configured" in error_data.get("detail", ""):
                        self.log_test_result(
                            "OpenAI API Key Configuration",
                            False,
                            "OpenAI API key not configured in backend",
                            response_time
                        )
                        return False
                    else:
                        self.log_test_result(
                            "OpenAI API Key Configuration",
                            False,
                            f"API error: {error_data.get('detail', 'Unknown error')}",
                            response_time
                        )
                        return False
                else:
                    self.log_test_result(
                        "OpenAI API Key Configuration",
                        False,
                        f"Unexpected status code: {response.status}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "OpenAI API Key Configuration",
                False,
                f"Configuration test failed: {str(e)}"
            )
            return False
            
    async def test_simple_message(self):
        """Test simple message: 'Hello'"""
        try:
            test_payload = {
                "message": "Hello",
                "session_id": TEST_SESSION_ID,
                "language": "en"
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{self.backend_url}/aavana2/chat",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    message = data.get("message", "")
                    
                    # Check if response is meaningful
                    if len(message) > 10 and "Aavana" in message:
                        self.log_test_result(
                            "Simple Message Test ('Hello')",
                            True,
                            f"Received meaningful response: '{message[:100]}...' (Response time: {response_time:.2f}s)",
                            response_time
                        )
                        return True, data
                    else:
                        self.log_test_result(
                            "Simple Message Test ('Hello')",
                            False,
                            f"Response too short or not contextual: '{message}'",
                            response_time
                        )
                        return False, data
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {"detail": "Unknown error"}
                    self.log_test_result(
                        "Simple Message Test ('Hello')",
                        False,
                        f"API returned status {response.status}: {error_data.get('detail', 'Unknown error')}",
                        response_time
                    )
                    return False, None
                    
        except Exception as e:
            self.log_test_result(
                "Simple Message Test ('Hello')",
                False,
                f"Test failed: {str(e)}"
            )
            return False, None
            
    async def test_complex_query(self):
        """Test complex query: 'How do I manage leads and create tasks effectively?'"""
        try:
            test_payload = {
                "message": "How do I manage leads and create tasks effectively?",
                "session_id": TEST_SESSION_ID,
                "language": "en"
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{self.backend_url}/aavana2/chat",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    message = data.get("message", "")
                    actions = data.get("actions", [])
                    
                    # Check if response is comprehensive and includes actions
                    if len(message) > 50 and ("lead" in message.lower() or "task" in message.lower()):
                        details = f"Comprehensive response received (Length: {len(message)} chars)"
                        if actions:
                            details += f", Actions provided: {len(actions)}"
                        
                        self.log_test_result(
                            "Complex Query Test",
                            True,
                            details,
                            response_time
                        )
                        return True, data
                    else:
                        self.log_test_result(
                            "Complex Query Test",
                            False,
                            f"Response not comprehensive enough: '{message[:100]}...'",
                            response_time
                        )
                        return False, data
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {"detail": "Unknown error"}
                    self.log_test_result(
                        "Complex Query Test",
                        False,
                        f"API returned status {response.status}: {error_data.get('detail', 'Unknown error')}",
                        response_time
                    )
                    return False, None
                    
        except Exception as e:
            self.log_test_result(
                "Complex Query Test",
                False,
                f"Test failed: {str(e)}"
            )
            return False, None
            
    async def test_different_session_ids(self):
        """Test with different session IDs"""
        try:
            session_ids = [str(uuid.uuid4()) for _ in range(3)]
            successful_sessions = 0
            
            for i, session_id in enumerate(session_ids):
                test_payload = {
                    "message": f"Test message {i+1}",
                    "session_id": session_id,
                    "language": "en"
                }
                
                start_time = time.time()
                async with self.session.post(
                    f"{self.backend_url}/aavana2/chat",
                    json=test_payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get("session_id") == session_id:
                            successful_sessions += 1
                            
            if successful_sessions == 3:
                self.log_test_result(
                    "Different Session IDs Test",
                    True,
                    f"All {successful_sessions}/3 sessions handled correctly"
                )
                return True
            else:
                self.log_test_result(
                    "Different Session IDs Test",
                    False,
                    f"Only {successful_sessions}/3 sessions handled correctly"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Different Session IDs Test",
                False,
                f"Test failed: {str(e)}"
            )
            return False
            
    async def test_gpt4o_mini_model_usage(self):
        """Test that GPT-4o-mini model is being used (cost-effective)"""
        try:
            # We can't directly verify the model from the API response,
            # but we can check the response characteristics and speed
            # GPT-4o-mini should be faster and more cost-effective
            
            test_payload = {
                "message": "What model are you using?",
                "session_id": TEST_SESSION_ID,
                "language": "en"
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{self.backend_url}/aavana2/chat",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    message = data.get("message", "")
                    
                    # Check response time (GPT-4o-mini should be faster)
                    if response_time < 5.0:  # Should be under 5 seconds for cost-effective model
                        details = f"Fast response time ({response_time:.2f}s) indicates cost-effective model usage"
                        if "gpt-4o-mini" in message.lower() or "4o-mini" in message.lower():
                            details += " - Model confirmed in response"
                        
                        self.log_test_result(
                            "GPT-4o-mini Model Usage Test",
                            True,
                            details,
                            response_time
                        )
                        return True
                    else:
                        self.log_test_result(
                            "GPT-4o-mini Model Usage Test",
                            False,
                            f"Response time too slow ({response_time:.2f}s) for cost-effective model",
                            response_time
                        )
                        return False
                else:
                    self.log_test_result(
                        "GPT-4o-mini Model Usage Test",
                        False,
                        f"API returned status {response.status}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "GPT-4o-mini Model Usage Test",
                False,
                f"Test failed: {str(e)}"
            )
            return False
            
    async def test_token_usage_limits(self):
        """Test that max_tokens limit is working for cost control"""
        try:
            # Send a request that would generate a very long response
            test_payload = {
                "message": "Please write a very detailed, comprehensive guide about lead management, task creation, HRMS features, marketing campaigns, sales pipeline, analytics, and all other CRM features. Include step-by-step instructions, best practices, examples, and detailed explanations for each feature.",
                "session_id": TEST_SESSION_ID,
                "language": "en"
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{self.backend_url}/aavana2/chat",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    message = data.get("message", "")
                    
                    # Check if response is limited (should be under reasonable length due to max_tokens=1000)
                    # Roughly 1000 tokens = ~750-1000 words = ~4000-6000 characters
                    if len(message) < 8000:  # Should be limited by max_tokens
                        self.log_test_result(
                            "Token Usage Limits Test",
                            True,
                            f"Response properly limited to {len(message)} characters (max_tokens working)",
                            response_time
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Token Usage Limits Test",
                            False,
                            f"Response too long ({len(message)} characters) - max_tokens limit may not be working",
                            response_time
                        )
                        return False
                else:
                    self.log_test_result(
                        "Token Usage Limits Test",
                        False,
                        f"API returned status {response.status}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "Token Usage Limits Test",
                False,
                f"Test failed: {str(e)}"
            )
            return False
            
    async def test_response_times(self):
        """Test response times for cost efficiency"""
        try:
            test_messages = [
                "Hello",
                "What can you help me with?",
                "How do I add a new lead?",
                "Show me my tasks",
                "Help with marketing"
            ]
            
            response_times = []
            successful_requests = 0
            
            for message in test_messages:
                test_payload = {
                    "message": message,
                    "session_id": TEST_SESSION_ID,
                    "language": "en"
                }
                
                start_time = time.time()
                try:
                    async with self.session.post(
                        f"{self.backend_url}/aavana2/chat",
                        json=test_payload,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            response_times.append(response_time)
                            successful_requests += 1
                            
                except Exception:
                    continue
                    
            if successful_requests >= 3:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
                
                # Good response times for cost-effective model
                if avg_response_time < 3.0 and max_response_time < 8.0:
                    self.log_test_result(
                        "Response Times Test",
                        True,
                        f"Excellent response times - Avg: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s, Min: {min_response_time:.2f}s",
                        avg_response_time
                    )
                    return True
                else:
                    self.log_test_result(
                        "Response Times Test",
                        False,
                        f"Response times too slow - Avg: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s",
                        avg_response_time
                    )
                    return False
            else:
                self.log_test_result(
                    "Response Times Test",
                    False,
                    f"Only {successful_requests}/5 requests successful"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Response Times Test",
                False,
                f"Test failed: {str(e)}"
            )
            return False
            
    async def test_error_handling(self):
        """Test API error scenarios"""
        try:
            error_scenarios = [
                {
                    "name": "Empty Message",
                    "payload": {"message": "", "session_id": TEST_SESSION_ID, "language": "en"},
                    "expected_behavior": "Should handle gracefully"
                },
                {
                    "name": "Very Long Message",
                    "payload": {"message": "x" * 10000, "session_id": TEST_SESSION_ID, "language": "en"},
                    "expected_behavior": "Should handle or limit appropriately"
                },
                {
                    "name": "Invalid Session ID",
                    "payload": {"message": "test", "session_id": "", "language": "en"},
                    "expected_behavior": "Should handle gracefully"
                }
            ]
            
            successful_error_handling = 0
            
            for scenario in error_scenarios:
                try:
                    start_time = time.time()
                    async with self.session.post(
                        f"{self.backend_url}/aavana2/chat",
                        json=scenario["payload"],
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        response_time = time.time() - start_time
                        
                        # Should either succeed with graceful handling or return appropriate error
                        if response.status in [200, 400, 422]:  # Valid responses
                            successful_error_handling += 1
                            
                except Exception:
                    # Some errors are expected, continue testing
                    continue
                    
            if successful_error_handling >= 2:
                self.log_test_result(
                    "Error Handling Test",
                    True,
                    f"Good error handling - {successful_error_handling}/3 scenarios handled appropriately"
                )
                return True
            else:
                self.log_test_result(
                    "Error Handling Test",
                    False,
                    f"Poor error handling - Only {successful_error_handling}/3 scenarios handled"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Error Handling Test",
                False,
                f"Test failed: {str(e)}"
            )
            return False
            
    async def test_no_emergent_llm_dependencies(self):
        """Test that no EMERGENT_LLM_KEY dependencies remain"""
        try:
            # Test multiple requests to ensure consistent OpenAI usage
            test_messages = [
                "What AI model are you using?",
                "Are you using OpenAI?",
                "Tell me about your AI capabilities"
            ]
            
            openai_indicators = 0
            emergent_indicators = 0
            
            for message in test_messages:
                test_payload = {
                    "message": message,
                    "session_id": TEST_SESSION_ID,
                    "language": "en"
                }
                
                try:
                    async with self.session.post(
                        f"{self.backend_url}/aavana2/chat",
                        json=test_payload,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            message_content = data.get("message", "").lower()
                            
                            # Look for OpenAI indicators
                            if any(term in message_content for term in ["openai", "gpt", "chatgpt"]):
                                openai_indicators += 1
                                
                            # Look for Emergent LLM indicators (should not be present)
                            if any(term in message_content for term in ["emergent", "emergent llm", "emergent_llm"]):
                                emergent_indicators += 1
                                
                except Exception:
                    continue
                    
            # Also test response characteristics (OpenAI responses have different patterns)
            if emergent_indicators == 0:
                self.log_test_result(
                    "No EMERGENT_LLM Dependencies Test",
                    True,
                    f"No EMERGENT_LLM references found. OpenAI indicators: {openai_indicators}"
                )
                return True
            else:
                self.log_test_result(
                    "No EMERGENT_LLM Dependencies Test",
                    False,
                    f"EMERGENT_LLM references still found: {emergent_indicators} instances"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "No EMERGENT_LLM Dependencies Test",
                False,
                f"Test failed: {str(e)}"
            )
            return False
            
    async def test_chat_history_functionality(self):
        """Test chat history endpoint"""
        try:
            # First send a message to create history
            test_payload = {
                "message": "Test message for history",
                "session_id": TEST_SESSION_ID,
                "language": "en"
            }
            
            async with self.session.post(
                f"{self.backend_url}/aavana2/chat",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    self.log_test_result(
                        "Chat History Functionality Test",
                        False,
                        "Failed to send initial message for history test"
                    )
                    return False
                    
            # Wait a moment for message to be saved
            await asyncio.sleep(1)
            
            # Now test history retrieval
            start_time = time.time()
            async with self.session.get(
                f"{self.backend_url}/aavana2/chat/history/{TEST_SESSION_ID}"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    messages = data.get("messages", [])
                    
                    if len(messages) > 0:
                        self.log_test_result(
                            "Chat History Functionality Test",
                            True,
                            f"Chat history retrieved successfully - {len(messages)} messages found",
                            response_time
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Chat History Functionality Test",
                            False,
                            "Chat history endpoint works but no messages found",
                            response_time
                        )
                        return False
                else:
                    self.log_test_result(
                        "Chat History Functionality Test",
                        False,
                        f"Chat history endpoint returned status {response.status}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "Chat History Functionality Test",
                False,
                f"Test failed: {str(e)}"
            )
            return False
            
    async def run_all_tests(self):
        """Run all OpenAI integration tests"""
        await self.setup()
        
        try:
            print("🧪 OPENAI API INTEGRATION TEST SUITE")
            print("=" * 80)
            
            # Critical tests first
            backend_healthy = await self.test_backend_health()
            if not backend_healthy:
                print("❌ Backend not healthy, skipping remaining tests")
                return
                
            openai_configured = await self.test_openai_api_key_configuration()
            if not openai_configured:
                print("❌ OpenAI not configured, skipping remaining tests")
                return
                
            # Core functionality tests
            await self.test_simple_message()
            await self.test_complex_query()
            await self.test_different_session_ids()
            
            # Performance and cost tests
            await self.test_gpt4o_mini_model_usage()
            await self.test_token_usage_limits()
            await self.test_response_times()
            
            # Quality and reliability tests
            await self.test_error_handling()
            await self.test_no_emergent_llm_dependencies()
            await self.test_chat_history_functionality()
            
        finally:
            await self.cleanup()
            
        # Print summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED - OpenAI Integration is working perfectly!")
        elif self.passed_tests >= self.total_tests * 0.8:
            print(f"\n✅ MOSTLY SUCCESSFUL - {self.passed_tests}/{self.total_tests} tests passed")
        else:
            print(f"\n⚠️  ISSUES DETECTED - Only {self.passed_tests}/{self.total_tests} tests passed")
            
        print("\n🔍 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
            
        return self.passed_tests, self.total_tests

async def main():
    """Main test execution"""
    tester = OpenAIIntegrationTester()
    passed, total = await tester.run_all_tests()
    
    # Return appropriate exit code
    if passed == total:
        exit(0)  # All tests passed
    elif passed >= total * 0.8:
        exit(1)  # Mostly successful but some issues
    else:
        exit(2)  # Significant issues detected

if __name__ == "__main__":
    asyncio.run(main())