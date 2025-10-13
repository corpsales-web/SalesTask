#!/usr/bin/env python3
"""
CRM Backend Targeted Test Suite
Tests specific endpoints and scenarios as requested in review:
1) POST /api/leads with phone normalization and owner_mobile defaulting
2) GET /api/leads/{id} returns the created lead
3) PUT /api/leads/{id} with owner_mobile normalization
4) POST /api/whatsapp/webhook with inbound message processing
5) GET /api/whatsapp/conversations shows proper conversation data
6) POST /api/whatsapp/send in stub mode with conversation updates
"""

import requests
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Configuration - Use production URL from frontend/.env
BASE_URL = "https://crm-whatsapp-hub-1.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class CRMTargetedTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_lead_id = None
        self.test_phone = "9876543210"
        self.test_phone_normalized = "+919876543210"
        self.owner_phone = "09999139938"
        self.owner_phone_normalized = "+919999139938"
        
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
    
    def test_1_create_lead_with_phone_normalization(self):
        """Test 1: POST /api/leads {name:'X', phone:'9876543210'} -> expect owner_mobile defaulted and phone normalized to +91 format"""
        try:
            lead_data = {
                "name": "Test Lead X",
                "phone": self.test_phone
            }
            
            response = self.session.post(
                f"{API_BASE}/leads",
                json=lead_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "lead" in data:
                    lead = data["lead"]
                    
                    # Check phone normalization
                    phone_normalized = lead.get("phone") == self.test_phone_normalized
                    
                    # Check owner_mobile defaulted
                    owner_defaulted = lead.get("owner_mobile") == "+919999139938"
                    
                    # Check UUID format
                    lead_id = lead.get("id")
                    try:
                        uuid.UUID(lead_id)
                        uuid_valid = True
                        self.created_lead_id = lead_id  # Store for next test
                    except (ValueError, TypeError):
                        uuid_valid = False
                    
                    # Check default status
                    status_correct = lead.get("status") == "New"
                    
                    if phone_normalized and owner_defaulted and uuid_valid and status_correct:
                        self.log_test("1. Create Lead with Phone Normalization", True, 
                                    f"Phone normalized to {lead.get('phone')}, owner_mobile defaulted to {lead.get('owner_mobile')}")
                        return True
                    else:
                        issues = []
                        if not phone_normalized: issues.append(f"phone not normalized (got: {lead.get('phone')})")
                        if not owner_defaulted: issues.append(f"owner_mobile not defaulted (got: {lead.get('owner_mobile')})")
                        if not uuid_valid: issues.append("invalid UUID")
                        if not status_correct: issues.append(f"wrong status (got: {lead.get('status')})")
                        self.log_test("1. Create Lead with Phone Normalization", False, 
                                    f"Issues: {', '.join(issues)}", data)
                else:
                    self.log_test("1. Create Lead with Phone Normalization", False, "Invalid response format", data)
            else:
                self.log_test("1. Create Lead with Phone Normalization", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("1. Create Lead with Phone Normalization", False, f"Error: {str(e)}")
        return False
    
    def test_2_get_created_lead(self):
        """Test 2: GET /api/leads/{id} returns the created lead"""
        if not self.created_lead_id:
            self.log_test("2. Get Created Lead", False, "No lead ID from previous test")
            return False
        
        try:
            response = self.session.get(
                f"{API_BASE}/leads/{self.created_lead_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "lead" in data:
                    lead = data["lead"]
                    
                    # Verify it's the same lead
                    correct_id = lead.get("id") == self.created_lead_id
                    correct_name = lead.get("name") == "Test Lead X"
                    correct_phone = lead.get("phone") == self.test_phone_normalized
                    correct_owner = lead.get("owner_mobile") == "+919999139938"
                    
                    if correct_id and correct_name and correct_phone and correct_owner:
                        self.log_test("2. Get Created Lead", True, 
                                    f"Retrieved lead with correct data: {lead.get('name')}")
                        return True
                    else:
                        issues = []
                        if not correct_id: issues.append("wrong ID")
                        if not correct_name: issues.append("wrong name")
                        if not correct_phone: issues.append("wrong phone")
                        if not correct_owner: issues.append("wrong owner_mobile")
                        self.log_test("2. Get Created Lead", False, 
                                    f"Data mismatch: {', '.join(issues)}", data)
                else:
                    self.log_test("2. Get Created Lead", False, "Invalid response format", data)
            elif response.status_code == 404:
                self.log_test("2. Get Created Lead", False, "Lead not found (404)")
            else:
                self.log_test("2. Get Created Lead", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("2. Get Created Lead", False, f"Error: {str(e)}")
        return False
    
    def test_3_update_lead_owner_mobile_normalization(self):
        """Test 3: PUT /api/leads/{id} with owner_mobile:'09999139938' -> normalized to +919999139938"""
        if not self.created_lead_id:
            self.log_test("3. Update Lead Owner Mobile", False, "No lead ID from previous test")
            return False
        
        try:
            update_data = {
                "owner_mobile": self.owner_phone  # "09999139938"
            }
            
            response = self.session.put(
                f"{API_BASE}/leads/{self.created_lead_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "lead" in data:
                    lead = data["lead"]
                    
                    # Check owner_mobile normalization
                    owner_normalized = lead.get("owner_mobile") == self.owner_phone_normalized
                    
                    # Check updated_at timestamp updated
                    updated_at = lead.get("updated_at")
                    timestamp_valid = False
                    if updated_at:
                        try:
                            datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                            timestamp_valid = True
                        except ValueError:
                            pass
                    
                    if owner_normalized and timestamp_valid:
                        self.log_test("3. Update Lead Owner Mobile", True, 
                                    f"Owner mobile normalized to {lead.get('owner_mobile')}")
                        return True
                    else:
                        issues = []
                        if not owner_normalized: issues.append(f"owner_mobile not normalized (got: {lead.get('owner_mobile')})")
                        if not timestamp_valid: issues.append("invalid updated_at timestamp")
                        self.log_test("3. Update Lead Owner Mobile", False, 
                                    f"Issues: {', '.join(issues)}", data)
                else:
                    self.log_test("3. Update Lead Owner Mobile", False, "Invalid response format", data)
            else:
                self.log_test("3. Update Lead Owner Mobile", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("3. Update Lead Owner Mobile", False, f"Error: {str(e)}")
        return False
    
    def test_4_whatsapp_webhook_inbound_processing(self):
        """Test 4: POST /api/whatsapp/webhook with sample inbound from 919876543210 -> conversations updated with owner_mobile and preview fields"""
        try:
            # Sample WhatsApp webhook payload for inbound message
            webhook_payload = {
                "object": "whatsapp_business_account",
                "entry": [
                    {
                        "id": "123456789",
                        "changes": [
                            {
                                "value": {
                                    "messaging_product": "whatsapp",
                                    "metadata": {
                                        "display_phone_number": "919999139938",
                                        "phone_number_id": "123456789"
                                    },
                                    "messages": [
                                        {
                                            "from": "919876543210",
                                            "id": "wamid.test123",
                                            "timestamp": str(int(time.time())),
                                            "type": "text",
                                            "text": {
                                                "body": "Hello, I'm interested in your services!"
                                            }
                                        }
                                    ]
                                },
                                "field": "messages"
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/webhook",
                json=webhook_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("4. WhatsApp Webhook Inbound", True, 
                                "Webhook processed successfully")
                    return True
                else:
                    self.log_test("4. WhatsApp Webhook Inbound", False, "Webhook not successful", data)
            else:
                self.log_test("4. WhatsApp Webhook Inbound", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("4. WhatsApp Webhook Inbound", False, f"Error: {str(e)}")
        return False
    
    def test_5_whatsapp_conversations_data(self):
        """Test 5: GET /api/whatsapp/conversations shows contact +919876543210, last_message_text, last_message_dir='in', owner_mobile present"""
        try:
            # Wait a moment for webhook processing
            time.sleep(1)
            
            response = self.session.get(
                f"{API_BASE}/whatsapp/conversations",
                timeout=10
            )
            
            if response.status_code == 200:
                conversations = response.json()
                if isinstance(conversations, list):
                    # Find conversation with our test contact
                    test_conversation = None
                    for conv in conversations:
                        if conv.get("contact") == self.test_phone_normalized:
                            test_conversation = conv
                            break
                    
                    if test_conversation:
                        # Check required fields
                        contact_correct = test_conversation.get("contact") == self.test_phone_normalized
                        has_last_message_text = "last_message_text" in test_conversation
                        message_dir_in = test_conversation.get("last_message_dir") == "in"
                        has_owner_mobile = "owner_mobile" in test_conversation
                        
                        # Check if linked to our created lead
                        linked_to_lead = test_conversation.get("lead_id") == self.created_lead_id
                        
                        if contact_correct and has_last_message_text and message_dir_in and has_owner_mobile:
                            details = f"Contact: {test_conversation.get('contact')}, " \
                                    f"Message: '{test_conversation.get('last_message_text')}', " \
                                    f"Direction: {test_conversation.get('last_message_dir')}, " \
                                    f"Owner: {test_conversation.get('owner_mobile')}"
                            if linked_to_lead:
                                details += f", Linked to lead: {test_conversation.get('lead_id')}"
                            
                            self.log_test("5. WhatsApp Conversations Data", True, details)
                            return True
                        else:
                            issues = []
                            if not contact_correct: issues.append("wrong contact")
                            if not has_last_message_text: issues.append("missing last_message_text")
                            if not message_dir_in: issues.append(f"wrong direction (got: {test_conversation.get('last_message_dir')})")
                            if not has_owner_mobile: issues.append("missing owner_mobile")
                            self.log_test("5. WhatsApp Conversations Data", False, 
                                        f"Issues: {', '.join(issues)}", test_conversation)
                    else:
                        self.log_test("5. WhatsApp Conversations Data", False, 
                                    f"No conversation found for contact {self.test_phone_normalized}")
                else:
                    self.log_test("5. WhatsApp Conversations Data", False, "Response is not a list", conversations)
            else:
                self.log_test("5. WhatsApp Conversations Data", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("5. WhatsApp Conversations Data", False, f"Error: {str(e)}")
        return False
    
    def test_6_whatsapp_send_stub_mode(self):
        """Test 6: POST /api/whatsapp/send {to:'+919876543210', text:'Hi'} -> stub mode ok and conversations updated with last_message_dir='out' and preview"""
        try:
            send_data = {
                "to": self.test_phone_normalized,
                "text": "Hi, thanks for your interest!"
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/send",
                json=send_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Check if it's stub mode
                    is_stub_mode = data.get("mode") == "stub"
                    has_message_id = "id" in data
                    
                    if is_stub_mode and has_message_id:
                        # Now check if conversation was updated
                        time.sleep(1)  # Wait for update
                        
                        conv_response = self.session.get(f"{API_BASE}/whatsapp/conversations", timeout=10)
                        if conv_response.status_code == 200:
                            conversations = conv_response.json()
                            test_conversation = None
                            for conv in conversations:
                                if conv.get("contact") == self.test_phone_normalized:
                                    test_conversation = conv
                                    break
                            
                            if test_conversation:
                                # Check conversation updated with outbound message
                                message_dir_out = test_conversation.get("last_message_dir") == "out"
                                has_outbound_text = test_conversation.get("last_message_text") == send_data["text"]
                                unread_reset = test_conversation.get("unread_count", 1) == 0
                                
                                if message_dir_out and has_outbound_text and unread_reset:
                                    self.log_test("6. WhatsApp Send Stub Mode", True, 
                                                f"Stub mode send successful, conversation updated with outbound message")
                                    return True
                                else:
                                    issues = []
                                    if not message_dir_out: issues.append(f"wrong direction (got: {test_conversation.get('last_message_dir')})")
                                    if not has_outbound_text: issues.append(f"wrong text (got: {test_conversation.get('last_message_text')})")
                                    if not unread_reset: issues.append(f"unread not reset (got: {test_conversation.get('unread_count')})")
                                    self.log_test("6. WhatsApp Send Stub Mode", False, 
                                                f"Conversation not properly updated: {', '.join(issues)}", test_conversation)
                            else:
                                self.log_test("6. WhatsApp Send Stub Mode", False, 
                                            "Conversation not found after send")
                        else:
                            self.log_test("6. WhatsApp Send Stub Mode", False, 
                                        "Could not retrieve conversations after send")
                    else:
                        issues = []
                        if not is_stub_mode: issues.append(f"not stub mode (got: {data.get('mode')})")
                        if not has_message_id: issues.append("missing message ID")
                        self.log_test("6. WhatsApp Send Stub Mode", False, 
                                    f"Send response issues: {', '.join(issues)}", data)
                else:
                    self.log_test("6. WhatsApp Send Stub Mode", False, "Send not successful", data)
            else:
                self.log_test("6. WhatsApp Send Stub Mode", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("6. WhatsApp Send Stub Mode", False, f"Error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all targeted tests in sequence"""
        print("🚀 Starting CRM Backend Targeted Test Suite")
        print("=" * 60)
        print("Testing specific endpoints and scenarios as requested")
        print("=" * 60)
        
        # Run tests in sequence
        tests = [
            self.test_1_create_lead_with_phone_normalization,
            self.test_2_get_created_lead,
            self.test_3_update_lead_owner_mobile_normalization,
            self.test_4_whatsapp_webhook_inbound_processing,
            self.test_5_whatsapp_conversations_data,
            self.test_6_whatsapp_send_stub_mode
        ]
        
        for i, test_func in enumerate(tests, 1):
            print(f"\n{i}️⃣ Running {test_func.__doc__.split(':')[0].strip()}...")
            test_func()
        
        # Summary
        self.print_summary()
        
        return self.get_overall_success()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TARGETED TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show all test results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}: {result['details']}")
        
        # Show failed tests details
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS DETAILS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
                if test.get('response_data'):
                    print(f"    Response: {json.dumps(test['response_data'], indent=4)}")
    
    def get_overall_success(self):
        """Get overall test success status"""
        if not self.test_results:
            return False
        
        # All tests are critical for the requested functionality
        return all(result["success"] for result in self.test_results)

def main():
    """Main test execution"""
    tester = CRMTargetedTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CRM Backend targeted tests completed successfully!")
        exit(0)
    else:
        print("\n❌ CRM Backend targeted tests had failures!")
        exit(1)

if __name__ == "__main__":
    main()