#!/usr/bin/env python3
"""
OpenAI API Debug Test
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

def test_openai_api():
    """Test OpenAI API with different models and parameters"""
    print("🔑 OPENAI API DEBUG TEST")
    print("=" * 30)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found")
        return
        
    print(f"🔑 API Key: {api_key[:20]}...")
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Test different models and parameters
        test_cases = [
            {
                'name': 'GPT-5 Basic Test',
                'model': 'gpt-5',
                'params': {
                    'messages': [{'role': 'user', 'content': 'Say "Hello from GPT-5"'}],
                    'max_completion_tokens': 50
                }
            },
            {
                'name': 'GPT-4o Test',
                'model': 'gpt-4o',
                'params': {
                    'messages': [{'role': 'user', 'content': 'Say "Hello from GPT-4o"'}],
                    'max_tokens': 50
                }
            },
            {
                'name': 'GPT-5 with max_completion_tokens',
                'model': 'gpt-5',
                'params': {
                    'messages': [{'role': 'user', 'content': 'Explain green building in one sentence'}],
                    'max_completion_tokens': 100
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['name']}")
            try:
                response = client.chat.completions.create(
                    model=test_case['model'],
                    **test_case['params']
                )
                
                if response.choices and response.choices[0].message.content:
                    content = response.choices[0].message.content.strip()
                    print(f"✅ Success: {content}")
                    
                    # Check usage info
                    if hasattr(response, 'usage') and response.usage:
                        print(f"   Tokens used: {response.usage.total_tokens}")
                else:
                    print("❌ No response content")
                    
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error: {error_msg}")
                
                # Analyze error type
                if "quota" in error_msg.lower():
                    print("   🚨 QUOTA ISSUE: Check billing and usage limits")
                elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                    print("   🚨 API KEY ISSUE: Invalid or expired key")
                elif "model" in error_msg.lower():
                    print("   🚨 MODEL ISSUE: Model not available or incorrect name")
                elif "parameter" in error_msg.lower() or "unsupported" in error_msg.lower():
                    print("   🚨 PARAMETER ISSUE: Invalid parameters for this model")
                else:
                    print("   🚨 UNKNOWN ISSUE: Check OpenAI service status")
                    
    except ImportError:
        print("❌ OpenAI library not installed")
    except Exception as e:
        print(f"❌ Setup error: {str(e)}")

if __name__ == "__main__":
    test_openai_api()