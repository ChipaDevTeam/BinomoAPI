#!/usr/bin/env python3
"""
Debug WebSocket authentication for Binomo API.
This script tests WebSocket connections with different authentication approaches.
"""

import asyncio
import websockets
import json
import time
from BinomoAPI import BinomoAPI

async def test_websocket_connection():
    """Test WebSocket connection with different authentication methods."""
    
    print("🔧 Testing WebSocket Authentication Methods...")
    
    # First, login and get valid credentials
    try:
        # Login to get auth token
        login_response = await BinomoAPI.login("testUser", "testPassword")
        if not login_response:
            print("❌ Login failed")
            return
            
        # Create API instance from login response
        api = BinomoAPI.create_from_login(login_response, enable_logging=True)
        print(f"✅ Login successful: {login_response.authtoken[:10]}...")
        
        # Test Method 1: URL Parameters (current approach)
        print("\n📡 Method 1: URL Parameters Authentication")
        ws_url_1 = (
            f"wss://ws.binomo.com?authtoken={login_response.authtoken}"
            f"&device=web&device_id={api._device_id}&v=2&vsn=2.0.0"
        )
        
        await test_websocket_url(ws_url_1, {}, "URL Parameters")
        
        # Test Method 2: Headers Only
        print("\n📡 Method 2: Headers Only Authentication")
        ws_url_2 = "wss://ws.binomo.com"
        headers_2 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Origin': 'https://binomo.com',
            'Authorization': f'Bearer {login_response.authtoken}',
            'Cookie': f'authtoken={login_response.authtoken}; device_type=web; device_id={api._device_id}',
            'authorization-token': login_response.authtoken,
            'device-id': api._device_id,
            'device-type': 'web'
        }
        
        await test_websocket_url(ws_url_2, headers_2, "Headers Only")
        
        # Test Method 3: Minimal URL + Minimal Headers
        print("\n📡 Method 3: Minimal Authentication")
        ws_url_3 = f"wss://ws.binomo.com?authtoken={login_response.authtoken}"
        headers_3 = {
            'Origin': 'https://binomo.com'
        }
        
        await test_websocket_url(ws_url_3, headers_3, "Minimal")
        
        # Test Method 4: Different WebSocket endpoint
        print("\n📡 Method 4: Alternative Endpoint")
        ws_url_4 = f"wss://api.binomo.com/ws?authtoken={login_response.authtoken}"
        headers_4 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': 'https://binomo.com'
        }
        
        await test_websocket_url(ws_url_4, headers_4, "Alternative Endpoint")
        
        # Test Method 5: Browser-like approach
        print("\n📡 Method 5: Browser-like Authentication")
        ws_url_5 = (
            f"wss://ws.binomo.com?authtoken={login_response.authtoken}"
            f"&device=web&device_id={api._device_id}&v=2&vsn=2.0.0"
        )
        headers_5 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            'Sec-WebSocket-Version': '13',
            'Origin': 'https://binomo.com',
            'Referer': 'https://binomo.com/'
        }
        
        await test_websocket_url(ws_url_5, headers_5, "Browser-like")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")

async def test_websocket_url(url: str, headers: dict, method_name: str):
    """Test a specific WebSocket URL and headers combination."""
    
    try:
        print(f"   🔍 Testing {method_name}...")
        print(f"   URL: {url[:100]}{'...' if len(url) > 100 else ''}")
        print(f"   Headers: {len(headers)} items")
        
        # Attempt connection with timeout
        try:
            websocket = await asyncio.wait_for(
                websockets.connect(url, extra_headers=headers),
                timeout=10.0
            )
            
            print(f"   ✅ Connection established!")
            
            # Try sending a simple ping message
            test_message = json.dumps({
                "method": "ping",
                "params": {},
                "ref": int(time.time())
            })
            
            await websocket.send(test_message)
            print(f"   📤 Sent ping message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"   📥 Received: {response[:100]}...")
                
                # Try sending a more complex message
                subscribe_message = json.dumps({
                    "method": "subscribe",
                    "params": {
                        "channels": ["balance", "user_info"]
                    },
                    "ref": int(time.time()) + 1
                })
                
                await websocket.send(subscribe_message)
                print(f"   📤 Sent subscribe message")
                
                # Wait for subscription response
                try:
                    response2 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"   📥 Subscribe response: {response2[:100]}...")
                    print(f"   🎉 {method_name} method appears to work!")
                    
                except asyncio.TimeoutError:
                    print(f"   ⚠️  Subscribe timeout - connection may be limited")
                    
            except asyncio.TimeoutError:
                print(f"   ⚠️  Ping timeout - no response received")
            
            await websocket.close()
            
        except asyncio.TimeoutError:
            print(f"   ❌ Connection timeout")
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"   ❌ HTTP Error: {e.status_code}")
            if hasattr(e, 'headers'):
                print(f"   📋 Response headers: {dict(e.headers)}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"   ❌ Connection closed: {e.code} {e.reason}")
        
    except Exception as e:
        print(f"   ❌ {method_name} failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
