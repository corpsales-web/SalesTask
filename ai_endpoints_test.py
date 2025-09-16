import requests
import sys
import json
from datetime import datetime, timezone
import uuid

class AIEndpointsTester:
    def __init__(self, base_url="https://navdebug-crm.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if params:
            print(f"   Params: {params}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    # Show a preview of the response for AI endpoints
                    if isinstance(response_data, dict):
                        if len(str(response_data)) > 500:
                            print(f"   Response: Large response received (AI generated content)")
                            # Show just the keys for large responses
                            print(f"   Response keys: {list(response_data.keys())}")
                        else:
                            print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    print(f"   Response: Non-JSON response received")
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'url': url
                })
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'expected': expected_status,
                'actual': 'Exception',
                'error': str(e),
                'url': url
            })
            return False, {}

    def test_smart_lead_scoring(self):
        """Test Smart Lead Scoring endpoint"""
        # Test with a test lead ID
        test_lead_id = "test_lead_id"
        params = {"lead_id": test_lead_id}
        return self.run_test(
            "Smart Lead Scoring", 
            "POST", 
            "ai/crm/smart-lead-scoring", 
            200,
            params=params
        )

    def test_deal_prediction(self):
        """Test Deal Prediction endpoint"""
        return self.run_test(
            "Deal Prediction", 
            "POST", 
            "ai/sales/deal-prediction", 
            200
        )

    def test_smart_proposal_generator(self):
        """Test Smart Proposal Generator endpoint"""
        test_lead_id = "test_lead"
        service_type = "balcony_garden"
        params = {"lead_id": test_lead_id, "service_type": service_type}
        return self.run_test(
            "Smart Proposal Generator", 
            "POST", 
            "ai/sales/smart-proposal-generator", 
            200,
            params=params
        )

    def test_recall_context(self):
        """Test Recall Context endpoint"""
        test_client_id = "test_client_id"
        params = {"query": "Complete client history"}
        return self.run_test(
            "Recall Context", 
            "GET", 
            f"ai/recall-context/{test_client_id}", 
            200,
            params=params
        )

    def test_with_real_lead_ids(self):
        """Test with real lead IDs if available"""
        print("\n🔍 Attempting to get real lead IDs for testing...")
        
        # Try to get existing leads
        try:
            response = requests.get(f"{self.base_url}/leads", timeout=10)
            if response.status_code == 200:
                leads = response.json()
                if leads and len(leads) > 0:
                    real_lead_id = leads[0]['id']
                    print(f"   Found real lead ID: {real_lead_id}")
                    
                    # Test with real lead ID
                    params = {"lead_id": real_lead_id}
                    self.run_test(
                        "Smart Lead Scoring (Real Lead)", 
                        "POST", 
                        "ai/crm/smart-lead-scoring", 
                        200,
                        params=params
                    )
                    
                    params = {"lead_id": real_lead_id, "service_type": "balcony_garden"}
                    self.run_test(
                        "Smart Proposal Generator (Real Lead)", 
                        "POST", 
                        "ai/sales/smart-proposal-generator", 
                        200,
                        params=params
                    )
                    
                    params = {"query": "Complete client history"}
                    self.run_test(
                        "Recall Context (Real Lead)", 
                        "GET", 
                        f"ai/recall-context/{real_lead_id}", 
                        200,
                        params=params
                    )
                else:
                    print("   No existing leads found, skipping real lead tests")
            else:
                print(f"   Could not fetch leads (status: {response.status_code})")
        except Exception as e:
            print(f"   Error fetching leads: {str(e)}")

def main():
    print("🚀 Starting AI Endpoints Testing")
    print("Testing 4 previously failing AI endpoints to verify database fixes")
    print("=" * 70)
    
    tester = AIEndpointsTester()

    # Test basic health check first
    print("\n📋 Basic Health Check...")
    success, _ = tester.run_test("Health Check", "GET", "", 200)
    if not success:
        print("❌ Health check failed, but continuing with AI endpoint tests")

    print("\n🤖 Testing Critical AI Endpoints...")
    
    # Test 1: Smart Lead Scoring
    print("\n1️⃣ Smart Lead Scoring Endpoint")
    tester.test_smart_lead_scoring()

    # Test 2: Deal Prediction
    print("\n2️⃣ Deal Prediction Endpoint")
    tester.test_deal_prediction()

    # Test 3: Smart Proposal Generator
    print("\n3️⃣ Smart Proposal Generator Endpoint")
    tester.test_smart_proposal_generator()

    # Test 4: Recall Context
    print("\n4️⃣ Recall Context Endpoint")
    tester.test_recall_context()

    # Test 5: Try with real lead IDs if available
    print("\n5️⃣ Testing with Real Lead IDs (if available)")
    tester.test_with_real_lead_ids()

    # Final Results
    print("\n" + "=" * 70)
    print(f"📊 AI ENDPOINTS TEST RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for failed in tester.failed_tests:
            print(f"   • {failed['name']}: Expected {failed['expected']}, got {failed['actual']}")
            if 'error' in failed:
                print(f"     Error: {failed['error']}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All AI endpoints are working correctly!")
        print("✅ Database fallback mechanisms are functioning properly")
        return 0
    else:
        print("⚠️ Some AI endpoints are still failing.")
        print("❌ Database fixes may need additional work")
        return 1

if __name__ == "__main__":
    sys.exit(main())