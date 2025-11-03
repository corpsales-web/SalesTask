#!/usr/bin/env python3
"""
WhatsApp Backend Smoke Test Suite
Tests specific WhatsApp endpoints as requested in review:
1) POST /api/whatsapp/webhook with demo payload creates conversation
2) GET /api/whatsapp/conversations returns array with age_sec, unread_count  
3) POST /api/whatsapp/send and /api/whatsapp/send_media update last_message and messages collection
4) GET /api/whatsapp/session_status
5) POST /api/whatsapp/conversations/{contact}/read
Ensure no 500s occur.
"""

import requests
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

# Configuration - Use production URL from frontend .env
BASE_URL = "https://crm-visual-studio.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class WhatsAppSmokeTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.test_contact = f"+91{int(time.time()) % 10000000000}"  # Generate unique contact
        
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
    
    def test_webhook_creates_conversation(self):
        """Test POST /api/whatsapp/webhook with demo payload creates conversation"""
        try:
            # Create demo webhook payload similar to WhatsApp Business API format
            webhook_payload = {
                "entry": [{
                    "id": "business_account_id",
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550199999",
                                "phone_number_id": "123456789"
                            },
                            "messages": [{
                                "from": self.test_contact.replace("+", ""),
                                "id": f"wamid.{uuid.uuid4()}",
                                "timestamp": str(int(time.time())),
                                "text": {
                                    "body": "Hello from smoke test! 👋"
                                },
                                "type": "text"
                            }]
                        },
                        "field": "messages"
                    }]
                }]
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/webhook",
                json=webhook_payload,
                timeout=10
            )
            
            # Check for no 500 errors
            if response.status_code >= 500:
                self.log_test("Webhook Creates Conversation", False, 
                            f"Server error {response.status_code}", response.text)
                return False
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Webhook Creates Conversation", True, 
                                f"Webhook processed successfully for contact {self.test_contact}")
                    return True
                else:
                    self.log_test("Webhook Creates Conversation", False, 
                                "Webhook response missing success flag", data)
            else:
                self.log_test("Webhook Creates Conversation", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Webhook Creates Conversation", False, f"Error: {str(e)}")
        return False
    
    def test_conversations_list_format(self):
        """Test GET /api/whatsapp/conversations returns array with age_sec, unread_count"""
        try:
            response = self.session.get(f"{API_BASE}/whatsapp/conversations", timeout=10)
            
            # Check for no 500 errors
            if response.status_code >= 500:
                self.log_test("Conversations List Format", False, 
                            f"Server error {response.status_code}", response.text)
                return False
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if our test contact conversation exists
                    test_conversation = None
                    for conv in data:
                        if conv.get("contact") == self.test_contact:
                            test_conversation = conv
                            break
                    
                    if test_conversation:
                        # Verify required fields
                        required_fields = ["age_sec", "unread_count"]
                        missing_fields = [field for field in required_fields 
                                        if field not in test_conversation]
                        
                        if not missing_fields:
                            # Verify field types
                            age_sec = test_conversation.get("age_sec")
                            unread_count = test_conversation.get("unread_count")
                            
                            if (isinstance(age_sec, (int, type(None))) and 
                                isinstance(unread_count, int)):
                                self.log_test("Conversations List Format", True, 
                                            f"Found conversation with correct format: age_sec={age_sec}, unread_count={unread_count}")
                                return True
                            else:
                                self.log_test("Conversations List Format", False, 
                                            f"Invalid field types: age_sec={type(age_sec)}, unread_count={type(unread_count)}")
                        else:
                            self.log_test("Conversations List Format", False, 
                                        f"Missing required fields: {missing_fields}")
                    else:
                        # Still check general format even if our test conversation isn't found
                        if data:  # If there are any conversations
                            sample_conv = data[0]
                            has_age_sec = "age_sec" in sample_conv
                            has_unread_count = "unread_count" in sample_conv
                            
                            if has_age_sec and has_unread_count:
                                self.log_test("Conversations List Format", True, 
                                            f"Conversations have correct format (checked {len(data)} items)")
                                return True
                            else:
                                missing = []
                                if not has_age_sec: missing.append("age_sec")
                                if not has_unread_count: missing.append("unread_count")
                                self.log_test("Conversations List Format", False, 
                                            f"Sample conversation missing: {missing}")
                        else:
                            self.log_test("Conversations List Format", True, 
                                        "Empty conversations list (valid format)")
                            return True
                else:
                    self.log_test("Conversations List Format", False, 
                                "Response is not an array", data)
            else:
                self.log_test("Conversations List Format", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Conversations List Format", False, f"Error: {str(e)}")
        return False
    
    def test_send_message_updates_conversation(self):
        """Test POST /api/whatsapp/send updates last_message and messages collection"""
        try:
            send_payload = {
                "to": self.test_contact,
                "text": "Test outbound message from smoke test"
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/send",
                json=send_payload,
                timeout=10
            )
            
            # Check for no 500 errors
            if response.status_code >= 500:
                self.log_test("Send Message Updates", False, 
                            f"Server error {response.status_code}", response.text)
                return False
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Verify conversation was updated by checking conversations list
                    time.sleep(0.5)  # Brief delay for DB update
                    conv_response = self.session.get(f"{API_BASE}/whatsapp/conversations", timeout=10)
                    
                    if conv_response.status_code == 200:
                        conversations = conv_response.json()
                        test_conv = None
                        for conv in conversations:
                            if conv.get("contact") == self.test_contact:
                                test_conv = conv
                                break
                        
                        if test_conv:
                            # Check if last_message was updated
                            last_message_text = test_conv.get("last_message_text", "")
                            last_message_dir = test_conv.get("last_message_dir", "")
                            
                            if ("Test outbound message" in last_message_text and 
                                last_message_dir == "out"):
                                self.log_test("Send Message Updates", True, 
                                            "Send message correctly updated conversation")
                                return True
                            else:
                                self.log_test("Send Message Updates", False, 
                                            f"Conversation not updated correctly: text='{last_message_text}', dir='{last_message_dir}'")
                        else:
                            self.log_test("Send Message Updates", False, 
                                        "Test conversation not found after send")
                    else:
                        self.log_test("Send Message Updates", False, 
                                    "Could not verify conversation update")
                else:
                    self.log_test("Send Message Updates", False, 
                                "Send response missing success flag", data)
            else:
                self.log_test("Send Message Updates", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Send Message Updates", False, f"Error: {str(e)}")
        return False
    
    def test_send_media_updates_conversation(self):
        """Test POST /api/whatsapp/send_media updates last_message and messages collection"""
        try:
            media_payload = {
                "to": self.test_contact,
                "media_url": "https://example.com/test-image.jpg",
                "media_type": "image"
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/send_media",
                json=media_payload,
                timeout=10
            )
            
            # Check for no 500 errors
            if response.status_code >= 500:
                self.log_test("Send Media Updates", False, 
                            f"Server error {response.status_code}", response.text)
                return False
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Verify conversation was updated
                    time.sleep(0.5)  # Brief delay for DB update
                    conv_response = self.session.get(f"{API_BASE}/whatsapp/conversations", timeout=10)
                    
                    if conv_response.status_code == 200:
                        conversations = conv_response.json()
                        test_conv = None
                        for conv in conversations:
                            if conv.get("contact") == self.test_contact:
                                test_conv = conv
                                break
                        
                        if test_conv:
                            # Check if last_message was updated with media info
                            last_message_text = test_conv.get("last_message_text", "")
                            last_message_dir = test_conv.get("last_message_dir", "")
                            
                            if ("image:" in last_message_text and 
                                "example.com/test-image.jpg" in last_message_text and
                                last_message_dir == "out"):
                                self.log_test("Send Media Updates", True, 
                                            "Send media correctly updated conversation")
                                return True
                            else:
                                self.log_test("Send Media Updates", False, 
                                            f"Media conversation not updated correctly: text='{last_message_text}', dir='{last_message_dir}'")
                        else:
                            self.log_test("Send Media Updates", False, 
                                        "Test conversation not found after media send")
                    else:
                        self.log_test("Send Media Updates", False, 
                                    "Could not verify media conversation update")
                else:
                    self.log_test("Send Media Updates", False, 
                                "Send media response missing success flag", data)
            else:
                self.log_test("Send Media Updates", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Send Media Updates", False, f"Error: {str(e)}")
        return False
    
    def test_session_status(self):
        """Test GET /api/whatsapp/session_status"""
        try:
            response = self.session.get(
                f"{API_BASE}/whatsapp/session_status?contact={self.test_contact}",
                timeout=10
            )
            
            # Check for no 500 errors
            if response.status_code >= 500:
                self.log_test("Session Status", False, 
                            f"Server error {response.status_code}", response.text)
                return False
            
            if response.status_code == 200:
                data = response.json()
                # Check for expected format (should have within_24h field)
                if "within_24h" in data:
                    within_24h = data.get("within_24h")
                    if isinstance(within_24h, bool):
                        self.log_test("Session Status", True, 
                                    f"Session status returned: within_24h={within_24h}")
                        return True
                    else:
                        self.log_test("Session Status", False, 
                                    f"within_24h field is not boolean: {type(within_24h)}")
                else:
                    self.log_test("Session Status", False, 
                                "Response missing within_24h field", data)
            else:
                self.log_test("Session Status", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Session Status", False, f"Error: {str(e)}")
        return False
    
    def test_mark_conversation_read(self):
        """Test POST /api/whatsapp/conversations/{contact}/read"""
        try:
            response = self.session.post(
                f"{API_BASE}/whatsapp/conversations/{self.test_contact}/read",
                json={},
                timeout=10
            )
            
            # Check for no 500 errors
            if response.status_code >= 500:
                self.log_test("Mark Conversation Read", False, 
                            f"Server error {response.status_code}", response.text)
                return False
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Mark Conversation Read", True, 
                                "Successfully marked conversation as read")
                    return True
                else:
                    self.log_test("Mark Conversation Read", False, 
                                "Response missing success flag", data)
            else:
                self.log_test("Mark Conversation Read", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Mark Conversation Read", False, f"Error: {str(e)}")
        return False
    
    def run_smoke_tests(self):
        """Run all WhatsApp smoke tests in sequence"""
        print("🚀 Starting WhatsApp Backend Smoke Test Suite")
        print("=" * 60)
        print(f"🎯 Testing with contact: {self.test_contact}")
        print("=" * 60)
        
        # Test 1: Webhook creates conversation
        print("\n1️⃣ Testing Webhook Creates Conversation...")
        self.test_webhook_creates_conversation()
        
        # Test 2: Conversations list format
        print("\n2️⃣ Testing Conversations List Format...")
        self.test_conversations_list_format()
        
        # Test 3: Send message updates
        print("\n3️⃣ Testing Send Message Updates...")
        self.test_send_message_updates_conversation()
        
        # Test 4: Send media updates
        print("\n4️⃣ Testing Send Media Updates...")
        self.test_send_media_updates_conversation()
        
        # Test 5: Session status
        print("\n5️⃣ Testing Session Status...")
        self.test_session_status()
        
        # Test 6: Mark conversation read
        print("\n6️⃣ Testing Mark Conversation Read...")
        self.test_mark_conversation_read()
        
        # Summary
        self.print_summary()
        
        return self.get_overall_success()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 WHATSAPP SMOKE TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Check for any 500 errors
        server_errors = [result for result in self.test_results 
                        if not result["success"] and "Server error 5" in result["details"]]
        if server_errors:
            print(f"\n⚠️  CRITICAL: Found {len(server_errors)} server errors (500s)!")
            for error in server_errors:
                print(f"  • {error['test']}: {error['details']}")
        else:
            print("\n✅ NO 500 ERRORS DETECTED")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
    
    def get_overall_success(self):
        """Get overall test success status"""
        if not self.test_results:
            return False
        
        # Check for any 500 errors (critical failure)
        has_500_errors = any(
            not result["success"] and "Server error 5" in result["details"]
            for result in self.test_results
        )
        
        if has_500_errors:
            return False
        
        # All tests should pass for smoke test
        all_passed = all(result["success"] for result in self.test_results)
        return all_passed

def main():
    """Main test execution"""
    tester = WhatsAppSmokeTest()
    success = tester.run_smoke_tests()
    
    if success:
        print("\n✅ WhatsApp backend smoke tests completed successfully!")
        print("🎯 All endpoints working, no 500 errors detected")
        exit(0)
    else:
        print("\n❌ WhatsApp backend smoke tests had failures!")
        exit(1)

if __name__ == "__main__":
    main()