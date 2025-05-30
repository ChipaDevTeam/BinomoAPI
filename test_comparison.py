#!/usr/bin/env python3
"""
Test to isolate the exact difference between working minimal test and BinomoAPI class
"""

import os
import asyncio
import requests
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("email")
password = os.getenv("password")
device_id = "174353421"

def working_approach():
    """The approach that works from our minimal test"""
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
    
    auth_token = response.json()['data']['authtoken']
    print(f"✅ Login Token: {auth_token}")
    
    # Step 2: Balance request  
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
    
    balance_response = session.get("https://api.binomo.com/bank/v1/read?locale=en", 
                                  headers=balance_headers, timeout=30)
    
    print(f"Working approach: {balance_response.status_code}")
    return auth_token

class SimpleBinomoAPI:
    """Minimal BinomoAPI implementation to isolate the issue"""
    
    def __init__(self, auth_token: str, device_id: str):
        self._auth_token = auth_token
        self._device_id = device_id
        self._session = requests.Session()
        print(f"SimpleBinomoAPI initialized with token: {auth_token[:8]}...")
    
    def get_balance_sync(self):
        """Synchronous version to eliminate async complexity"""
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'authorization-token': self._auth_token,
            'cache-control': 'no-cache',
            'cookie': f'authtoken={self._auth_token}; device_type=web; device_id={self._device_id}',
            'device-id': self._device_id,
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
        
        response = self._session.get("https://api.binomo.com/bank/v1/read?locale=en", 
                                   headers=headers, timeout=30)
        
        print(f"SimpleBinomoAPI response: {response.status_code}")
        return response

def test_comparison():
    print("=== Working approach ===")
    auth_token = working_approach()
    
    print("\n=== SimpleBinomoAPI approach ===")
    simple_api = SimpleBinomoAPI(auth_token, device_id)
    simple_api.get_balance_sync()

if __name__ == "__main__":
    test_comparison()
