#!/usr/bin/env python3
"""
Minimal test to isolate session transfer issue
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("email")
password = os.getenv("password")
device_id = "174353421"

def minimal_test():
    """Minimal test with no complexity"""
    
    # Step 1: Login
    session = requests.Session()
    session.get('https://binomo.com/', timeout=10)
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'device-id': device_id,
        'device-type': 'web',
        'origin': 'https://binomo.com',
        'referer': 'https://binomo.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'user-timezone': 'UTC'
    }
    
    payload = {"email": email, "password": password}
    
    response = session.post("https://api.binomo.com/passport/v2/sign_in?locale=en", 
                           headers=headers, json=payload, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
        
    auth_token = response.json()['data']['authtoken']
    print(f"✅ Login successful: {auth_token}")
    
    # Step 2: Test balance immediately
    balance_headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'authorization-token': auth_token,
        'cache-control': 'no-cache',
        'cookie': f'authtoken={auth_token}; device_type=web; device_id={device_id}',
        'device-id': device_id,
        'device-type': 'web',
        'origin': 'https://binomo.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://binomo.com/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'user-timezone': 'America/Santiago'
    }
    
    print("\n🔸 Test 1: Immediate balance request")
    resp1 = session.get("https://api.binomo.com/bank/v1/read?locale=en", headers=balance_headers, timeout=30)
    print(f"Status: {resp1.status_code}")
    
    # Step 3: Create a new session with same token
    print("\n🔸 Test 2: New session with same token")
    new_session = requests.Session()
    resp2 = new_session.get("https://api.binomo.com/bank/v1/read?locale=en", headers=balance_headers, timeout=30)
    print(f"Status: {resp2.status_code}")
    
    # Step 4: Store session in a variable and use it
    print("\n🔸 Test 3: Session stored in variable")
    stored_session = session  # This is what we do in the API
    resp3 = stored_session.get("https://api.binomo.com/bank/v1/read?locale=en", headers=balance_headers, timeout=30)
    print(f"Status: {resp3.status_code}")
    
    # Step 5: Pass session to a function
    print("\n🔸 Test 4: Session passed to function")
    def test_with_session(s, token, dev_id):
        hdrs = balance_headers.copy()
        hdrs['authorization-token'] = token
        hdrs['cookie'] = f'authtoken={token}; device_type=web; device_id={dev_id}'
        hdrs['device-id'] = dev_id
        return s.get("https://api.binomo.com/bank/v1/read?locale=en", headers=hdrs, timeout=30)
    
    resp4 = test_with_session(session, auth_token, device_id)
    print(f"Status: {resp4.status_code}")

if __name__ == "__main__":
    minimal_test()
