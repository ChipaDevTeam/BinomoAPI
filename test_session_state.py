#!/usr/bin/env python3
"""
Test session state after API initialization
"""

import os
import asyncio
from dotenv import load_dotenv
from BinomoAPI import BinomoAPI

load_dotenv()

email = os.getenv("email")
password = os.getenv("password")

async def test_session_after_api():
    """Test if session works immediately after API initialization"""
    
    # Step 1: Login
    login_response = BinomoAPI.login(email, password)
    print(f"Login Token: {login_response.authtoken}")
    
    # Step 2: Create API
    api = BinomoAPI.create_from_login(
        login_response=login_response,
        device_id=login_response.user_id,
        demo=True,
        enable_logging=False
    )
    print("API initialized")
    
    # Step 3: Test direct session call
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'authorization-token': login_response.authtoken,
        'cache-control': 'no-cache',
        'cookie': f'authtoken={login_response.authtoken}; device_type=web; device_id={login_response.user_id}',
        'device-id': login_response.user_id,
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
    
    print("\n=== Testing API session directly ===")
    resp = api._session.get("https://api.binomo.com/bank/v1/read?locale=en", headers=headers, timeout=30)
    print(f"Direct API session call: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ SUCCESS!")
    else:
        print(f"❌ FAILED: {resp.text[:100]}")
    
    print("\n=== Testing API get_balance method ===")
    try:
        balance = await api.get_balance("demo")
        print(f"✅ get_balance SUCCESS: ${balance.amount:.2f}")
    except Exception as e:
        print(f"❌ get_balance FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_session_after_api())
