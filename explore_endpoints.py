"""
Test script to discover potential HTTP-based trading endpoints
"""

import requests
import json
from BinomoAPI import BinomoAPI
import os
import dotenv

dotenv.load_dotenv()

def explore_api_endpoints():
    """Explore potential API endpoints for trading"""
    
    # Login first to get auth token
    email = os.getenv("email")
    password = os.getenv("password")
    
    login_response = BinomoAPI.login(email, password)
    if not login_response:
        print("❌ Login failed")
        return
        
    print(f"✅ Login successful: {login_response.authtoken[:10]}...")
    
    session = login_response._session
    auth_token = login_response.authtoken
    device_id = login_response.user_id
    
    # Common headers for API exploration
    headers = {
        'accept': 'application/json, text/plain, */*',
        'authorization-token': auth_token,
        'device-id': device_id,
        'device-type': 'web',
        'origin': 'https://binomo.com',
        'referer': 'https://binomo.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Potential trading endpoints to test
    base_url = "https://api.binomo.com"
    endpoints_to_test = [
        "/trading/v1/place",
        "/trading/v1/create",
        "/trading/v1/order",
        "/binary/v1/place",
        "/binary/v1/order",
        "/orders/v1/create",
        "/orders/v1/place",
        "/trade/v1/place",
        "/trade/v1/create",
        "/option/v1/place",
        "/option/v1/create",
        "/bo/v1/place",  # binary options
        "/bo/v1/create",
        "/turbo/v1/place",
        "/turbo/v1/create",
        "/v1/trading/place",
        "/v1/binary/place",
        "/v1/orders/create",
        "/v2/trading/place",
        "/v2/binary/place"
    ]
    
    # Also try different HTTP methods
    methods_to_test = ['GET', 'POST', 'PUT']
    
    print(f"\n🔍 Exploring {len(endpoints_to_test)} potential trading endpoints...")
    
    working_endpoints = []
    
    for endpoint in endpoints_to_test:
        full_url = f"{base_url}{endpoint}"
        
        for method in methods_to_test:
            try:
                if method == 'GET':
                    response = session.get(full_url, headers=headers, timeout=5)
                elif method == 'POST':
                    # Try with minimal trading data
                    test_data = {
                        "asset": "EUR/USD",
                        "direction": "call",
                        "amount": 1,
                        "duration": 60,
                        "account_type": "demo"
                    }
                    response = session.post(full_url, headers=headers, json=test_data, timeout=5)
                else:  # PUT
                    response = session.put(full_url, headers=headers, timeout=5)
                
                # Check for interesting responses
                if response.status_code != 404:  # Skip 404s
                    status_info = f"{method} {endpoint} -> {response.status_code}"
                    
                    if response.status_code == 200:
                        print(f"✅ {status_info} (SUCCESS!)")
                        working_endpoints.append((method, endpoint, response.status_code, response.text[:200]))
                    elif response.status_code == 401:
                        print(f"🔐 {status_info} (AUTH REQUIRED)")
                    elif response.status_code == 403:
                        print(f"🚫 {status_info} (FORBIDDEN)")
                    elif response.status_code == 400:
                        print(f"⚠️ {status_info} (BAD REQUEST - endpoint exists but wrong data)")
                        working_endpoints.append((method, endpoint, response.status_code, response.text[:200]))
                    elif response.status_code == 405:
                        print(f"❌ {status_info} (METHOD NOT ALLOWED)")
                    elif response.status_code == 500:
                        print(f"💥 {status_info} (SERVER ERROR)")
                    else:
                        print(f"❓ {status_info} (OTHER)")
                        
            except requests.exceptions.Timeout:
                pass  # Skip timeouts
            except Exception as e:
                pass  # Skip other errors
    
    print(f"\n📊 Exploration Results:")
    print(f"Total endpoints tested: {len(endpoints_to_test) * len(methods_to_test)}")
    print(f"Interesting responses: {len(working_endpoints)}")
    
    if working_endpoints:
        print("\n🎯 Potential working endpoints:")
        for method, endpoint, status, response_preview in working_endpoints:
            print(f"  {method} {endpoint} ({status})")
            if status == 200 or status == 400:
                print(f"    Response preview: {response_preview}")
    else:
        print("\n❌ No promising HTTP trading endpoints found")
        
    return working_endpoints

if __name__ == "__main__":
    explore_api_endpoints()
