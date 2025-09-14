import requests
import json
import sys

def test_ai_endpoint(name, endpoint, method="POST", data=None, params=None, timeout=30):
    """Test a single AI endpoint with timeout"""
    base_url = "https://aavana-crm-1.preview.emergentagent.com/api"
    url = f"{base_url}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    print(f"\n🔍 Testing {name}...")
    print(f"   URL: {url}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PASSED")
            try:
                resp_data = response.json()
                if isinstance(resp_data, dict):
                    # Show key indicators of AI response
                    key_fields = ['lead_scoring', 'conversation_analysis', 'response', 'context', 'insights', 'content']
                    for field in key_fields:
                        if field in resp_data:
                            print(f"   AI Response: Contains '{field}' field")
                            break
                    else:
                        print(f"   Response keys: {list(resp_data.keys())[:3]}...")
                return True
            except:
                print("   Response: Non-JSON or empty")
                return True
        else:
            print("❌ FAILED")
            try:
                error = response.json()
                print(f"   Error: {error.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text[:100]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ FAILED - Timeout (>30s)")
        return False
    except Exception as e:
        print(f"❌ FAILED - {str(e)}")
        return False

def main():
    print("🚀 Quick AI Stack Integration Test")
    print("=" * 50)
    
    # Create a test lead first
    print("\n🔧 Creating test lead...")
    test_lead = {
        "name": "AI Test Client",
        "phone": "9876543210", 
        "email": "aitest@example.com",
        "budget": 500000,
        "space_size": "3 BHK",
        "location": "Mumbai"
    }
    
    try:
        response = requests.post(
            "https://aavana-crm-1.preview.emergentagent.com/api/leads",
            json=test_lead,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 200:
            lead_data = response.json()
            test_lead_id = lead_data['id']
            print(f"✅ Test lead created: {test_lead_id}")
        else:
            print("❌ Failed to create test lead")
            test_lead_id = "test_lead_id"
    except:
        print("❌ Failed to create test lead")
        test_lead_id = "test_lead_id"
    
    # Test key AI endpoints
    tests = [
        # Basic AI endpoints
        {
            "name": "AI Insights Generation",
            "endpoint": "ai/insights",
            "data": {"type": "leads", "timeframe": "current"}
        },
        {
            "name": "AI Content Generation", 
            "endpoint": "ai/generate-content",
            "data": {
                "type": "social_post",
                "topic": "Winter gardening tips",
                "target_audience": "Urban homeowners"
            }
        },
        {
            "name": "AI Voice to Task",
            "endpoint": "ai/voice-to-task",
            "data": {
                "voice_input": "Schedule a follow-up call with the Mumbai client tomorrow",
                "context": {"user": "Sales Team"}
            }
        },
        
        # CRM AI endpoints
        {
            "name": "AI Conversation Analysis",
            "endpoint": "ai/crm/conversation-analysis",
            "data": {
                "conversation": [
                    {"speaker": "customer", "message": "I need a balcony garden setup"},
                    {"speaker": "agent", "message": "We can help with that. What's your budget?"}
                ]
            }
        },
        
        # Marketing AI
        {
            "name": "AI Campaign Optimizer",
            "endpoint": "ai/marketing/campaign-optimizer", 
            "data": {
                "campaign_name": "Test Campaign",
                "budget": 50000,
                "channels": ["Google Ads", "Facebook"]
            }
        },
        
        # Global AI Assistant
        {
            "name": "AI Global Assistant",
            "endpoint": "ai/chat/global-assistant",
            "data": {
                "message": "What's the status of our business?",
                "context": {"user_role": "Manager"}
            }
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test_ai_endpoint(test["name"], test["endpoint"], data=test["data"]):
            passed += 1
    
    # Cleanup test lead
    if test_lead_id != "test_lead_id":
        try:
            requests.delete(
                f"https://aavana-crm-1.preview.emergentagent.com/api/leads/{test_lead_id}",
                timeout=10
            )
            print(f"\n🧹 Cleaned up test lead")
        except:
            pass
    
    # Results
    print("\n" + "=" * 50)
    print(f"📊 QUICK AI TEST RESULTS")
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("🎉 All AI endpoints are working!")
        return 0
    else:
        print("⚠️ Some AI endpoints have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())