#!/usr/bin/env python3
"""
Test emergentintegrations import during function execution
"""

import sys
sys.path.append('/app/backend')

def test_emergent_import():
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        from dotenv import load_dotenv
        
        load_dotenv()
        import os
        api_key = os.getenv('EMERGENT_LLM_KEY')
        
        print(f"✅ Import successful, API key: {api_key[:20]}..." if api_key else "❌ No API key")
        
        # Test creating LlmChat instance
        chat = LlmChat(
            api_key=api_key,
            session_id="test_session",
            system_message="Test system message"
        )
        print("✅ LlmChat instance created successfully")
        
        # Test creating UserMessage
        user_message = UserMessage(text="Test message")
        print("✅ UserMessage created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during import/initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_emergent_import()