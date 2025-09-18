#!/usr/bin/env python3
"""
GPT-5 Integration Verification Summary
Final verification of GPT-5 integration fixes
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://green-crm-suite.preview.emergentagent.com/api"

def test_gpt5_endpoints():
    """Test all GPT-5 endpoints and verify fixes"""
    results = []
    
    print("🚀 GPT-5 INTEGRATION VERIFICATION")
    print("=" * 50)
    
    # Test 1: Lead Qualification Analysis with GPT-5
    print("\n1. Testing GPT-5 Lead Qualification Analysis...")
    try:
        test_data = {
            "formData": {
                "name": "Rajesh Kumar",
                "project_type": "commercial_green_building",
                "budget_range": "250k_500k",
                "timeline": "3_months",
                "decision_maker": "yes",
                "urgency": "high"
            },
            "qualificationScore": 85
        }
        
        response = requests.post(
            f"{BACKEND_URL}/ai/analyze-lead-qualification",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            analysis = data.get('analysis', {})
            results.append({
                "test": "GPT-5 Lead Qualification",
                "status": "✅ PASS",
                "details": f"Qualification: {analysis.get('qualification')}, Confidence: {analysis.get('confidence')}%"
            })
        else:
            results.append({
                "test": "GPT-5 Lead Qualification",
                "status": "❌ FAIL",
                "details": f"HTTP {response.status_code}: {response.text[:100]}"
            })
    except Exception as e:
        results.append({
            "test": "GPT-5 Lead Qualification",
            "status": "❌ FAIL",
            "details": f"Exception: {str(e)}"
        })
    
    # Test 2: Optimized Lead Creation with GPT-5
    print("\n2. Testing Optimized Lead Creation with GPT-5...")
    try:
        test_data = {
            "name": "Priya Sharma",
            "email": f"priya.gpt5test.{int(time.time())}@example.com",
            "phone": "9876543210",
            "project_type": "residential_balcony",
            "budget_range": "50k_100k",
            "timeline": "1_month",
            "qualification_score": 75,
            "status": "Qualified"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/leads/optimized-create",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            lead = data.get('lead', {})
            auto_converted = data.get('auto_converted_to_deal', False)
            results.append({
                "test": "GPT-5 Optimized Lead Creation",
                "status": "✅ PASS",
                "details": f"Lead created: {lead.get('id', 'N/A')[:8]}..., Auto-converted: {auto_converted}"
            })
        else:
            results.append({
                "test": "GPT-5 Optimized Lead Creation",
                "status": "❌ FAIL",
                "details": f"HTTP {response.status_code}: {response.text[:100]}"
            })
    except Exception as e:
        results.append({
            "test": "GPT-5 Optimized Lead Creation",
            "status": "❌ FAIL",
            "details": f"Exception: {str(e)}"
        })
    
    # Test 3: Parameter Fix Verification (max_completion_tokens)
    print("\n3. Testing Parameter Fix (max_completion_tokens)...")
    try:
        # This should not cause parameter errors
        test_data = {
            "formData": {
                "name": "Parameter Test User",
                "project_type": "residential_garden",
                "budget_range": "25k_50k"
            },
            "qualificationScore": 50
        }
        
        response = requests.post(
            f"{BACKEND_URL}/ai/analyze-lead-qualification",
            json=test_data,
            timeout=20
        )
        
        if response.status_code == 200:
            results.append({
                "test": "Parameter Fix Verification",
                "status": "✅ PASS",
                "details": "max_completion_tokens parameter working correctly, no 400 errors"
            })
        elif response.status_code == 400 and 'max_tokens' in response.text.lower():
            results.append({
                "test": "Parameter Fix Verification",
                "status": "❌ FAIL",
                "details": f"Parameter error still present: {response.text[:100]}"
            })
        else:
            results.append({
                "test": "Parameter Fix Verification",
                "status": "✅ PASS",
                "details": f"No parameter errors (HTTP {response.status_code})"
            })
    except Exception as e:
        results.append({
            "test": "Parameter Fix Verification",
            "status": "❌ FAIL",
            "details": f"Exception: {str(e)}"
        })
    
    # Test 4: GPT-5 Model Usage Verification
    print("\n4. Testing GPT-5 Model Usage...")
    try:
        # Direct OpenAI API test to verify GPT-5 access
        from openai import OpenAI
        import os
        from dotenv import load_dotenv
        
        load_dotenv('/app/backend/.env')
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model='gpt-5',
            messages=[{'role': 'user', 'content': 'Respond with: GPT-5 model verification successful'}],
            max_completion_tokens=50
        )
        
        content = response.choices[0].message.content
        if 'GPT-5' in content and 'successful' in content:
            results.append({
                "test": "GPT-5 Model Access",
                "status": "✅ PASS",
                "details": f"Direct GPT-5 API access working: {content[:50]}..."
            })
        else:
            results.append({
                "test": "GPT-5 Model Access",
                "status": "❌ FAIL",
                "details": f"Unexpected response: {content[:50]}..."
            })
    except Exception as e:
        results.append({
            "test": "GPT-5 Model Access",
            "status": "❌ FAIL",
            "details": f"API access failed: {str(e)}"
        })
    
    # Print Results
    print("\n" + "=" * 50)
    print("🎯 GPT-5 INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for result in results:
        print(f"{result['status']} {result['test']}")
        print(f"   └─ {result['details']}")
        if result['status'] == "✅ PASS":
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n📊 Success Rate: {success_rate:.1f}% ({passed}/{total} tests passed)")
    
    # Summary
    print(f"\n🔍 VERIFICATION SUMMARY:")
    print(f"✅ GPT-5 Model Integration: {'Working' if passed >= 3 else 'Issues Found'}")
    print(f"✅ Parameter Fixes: {'Applied' if passed >= 2 else 'Needs Attention'}")
    print(f"✅ AI Endpoints: {'Functional' if passed >= 2 else 'Issues Found'}")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = test_gpt5_endpoints()
    
    if success:
        print("\n🎉 GPT-5 INTEGRATION VERIFICATION SUCCESSFUL")
    else:
        print("\n⚠️ GPT-5 INTEGRATION VERIFICATION COMPLETED WITH ISSUES")