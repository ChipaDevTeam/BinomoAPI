#!/usr/bin/env python3
"""
Debug session transfer issue
"""

import os
import requests
from dotenv import load_dotenv
from BinomoAPI import BinomoAPI

load_dotenv()

email = os.getenv("email")
password = os.getenv("password")
device_id = "174353421"

def test_session_transfer():
    """Test what happens to the session when transferred"""
    
    print("=== STEP 1: Login and get session ===")
    login_response = BinomoAPI.login(email, password, device_id)
    session = login_response._session
    auth_token = login_response.authtoken
    
    print(f"Session ID after login: {id(session)}")
    print(f"Session cookies after login: {session.cookies}")
    
    print("\n=== STEP 2: Test direct balance call with original session ===")
    headers = {
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
    
    response = session.get("https://api.binomo.com/bank/v1/read?locale=en", headers=headers, timeout=30)
    print(f"Direct session call status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ SUCCESS! Balance data: {response.json()}")
    else:
        print(f"❌ Failed: {response.text[:200]}")
    
    print(f"\nSession ID before creating API: {id(session)}")
    print(f"Session cookies before creating API: {session.cookies}")
    
    print("\n=== STEP 3: Create API instance and check session ===")
    api = BinomoAPI(
        auth_token=auth_token,
        device_id=device_id,
        demo=True,
        enable_logging=True,
        login_session=session
    )
    
    print(f"Session ID after creating API: {id(api._session)}")
    print(f"Session cookies after creating API: {api._session.cookies}")
    
    print("\n=== STEP 4: Test if sessions are the same object ===")
    print(f"Sessions are same object: {session is api._session}")
    print(f"Session cookies are same: {session.cookies is api._session.cookies}")

if __name__ == "__main__":
    test_session_transfer()
