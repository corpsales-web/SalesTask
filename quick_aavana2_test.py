#!/usr/bin/env python3
"""
Quick Aavana 2.0 OpenAI Connection Test
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://green-crm-suite.preview.emergentagent.com/api"

def test_aavana2_chat():
    """Quick test of Aavana 2.0 chat endpoint"""
    print("🤖 TESTING AAVANA 2.0 CHAT ENDPOINT")
    print("=" * 45)
    
    test_cases = [
        {
            'name': 'Simple Greeting',
            'message': 'Hello, can you help me with lead management?',
            'context': 'general_inquiry'
        },
        {
            'name': 'Task Creation Query',
            'message': 'How do I create a new task?',
            'context': 'task_help'
        },
        {
            'name': 'Green Building Query',
            'message': 'What green building solutions do we offer?',
            'context': 'general_inquiry'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        
        payload = {
            'message': test_case['message'],
            'session_id': str(uuid.uuid4()),
            'context': test_case['context'],
            'user_id': 'test_user',
            'language': 'en'
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BACKEND_URL}/aavana2/chat",
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for OpenAI connection issues
                message = data.get('message', '')
                if 'trouble connecting to openai' in message.lower():
                    print(f"❌ OpenAI Connection Error: {message}")
                    results.append({'test': test_case['name'], 'success': False, 'issue': 'OpenAI Connection Error'})
                elif len(message) == 0:
                    print(f"⚠️ Empty Response - Possible OpenAI Issue")
                    print(f"   Response data: {json.dumps(data, indent=2)}")
                    results.append({'test': test_case['name'], 'success': False, 'issue': 'Empty Response'})
                else:
                    print(f"✅ Success ({response_time:.2f}s)")
                    print(f"   Message length: {len(message)} chars")
                    print(f"   Actions: {len(data.get('actions', []))}")
                    print(f"   Message preview: {message[:100]}...")
                    results.append({'test': test_case['name'], 'success': True, 'response_time': response_time})
                    
            else:
                print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
                results.append({'test': test_case['name'], 'success': False, 'issue': f'HTTP {response.status_code}'})
                
        except requests.exceptions.Timeout:
            print(f"❌ Timeout (>30s)")
            results.append({'test': test_case['name'], 'success': False, 'issue': 'Timeout'})
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({'test': test_case['name'], 'success': False, 'issue': str(e)})
        
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 20)
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    # Issues
    issues = [r for r in results if not r['success']]
    if issues:
        print(f"\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"   • {issue['test']}: {issue['issue']}")
    
    # Performance
    successful_tests = [r for r in results if r['success'] and 'response_time' in r]
    if successful_tests:
        avg_time = sum(r['response_time'] for r in successful_tests) / len(successful_tests)
        print(f"\n⏱️ Average Response Time: {avg_time:.2f}s")
    
    return passed == total

def test_openai_direct():
    """Test OpenAI API directly"""
    print(f"\n🔑 TESTING OPENAI API DIRECTLY")
    print("=" * 35)
    
    try:
        import openai
        import os
        from dotenv import load_dotenv
        
        load_dotenv('/app/backend/.env')
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ No OpenAI API key found")
            return False
            
        print(f"🔑 API Key: {api_key[:15]}...")
        
        client = openai.OpenAI(api_key=api_key)
        
        start_time = time.time()
        response = client.chat.completions.create(
            model='gpt-5',
            messages=[{'role': 'user', 'content': 'Test connection - respond with "OpenAI GPT-5 working"'}],
            max_completion_tokens=50
        )
        response_time = time.time() - start_time
        
        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content.strip()
            print(f"✅ GPT-5 Direct Test Success ({response_time:.2f}s)")
            print(f"   Response: {content}")
            return True
        else:
            print("❌ No response content received")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower():
            print(f"❌ QUOTA EXCEEDED: {error_msg}")
        elif "invalid" in error_msg.lower():
            print(f"❌ INVALID API KEY: {error_msg}")
        else:
            print(f"❌ API Error: {error_msg}")
        return False

if __name__ == "__main__":
    print("🚀 QUICK AAVANA 2.0 OPENAI CONNECTION TEST")
    print("=" * 50)
    
    # Test OpenAI directly first
    openai_working = test_openai_direct()
    
    # Test Aavana 2.0 chat
    aavana2_working = test_aavana2_chat()
    
    print(f"\n🎯 FINAL RESULTS")
    print("=" * 20)
    print(f"OpenAI Direct: {'✅ Working' if openai_working else '❌ Failed'}")
    print(f"Aavana 2.0 Chat: {'✅ Working' if aavana2_working else '❌ Failed'}")
    
    if openai_working and aavana2_working:
        print("\n🎉 SUCCESS: OpenAI connection fix is working!")
    elif openai_working and not aavana2_working:
        print("\n⚠️ PARTIAL: OpenAI works directly but Aavana 2.0 integration has issues")
    elif not openai_working:
        print("\n🚨 CRITICAL: OpenAI API connection is broken")
    else:
        print("\n❓ UNKNOWN: Unexpected test results")