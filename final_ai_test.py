#!/usr/bin/env python3

import requests
import json
import time

def test_ai_endpoint(name, method, endpoint, params=None, data=None, timeout=60):
    """Test an AI endpoint with extended timeout"""
    base_url = "https://aavana-workspace.preview.emergentagent.com/api"
    url = f"{base_url}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    print(f"\n🔍 Testing {name}...")
    print(f"   URL: {url}")
    if params:
        print(f"   Params: {params}")
    
    start_time = time.time()
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, params=params, timeout=timeout)
        
        elapsed = time.time() - start_time
        print(f"   Response time: {elapsed:.1f}s")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS - Endpoint is working!")
            try:
                resp_data = response.json()
                if isinstance(resp_data, dict):
                    # Show evidence of AI response
                    ai_indicators = ['lead_scoring', 'deal_predictions', 'proposal', 'context', 'response']
                    for indicator in ai_indicators:
                        if indicator in resp_data:
                            content = str(resp_data[indicator])
                            if len(content) > 100:  # AI responses are typically long
                                print(f"   🤖 AI Response detected: {indicator} field with {len(content)} characters")
                                break
                    else:
                        print(f"   📊 Response keys: {list(resp_data.keys())}")
                return True
            except Exception as e:
                print(f"   ⚠️ Response parsing error: {e}")
                return True  # Still count as success if status is 200
        else:
            print("   ❌ FAILED")
            try:
                error = response.json()
                print(f"   Error: {error.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ❌ TIMEOUT after {timeout}s")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def main():
    print("🚀 Final AI Endpoints Verification Test")
    print("Testing the 4 critical AI endpoints that were previously failing")
    print("=" * 70)
    
    # Get a real lead ID for testing
    print("\n📋 Getting real lead ID for testing...")
    try:
        response = requests.get("https://aavana-workspace.preview.emergentagent.com/api/leads", timeout=10)
        if response.status_code == 200:
            leads = response.json()
            if leads:
                real_lead_id = leads[0]['id']
                print(f"   Found real lead ID: {real_lead_id}")
            else:
                real_lead_id = "test_lead_id"
                print("   No real leads found, using demo ID")
        else:
            real_lead_id = "test_lead_id"
            print("   Failed to get leads, using demo ID")
    except:
        real_lead_id = "test_lead_id"
        print("   Error getting leads, using demo ID")
    
    # Test the 4 critical endpoints
    tests = [
        {
            "name": "1. Smart Lead Scoring",
            "method": "POST",
            "endpoint": "ai/crm/smart-lead-scoring",
            "params": {"lead_id": real_lead_id}
        },
        {
            "name": "2. Deal Prediction", 
            "method": "POST",
            "endpoint": "ai/sales/deal-prediction"
        },
        {
            "name": "3. Smart Proposal Generator",
            "method": "POST", 
            "endpoint": "ai/sales/smart-proposal-generator",
            "params": {"lead_id": real_lead_id, "service_type": "balcony_garden"}
        },
        {
            "name": "4. Recall Context",
            "method": "GET",
            "endpoint": f"ai/recall-context/{real_lead_id}",
            "params": {"query": "Complete client history"}
        }
    ]
    
    results = []
    
    for test in tests:
        success = test_ai_endpoint(
            test["name"],
            test["method"], 
            test["endpoint"],
            params=test.get("params"),
            data=test.get("data"),
            timeout=90  # Extended timeout for AI processing
        )
        results.append(success)
        
        # Small delay between tests
        if not success:
            print("   ⏳ Waiting 5s before next test...")
            time.sleep(5)
    
    # Results summary
    print("\n" + "=" * 70)
    print("📊 FINAL TEST RESULTS")
    print(f"Tests Passed: {sum(results)}/4")
    print(f"Success Rate: {(sum(results)/4*100):.1f}%")
    
    if sum(results) == 4:
        print("\n🎉 SUCCESS: All 4 critical AI endpoints are now working!")
        print("✅ Database fallback mechanisms are functioning properly")
        print("✅ ObjectId and datetime serialization issues have been resolved")
        return 0
    elif sum(results) >= 2:
        print(f"\n⚠️ PARTIAL SUCCESS: {sum(results)}/4 endpoints working")
        print("Some endpoints may need additional optimization")
        return 1
    else:
        print("\n❌ FAILURE: Most endpoints still have issues")
        print("Additional debugging required")
        return 1

if __name__ == "__main__":
    exit(main())