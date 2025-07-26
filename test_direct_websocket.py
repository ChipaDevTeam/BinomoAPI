"""
Direct WebSocket test using the exact working session from login
This attempts to use the session state that successfully retrieves balance
"""

import asyncio
import websockets
import os
import dotenv
import json
from BinomoAPI import BinomoAPI

dotenv.load_dotenv()

async def test_direct_websocket_with_working_session():
    """Test WebSocket using the exact session state that works for balance"""
    
    print("🧪 Direct WebSocket Test with Working Session")
    print("=" * 60)
    
    # Step 1: Get working session from login
    print("🔐 Step 1: Getting working session from login...")
    login_response = BinomoAPI.login(os.getenv("email"), os.getenv("password"))
    print(f"✅ Login successful! Token: {login_response.authtoken[:20]}...")
    
    # Extract the working session details
    working_session = login_response._session
    working_cookies = dict(working_session.cookies)
    working_headers = dict(working_session.headers)
    
    print(f"📋 Working session cookies: {working_cookies}")
    print(f"📋 Working session headers: {list(working_headers.keys())}")
    
    # Step 2: Test WebSocket with exact session parameters
    print("\n🌐 Step 2: Testing WebSocket with exact session parameters...")
    
    # Build WebSocket URL with auth parameters
    ws_url = f"wss://ws.binomo.com/?v=2&vsn=2.0.0&authtoken={login_response.authtoken}&device_id={login_response.user_id}"
    
    # Build headers combining curl headers + session headers  
    ws_headers = {
        "Origin": "https://binomo.com",
        "Cache-Control": "no-cache",
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8,fr;q=0.7",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
        "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
        # Add session authentication headers
        "authorization-token": login_response.authtoken,
        "device-id": str(login_response.user_id),
        "device-type": "web",
        # Add cookies as header
        "Cookie": f"authtoken={login_response.authtoken}; device_type=web; device_id={login_response.user_id}"
    }
    
    print(f"🔗 WebSocket URL: {ws_url[:80]}...")
    print(f"🔑 WebSocket headers: {list(ws_headers.keys())}")
    
    try:
        print("\n🚀 Attempting WebSocket connection...")
        
        # Try connecting with all the session details
        websocket = await websockets.connect(
            ws_url,
            extra_headers=ws_headers,
            timeout=30
        )
        
        print("🎉 SUCCESS! WebSocket connected!")
        print("✅ The exact session parameters worked!")
        
        # Test sending a message
        print("\n📤 Testing message sending...")
        
        # Try Phoenix/Elixir channel join
        auth_message = {
            "topic": "auth",
            "event": "phx_join",
            "payload": {
                "token": login_response.authtoken,
                "device_id": str(login_response.user_id)
            },
            "ref": "1"
        }
        
        await websocket.send(json.dumps(auth_message))
        print("✅ Authentication message sent")
        
        # Try to receive response
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 Received response: {response}")
            
            # Try trading message
            print("\n📈 Testing trade message...")
            trade_message = {
                "topic": "trading",
                "event": "place_trade",
                "payload": {
                    "asset": "EUR/USD",
                    "direction": "call",
                    "amount": 1.0,
                    "duration": 60
                },
                "ref": "2"
            }
            
            await websocket.send(json.dumps(trade_message))
            print("✅ Trade message sent")
            
            # Try to get trade response
            try:
                trade_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📈 Trade response: {trade_response}")
                print("🎯 COMPLETE SUCCESS! Trading via WebSocket works!")
                
            except asyncio.TimeoutError:
                print("⏰ No trade response (may need different message format)")
                
        except asyncio.TimeoutError:
            print("⏰ No auth response (but connection successful)")
            
        await websocket.close()
        print("✅ WebSocket closed cleanly")
        
        return True
        
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket connection failed with status {e.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

# Alternative test with minimal parameters
async def test_minimal_websocket():
    """Test with minimal WebSocket parameters to isolate the issue"""
    
    print("\n🧪 Minimal WebSocket Test")
    print("=" * 40)
    
    # Get fresh login
    login_response = BinomoAPI.login(os.getenv("email"), os.getenv("password"))
    
    # Try the absolute minimal WebSocket connection
    minimal_url = "wss://ws.binomo.com/"
    minimal_headers = {
        "Origin": "https://binomo.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"🔗 Trying minimal URL: {minimal_url}")
    
    try:
        websocket = await websockets.connect(
            minimal_url,
            extra_headers=minimal_headers,
            timeout=10
        )
        print("✅ Minimal WebSocket connected!")
        await websocket.close()
        return True
        
    except Exception as e:
        print(f"❌ Minimal connection failed: {e}")
        return False

async def main():
    """Run all WebSocket tests"""
    
    # Test 1: Direct WebSocket with working session
    success1 = await test_direct_websocket_with_working_session()
    
    # Test 2: Minimal WebSocket
    success2 = await test_minimal_websocket()
    
    print("\n📊 Test Results:")
    print(f"   Direct WebSocket: {'✅ SUCCESS' if success1 else '❌ FAILED'}")
    print(f"   Minimal WebSocket: {'✅ SUCCESS' if success2 else '❌ FAILED'}")
    
    if success1:
        print("\n🎯 SOLUTION FOUND!")
        print("✅ WebSocket works with exact session parameters")
        print("✅ Ready to integrate into BinomoAPI")
    else:
        print("\n🔍 DIAGNOSIS:")
        print("❌ WebSocket authentication still blocked")
        print("💡 May require browser-level authentication")

if __name__ == "__main__":
    asyncio.run(main())
