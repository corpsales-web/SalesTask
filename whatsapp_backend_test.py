#!/usr/bin/env python3
"""
CRM Backend WhatsApp Endpoints Test Suite
Tests WhatsApp 360dialog integration endpoints in stub mode
"""

import requests
import json
import time
import uuid
import hmac
import hashlib
from typing import Dict, Any, List

# Configuration - Use production URL from frontend/.env
BASE_URL = "https://crm-whatsapp-hub-1.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class WhatsAppTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_messages = []  # Track created webhook messages
        
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
    
    def test_webhook_verification_no_token(self):
        """Test GET /api/whatsapp/webhook without verify token - expect 403"""
        try:
            params = {
                "hub.mode": "subscribe",
                "hub.verify_token": "test_token_123",
                "hub.challenge": "challenge_xyz"
            }
            
            response = self.session.get(f"{API_BASE}/whatsapp/webhook", params=params, timeout=10)
            
            if response.status_code == 403:
                self.log_test("Webhook Verification (No Token)", True, 
                            "Correctly returned 403 when WHATSAPP_VERIFY_TOKEN not set")
                return True
            else:
                self.log_test("Webhook Verification (No Token)", False, 
                            f"Expected 403 but got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Webhook Verification (No Token)", False, f"Connection error: {str(e)}")
        return False
    
    def test_webhook_verification_wrong_mode(self):
        """Test GET /api/whatsapp/webhook with wrong hub.mode - expect 403"""
        try:
            params = {
                "hub.mode": "unsubscribe",  # Wrong mode
                "hub.verify_token": "test_token_123",
                "hub.challenge": "challenge_xyz"
            }
            
            response = self.session.get(f"{API_BASE}/whatsapp/webhook", params=params, timeout=10)
            
            if response.status_code == 403:
                self.log_test("Webhook Verification (Wrong Mode)", True, 
                            "Correctly returned 403 for wrong hub.mode")
                return True
            else:
                self.log_test("Webhook Verification (Wrong Mode)", False, 
                            f"Expected 403 but got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Webhook Verification (Wrong Mode)", False, f"Connection error: {str(e)}")
        return False
    
    def test_webhook_receive_no_signature(self):
        """Test POST /api/whatsapp/webhook without signature - should pass if no WHATSAPP_WEBHOOK_SECRET"""
        try:
            # Sample 360dialog webhook payload
            payload = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "id": "123456789",
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15551234567",
                                "phone_number_id": "987654321"
                            },
                            "messages": [{
                                "from": "1234567890",
                                "id": "wamid.ABC123",
                                "timestamp": "1234567890",
                                "text": {
                                    "body": "Hello from WhatsApp!"
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
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") is True:
                    self.log_test("Webhook Receive (No Signature)", True, 
                                "Successfully received webhook without signature (no secret configured)")
                    return True
                else:
                    self.log_test("Webhook Receive (No Signature)", False, 
                                "Response missing success: true", data)
            else:
                self.log_test("Webhook Receive (No Signature)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Webhook Receive (No Signature)", False, f"Error: {str(e)}")
        return False
    
    def test_webhook_receive_with_signature(self):
        """Test POST /api/whatsapp/webhook with valid signature - should pass if no secret configured"""
        try:
            payload = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "id": "123456789",
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15551234567",
                                "phone_number_id": "987654321"
                            },
                            "messages": [{
                                "from": "9876543210",
                                "id": "wamid.XYZ789",
                                "timestamp": "1234567891",
                                "text": {
                                    "body": "Another test message"
                                },
                                "type": "text"
                            }]
                        },
                        "field": "messages"
                    }]
                }]
            }
            
            # Create a dummy signature (won't be validated if no secret)
            body_str = json.dumps(payload)
            dummy_signature = "sha256=dummy_signature_for_testing"
            
            headers = {
                "X-Hub-Signature-256": dummy_signature,
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/webhook",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") is True:
                    self.log_test("Webhook Receive (With Signature)", True, 
                                "Successfully received webhook with signature")
                    return True
                else:
                    self.log_test("Webhook Receive (With Signature)", False, 
                                "Response missing success: true", data)
            else:
                self.log_test("Webhook Receive (With Signature)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Webhook Receive (With Signature)", False, f"Error: {str(e)}")
        return False
    
    def test_webhook_receive_invalid_json(self):
        """Test POST /api/whatsapp/webhook with invalid JSON - expect 400"""
        try:
            response = self.session.post(
                f"{API_BASE}/whatsapp/webhook",
                data="invalid json content",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("Webhook Receive (Invalid JSON)", True, 
                            "Correctly returned 400 for invalid JSON")
                return True
            else:
                self.log_test("Webhook Receive (Invalid JSON)", False, 
                            f"Expected 400 but got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Webhook Receive (Invalid JSON)", False, f"Error: {str(e)}")
        return False
    
    def test_messages_list_empty(self):
        """Test GET /api/whatsapp/messages - should return array (empty or with stored messages)"""
        try:
            response = self.session.get(f"{API_BASE}/whatsapp/messages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Verify no _id fields in response
                    has_mongo_id = any("_id" in item for item in data if isinstance(item, dict))
                    if not has_mongo_id:
                        self.log_test("Messages List", True, 
                                    f"Retrieved {len(data)} messages without _id fields")
                        return True
                    else:
                        self.log_test("Messages List", False, 
                                    "Response contains _id fields", data[:2])
                else:
                    self.log_test("Messages List", False, "Response is not an array", data)
            else:
                self.log_test("Messages List", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Messages List", False, f"Error: {str(e)}")
        return False
    
    def test_messages_list_with_limit(self):
        """Test GET /api/whatsapp/messages with limit parameter"""
        try:
            response = self.session.get(f"{API_BASE}/whatsapp/messages?limit=5", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) <= 5:  # Should respect limit
                        self.log_test("Messages List (With Limit)", True, 
                                    f"Retrieved {len(data)} messages (≤ limit of 5)")
                        return True
                    else:
                        self.log_test("Messages List (With Limit)", False, 
                                    f"Returned {len(data)} messages, expected ≤ 5")
                else:
                    self.log_test("Messages List (With Limit)", False, "Response is not an array", data)
            else:
                self.log_test("Messages List (With Limit)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Messages List (With Limit)", False, f"Error: {str(e)}")
        return False
    
    def test_send_text_stub_mode(self):
        """Test POST /api/whatsapp/send in stub mode (no API key) - expect success with stub response"""
        try:
            send_request = {
                "to": "1234567890",
                "text": "Hello from CRM test suite!"
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/send",
                json=send_request,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["success", "mode", "id"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    if (data.get("success") is True and 
                        data.get("mode") == "stub" and
                        data.get("id")):
                        # Verify UUID format for id
                        try:
                            uuid.UUID(data["id"])
                            self.log_test("Send Text (Stub Mode)", True, 
                                        f"Successfully sent in stub mode with ID: {data['id']}")
                            return True
                        except ValueError:
                            self.log_test("Send Text (Stub Mode)", False, 
                                        "Invalid UUID format for id", data)
                    else:
                        self.log_test("Send Text (Stub Mode)", False, 
                                    "Invalid field values", data)
                else:
                    self.log_test("Send Text (Stub Mode)", False, 
                                f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("Send Text (Stub Mode)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Send Text (Stub Mode)", False, f"Error: {str(e)}")
        return False
    
    def test_send_text_missing_to(self):
        """Test POST /api/whatsapp/send without 'to' field - expect 400"""
        try:
            send_request = {
                "text": "Hello without recipient!"
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/send",
                json=send_request,
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("Send Text (Missing To)", True, 
                            "Correctly returned 400 for missing 'to' field")
                return True
            else:
                self.log_test("Send Text (Missing To)", False, 
                            f"Expected 400 but got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Send Text (Missing To)", False, f"Error: {str(e)}")
        return False
    
    def test_send_text_empty_to(self):
        """Test POST /api/whatsapp/send with empty 'to' field - expect 400"""
        try:
            send_request = {
                "to": "",
                "text": "Hello with empty recipient!"
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/send",
                json=send_request,
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("Send Text (Empty To)", True, 
                            "Correctly returned 400 for empty 'to' field")
                return True
            else:
                self.log_test("Send Text (Empty To)", False, 
                            f"Expected 400 but got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Send Text (Empty To)", False, f"Error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all WhatsApp tests in sequence"""
        print("🚀 Starting CRM WhatsApp Backend Test Suite")
        print("=" * 60)
        print("📱 Testing 360dialog WhatsApp integration in stub mode")
        print("=" * 60)
        
        # Test 1: Webhook verification
        print("\n1️⃣ Testing Webhook Verification...")
        self.test_webhook_verification_no_token()
        self.test_webhook_verification_wrong_mode()
        
        # Test 2: Webhook receive
        print("\n2️⃣ Testing Webhook Receive...")
        self.test_webhook_receive_no_signature()
        self.test_webhook_receive_with_signature()
        self.test_webhook_receive_invalid_json()
        
        # Test 3: Messages list
        print("\n3️⃣ Testing Messages List...")
        self.test_messages_list_empty()
        self.test_messages_list_with_limit()
        
        # Test 4: Send text messages
        print("\n4️⃣ Testing Send Text Messages...")
        self.test_send_text_stub_mode()
        self.test_send_text_missing_to()
        self.test_send_text_empty_to()
        
        # Summary
        self.print_summary()
        
        return self.get_overall_success()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 WHATSAPP TEST SUMMARY")
        print("=" * 60)
        
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
        
        print("\n📱 All tests run in STUB MODE (no real WhatsApp API calls)")
    
    def get_overall_success(self):
        """Get overall test success status"""
        if not self.test_results:
            return False
        
        # Critical tests that must pass for WhatsApp functionality
        critical_tests = [
            "Webhook Verification (No Token)",
            "Webhook Receive (No Signature)", 
            "Messages List",
            "Send Text (Stub Mode)"
        ]
        
        critical_passed = all(
            any(result["test"] == test and result["success"] for result in self.test_results)
            for test in critical_tests
        )
        
        return critical_passed

def main():
    """Main test execution"""
    tester = WhatsAppTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CRM WhatsApp backend tests completed successfully!")
        exit(0)
    else:
        print("\n❌ CRM WhatsApp backend tests had critical failures!")
        exit(1)

if __name__ == "__main__":
    main()