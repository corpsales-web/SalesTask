import requests
import json

def test_auth_flow():
    base_url = "https://aavana-green-crm.preview.emergentagent.com/api"
    
    print("🔐 Testing Authentication Flow...")
    
    # Test 1: Register a new user
    print("\n1. Testing User Registration...")
    user_data = {
        "username": "authtest789",
        "email": "authtest789@example.com",
        "phone": "9876543217",
        "full_name": "Auth Test User 3",
        "role": "Employee",
        "password": "SecurePass123!",
        "department": "Testing"
    }
    
    response = requests.post(f"{base_url}/auth/register", json=user_data)
    print(f"Registration Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Registration successful")
        reg_data = response.json()
        print(f"User ID: {reg_data.get('id')}")
    else:
        print(f"❌ Registration failed: {response.text}")
        return
    
    # Test 2: Login with username
    print("\n2. Testing Login with Username...")
    login_data = {
        "identifier": "authtest789",
        "password": "SecurePass123!"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    print(f"Login Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Login successful")
        login_response = response.json()
        token = login_response.get('access_token')
        print(f"Token received: {token[:20]}...")
        
        # Test 3: Use token to access protected endpoint
        print("\n3. Testing Protected Endpoint Access...")
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{base_url}/auth/me", headers=headers)
        print(f"Protected endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Protected endpoint access successful")
            user_profile = response.json()
            print(f"User profile: {user_profile.get('username')}")
        else:
            print(f"❌ Protected endpoint failed: {response.text}")
    else:
        print(f"❌ Login failed: {response.text}")

if __name__ == "__main__":
    test_auth_flow()