#!/usr/bin/env python3
"""
Test immediate balance request within the login session
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("email")
password = os.getenv("password")
device_id = "174353421"

def test_login_and_balance():
    """Test login and balance in one continuous session"""
    
    # Create session
    session = requests.Session()
    
    # Visit main site first
    try:
        session.get('https://binomo.com/', timeout=10)
        print("✅ Visited main site")
    except:
        print("⚠️ Failed to visit main site")
    
    # Login
    login_headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'device-id': device_id,
        'device-type': 'web',  # This was missing!
        'origin': 'https://binomo.com',
        'referer': 'https://binomo.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'user-timezone': 'UTC'
    }
    
    login_payload = {
        "email": email,
        "password": password,
    }
    
    print("🔐 Attempting login...")
    login_response = session.post(
        "https://api.binomo.com/passport/v2/sign_in?locale=en", 
        headers=login_headers, 
        json=login_payload, 
        timeout=30
    )
    
    print(f"Login status: {login_response.status_code}")
    print(f"Login cookies after: {session.cookies}")
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
        
    login_data = login_response.json()
    auth_token = login_data['data']['authtoken']
    print(f"✅ Login successful! Token: {auth_token}")
    
    # Immediate balance request (this works)
    print("\n💰 Testing immediate balance request...")
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
    
    balance_response = session.get(
        "https://api.binomo.com/bank/v1/read?locale=en",
        headers=balance_headers,
        timeout=30
    )
    
    print(f"Balance status: {balance_response.status_code}")
    if balance_response.status_code == 200:
        print(f"✅ SUCCESS! Balance data: {balance_response.json()}")
    else:
        print(f"❌ Failed: {balance_response.text[:200]}")
        
    # Wait a moment and try again
    print("\n⏰ Waiting 2 seconds and trying again...")
    import time
    time.sleep(2)
    
    balance_response2 = session.get(
        "https://api.binomo.com/bank/v1/read?locale=en",
        headers=balance_headers,
        timeout=30
    )
    
    print(f"Balance status (after wait): {balance_response2.status_code}")
    if balance_response2.status_code == 200:
        print(f"✅ SUCCESS! Balance data: {balance_response2.json()}")
    else:
        print(f"❌ Failed: {balance_response2.text[:200]}")

if __name__ == "__main__":
    test_login_and_balance()
