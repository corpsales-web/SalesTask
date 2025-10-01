#!/usr/bin/env python3
"""
CRM Backend Test Suite
Tests CRM Tasks and Leads endpoints to ensure compatibility with frontend after fixes
"""

import requests
import json
import time
import uuid
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception:
        pass
    return "https://aavana-crm-dmm.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class CRMBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_leads = []  # Track created leads for cleanup
        self.created_tasks = []  # Track created tasks for cleanup
        
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
    
    def test_health_endpoint(self):
        """Test GET /api/health - expect 200, JSON with status: ok, service: crm-backend, time ISO"""
        try:
            response = self.session.get(f"{API_BASE}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["status", "service", "time"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    if (data.get("status") == "ok" and 
                        data.get("service") == "crm-backend" and
                        data.get("time")):  # Check time is present and ISO format
                        try:
                            # Validate ISO format
                            datetime.fromisoformat(data["time"].replace('Z', '+00:00'))
                            self.log_test("Health Check", True, "CRM backend healthy with correct schema")
                            return True
                        except ValueError:
                            self.log_test("Health Check", False, "Invalid ISO time format", data)
                    else:
                        self.log_test("Health Check", False, "Invalid field values", data)
                else:
                    self.log_test("Health Check", False, f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_stt_chunk_endpoint(self):
        """Test POST /api/stt/chunk - expect stt_ready false (no creds)"""
        try:
            # Test with empty body
            response = self.session.post(f"{API_BASE}/stt/chunk", json={}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for stt_ready field
                if "stt_ready" in data:
                    stt_ready = data.get("stt_ready")
                    if stt_ready is False:
                        self.log_test("STT Chunk Endpoint", True, 
                                    "STT chunk correctly returns stt_ready: false (no credentials)")
                        return True
                    else:
                        self.log_test("STT Chunk Endpoint", False, 
                                    f"Expected stt_ready: false, got: {stt_ready}", data)
                else:
                    self.log_test("STT Chunk Endpoint", False, "Missing stt_ready field", data)
            else:
                self.log_test("STT Chunk Endpoint", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("STT Chunk Endpoint", False, f"Error: {str(e)}")
        return False
    
    def test_stt_websocket_stream(self):
        """Test WS /api/stt/stream - expect connection and error message when STT not configured"""
        try:
            # Convert HTTP URL to WebSocket URL
            ws_url = API_BASE.replace("https://", "wss://").replace("http://", "ws://") + "/stt/stream"
            
            messages_received = []
            connection_successful = False
            error_received = False
            
            def on_message(ws, message):
                nonlocal messages_received, error_received
                try:
                    data = json.loads(message)
                    messages_received.append(data)
                    if data.get("type") == "error" and "STT not configured" in data.get("message", ""):
                        error_received = True
                except json.JSONDecodeError:
                    messages_received.append({"raw": message})
            
            def on_open(ws):
                nonlocal connection_successful
                connection_successful = True
            
            def on_error(ws, error):
                print(f"WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                pass
            
            # Create WebSocket connection
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run WebSocket in a separate thread with timeout
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Wait for connection and messages
            time.sleep(3)
            ws.close()
            
            if connection_successful:
                if error_received:
                    self.log_test("STT WebSocket Stream", True, 
                                "WebSocket connected and received STT not configured error message")
                    return True
                elif messages_received:
                    self.log_test("STT WebSocket Stream", False, 
                                f"Connected but didn't receive expected error message. Got: {messages_received}")
                else:
                    self.log_test("STT WebSocket Stream", False, 
                                "Connected but no messages received")
            else:
                self.log_test("STT WebSocket Stream", False, "Failed to establish WebSocket connection")
                
        except Exception as e:
            self.log_test("STT WebSocket Stream", False, f"WebSocket error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all temp-restore server tests"""
        print("🚀 Starting CRM Backend Temp-Restore Test Suite")
        print("=" * 60)
        print(f"Testing server at: {BASE_URL}")
        print("=" * 60)
        
        # Test 1: Health endpoint
        print("\n1️⃣ Testing Health Endpoint...")
        health_success = self.test_health_endpoint()
        
        # Test 2: STT chunk endpoint
        print("\n2️⃣ Testing STT Chunk Endpoint...")
        chunk_success = self.test_stt_chunk_endpoint()
        
        # Test 3: STT WebSocket stream
        print("\n3️⃣ Testing STT WebSocket Stream...")
        ws_success = self.test_stt_websocket_stream()
        
        # Summary
        self.print_summary()
        
        # All three tests must pass for overall success
        return health_success and chunk_success and ws_success
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 CRM TEMP-RESTORE TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "No tests run")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        # Show passed tests
        passed_tests = [result for result in self.test_results if result["success"]]
        if passed_tests:
            print("\n✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"  • {test['test']}: {test['details']}")

def main():
    """Main test execution"""
    tester = CRMTempRestoreTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CRM Backend temp-restore tests PASSED!")
        return True
    else:
        print("\n❌ CRM Backend temp-restore tests FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)