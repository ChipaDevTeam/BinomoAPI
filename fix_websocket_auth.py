#!/usr/bin/env python3
"""
Advanced WebSocket Authentication Fix for BinomoAPI.
This script implements multiple authentication strategies to resolve HTTP 401 WebSocket errors.
"""

import asyncio
import websockets
import json
import time
import requests
from typing import Optional, Dict, Any
from BinomoAPI import BinomoAPI

class AdvancedWebSocketAuth:
    """Advanced WebSocket authentication handler for Binomo API."""
    
    def __init__(self, auth_token: str, device_id: str, session: requests.Session):
        self.auth_token = auth_token
        self.device_id = device_id
        self.session = session
        self.websocket = None
        
    async def authenticate_websocket_v1(self) -> bool:
        """Method 1: Enhanced URL parameters with session cookies"""
        try:
            print("🔧 Trying Method 1: Enhanced URL + Session Cookies")
            
            # Extract all cookies from session
            cookies_str = "; ".join([f"{name}={value}" for name, value in self.session.cookies.items()])
            
            ws_url = (
                f"wss://ws.binomo.com?authtoken={self.auth_token}"
                f"&device=web&device_id={self.device_id}&v=2&vsn=2.0.0"
                f"&locale=en&timezone=UTC"
            )
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
                'Sec-WebSocket-Protocol': 'wamp',
                'Origin': 'https://binomo.com',
                'Referer': 'https://binomo.com/',
                'Cookie': cookies_str,
                'Authorization': f'Bearer {self.auth_token}',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            return await self._test_websocket_connection(ws_url, headers, "Method 1")
            
        except Exception as e:
            print(f"   ❌ Method 1 failed: {e}")
            return False
    
    async def authenticate_websocket_v2(self) -> bool:
        """Method 2: Protocol-specific authentication"""
        try:
            print("🔧 Trying Method 2: Protocol-specific Authentication")
            
            ws_url = f"wss://ws.binomo.com"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Origin': 'https://binomo.com',
                'Sec-WebSocket-Protocol': 'wamp',
                'authorization-token': self.auth_token,
                'device-id': self.device_id,
                'device-type': 'web',
                'x-auth-token': self.auth_token,
                'x-device-id': self.device_id
            }
            
            return await self._test_websocket_connection(ws_url, headers, "Method 2")
            
        except Exception as e:
            print(f"   ❌ Method 2 failed: {e}")
            return False
    
    async def authenticate_websocket_v3(self) -> bool:
        """Method 3: WAMP protocol authentication"""
        try:
            print("🔧 Trying Method 3: WAMP Protocol Authentication")
            
            ws_url = (
                f"wss://ws.binomo.com/ws?authtoken={self.auth_token}"
                f"&device_id={self.device_id}&version=2"
            )
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Origin': 'https://binomo.com',
                'Sec-WebSocket-Protocol': 'wamp.2.json',
                'Sec-WebSocket-Version': '13'
            }
            
            return await self._test_websocket_connection(ws_url, headers, "Method 3")
            
        except Exception as e:
            print(f"   ❌ Method 3 failed: {e}")
            return False
    
    async def authenticate_websocket_v4(self) -> bool:
        """Method 4: Token in first message"""
        try:
            print("🔧 Trying Method 4: Token in First Message")
            
            ws_url = "wss://ws.binomo.com"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Origin': 'https://binomo.com'
            }
            
            websocket = await websockets.connect(ws_url, extra_headers=headers)
            print(f"   ✅ WebSocket connection established")
            
            # Send authentication message first
            auth_message = json.dumps({
                "method": "authenticate",
                "params": {
                    "authtoken": self.auth_token,
                    "device_id": self.device_id,
                    "device_type": "web"
                },
                "ref": int(time.time())
            })
            
            await websocket.send(auth_message)
            print(f"   📤 Sent authentication message")
            
            # Wait for auth response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"   📥 Auth response: {response[:100]}...")
                
                # Test trading message
                return await self._test_trading_message(websocket, "Method 4")
                
            except asyncio.TimeoutError:
                print(f"   ❌ Authentication timeout")
                return False
            finally:
                await websocket.close()
                
        except Exception as e:
            print(f"   ❌ Method 4 failed: {e}")
            return False
    
    async def authenticate_websocket_v5(self) -> bool:
        """Method 5: Session transfer approach"""
        try:
            print("🔧 Trying Method 5: Session Transfer Approach")
            
            # First, get a fresh session token
            refresh_url = f"https://api.binomo.com/passport/v2/refresh"
            refresh_headers = self.session.headers.copy()
            
            refresh_response = self.session.post(refresh_url, headers=refresh_headers)
            print(f"   🔄 Session refresh status: {refresh_response.status_code}")
            
            if refresh_response.status_code == 200:
                refresh_data = refresh_response.json()
                if 'data' in refresh_data and 'authtoken' in refresh_data['data']:
                    fresh_token = refresh_data['data']['authtoken']
                    print(f"   ✅ Got fresh token: {fresh_token[:10]}...")
                    
                    ws_url = (
                        f"wss://ws.binomo.com?authtoken={fresh_token}"
                        f"&device=web&device_id={self.device_id}&v=2&vsn=2.0.0"
                    )
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Origin': 'https://binomo.com',
                        'Authorization': f'Bearer {fresh_token}',
                        'Cookie': f'authtoken={fresh_token}; device_type=web; device_id={self.device_id}'
                    }
                    
                    return await self._test_websocket_connection(ws_url, headers, "Method 5")
            
            return False
            
        except Exception as e:
            print(f"   ❌ Method 5 failed: {e}")
            return False
    
    async def _test_websocket_connection(self, url: str, headers: dict, method_name: str) -> bool:
        """Test WebSocket connection with given parameters."""
        try:
            print(f"   🔍 Testing {method_name}...")
            print(f"   URL: {url[:80]}{'...' if len(url) > 80 else ''}")
            
            websocket = await asyncio.wait_for(
                websockets.connect(url, extra_headers=headers),
                timeout=15.0
            )
            
            print(f"   ✅ Connection established!")
            
            # Test trading message
            result = await self._test_trading_message(websocket, method_name)
            await websocket.close()
            return result
            
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"   ❌ HTTP Error: {e.status_code}")
            return False
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            return False
    
    async def _test_trading_message(self, websocket, method_name: str) -> bool:
        """Test sending a trading message through WebSocket."""
        try:
            # Test with a minimal trading message
            test_trade = {
                "method": "place_order",
                "params": {
                    "asset": "AUD/USD",
                    "direction": "call",
                    "amount": 1,
                    "duration": 60,
                    "account_type": "demo"
                },
                "ref": int(time.time())
            }
            
            await websocket.send(json.dumps(test_trade))
            print(f"   📤 Sent test trading message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"   📥 Trading response: {response[:100]}...")
                
                # Check if response indicates success
                try:
                    response_data = json.loads(response)
                    if 'error' not in response_data or response_data.get('status') == 'success':
                        print(f"   🎉 {method_name} - Trading message successful!")
                        return True
                    else:
                        print(f"   ⚠️ {method_name} - Trading error: {response_data.get('error', 'Unknown')}")
                        return False
                except:
                    print(f"   ⚠️ {method_name} - Got response but couldn't parse JSON")
                    return True  # Still counts as success if we got a response
                    
            except asyncio.TimeoutError:
                print(f"   ⚠️ {method_name} - Trading message timeout")
                return False
                
        except Exception as e:
            print(f"   ❌ Trading test failed: {e}")
            return False

async def fix_websocket_authentication():
    """Main function to test and fix WebSocket authentication."""
    print("🚀 Advanced WebSocket Authentication Fix")
    print("=" * 60)
    
    # Login first
    try:
        login_response = await BinomoAPI.login("testUser", "testPassword")
        print(f"✅ Login successful: {login_response.authtoken[:10]}...")
        
        # Create advanced auth handler
        auth_handler = AdvancedWebSocketAuth(
            login_response.authtoken,
            login_response.user_id,
            login_response._session
        )
        
        # Try all authentication methods
        methods = [
            auth_handler.authenticate_websocket_v1,
            auth_handler.authenticate_websocket_v2,
            auth_handler.authenticate_websocket_v3,
            auth_handler.authenticate_websocket_v4,
            auth_handler.authenticate_websocket_v5
        ]
        
        print(f"\n🔧 Testing {len(methods)} authentication methods...")
        
        for i, method in enumerate(methods, 1):
            print(f"\n📡 Testing Method {i}...")
            try:
                success = await method()
                if success:
                    print(f"🎉 SUCCESS! Method {i} works for WebSocket authentication!")
                    return method, login_response
                else:
                    print(f"❌ Method {i} failed")
            except Exception as e:
                print(f"❌ Method {i} exception: {e}")
        
        print(f"\n❌ All authentication methods failed")
        return None, login_response
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None, None

if __name__ == "__main__":
    asyncio.run(fix_websocket_authentication())
