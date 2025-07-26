"""
WebSocket Connection Fix - Replicating Exact Browser Behavior
This attempts to fix the WebSocket by matching the exact browser handshake
"""

import asyncio
import websockets
import ssl
import base64
import hashlib
import os
import dotenv
from urllib.parse import urlparse
from BinomoAPI import BinomoAPI

dotenv.load_dotenv()

class FixedWebSocketConnection:
    """WebSocket connection that replicates exact browser behavior"""
    
    def __init__(self, auth_token=None, device_id=None):
        self.auth_token = auth_token
        self.device_id = device_id
        self.websocket = None
        self.connected = False
        
    async def connect_exact_browser_style(self):
        """Connect using exact browser WebSocket handshake"""
        
        # Exact URL from your curl (no auth parameters)
        uri = "wss://ws.binomo.com/?v=2&vsn=2.0.0"
        
        # Generate proper WebSocket key (browsers do this automatically)
        websocket_key = base64.b64encode(os.urandom(16)).decode('ascii')
        
        # Exact headers from your working curl
        headers = {
            "Host": "ws.binomo.com",
            "Upgrade": "websocket",
            "Connection": "Upgrade", 
            "Sec-WebSocket-Key": websocket_key,
            "Sec-WebSocket-Version": "13",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Origin": "https://binomo.com",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8,fr;q=0.7",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0"
        }
        
        print(f"🔗 Connecting to: {uri}")
        print(f"🔑 WebSocket Key: {websocket_key}")
        print(f"📋 Headers: {list(headers.keys())}")
        
        try:
            # Create SSL context that matches browsers
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Connect with exact browser parameters
            self.websocket = await websockets.connect(
                uri,
                extra_headers=headers,
                ssl=ssl_context,
                timeout=30,
                compression="deflate"  # Enable compression like browsers
            )
            
            self.connected = True
            print("🎉 WebSocket connected successfully!")
            
            # Start listening
            asyncio.create_task(self._listen())
            
            return True
            
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"❌ Connection failed with status: {e.status_code}")
            print(f"   Response headers: {dict(e.response_headers) if hasattr(e, 'response_headers') else 'None'}")
            return False
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    async def connect_with_session_cookies(self, session):
        """Try connecting with session cookies from successful login"""
        
        uri = "wss://ws.binomo.com/?v=2&vsn=2.0.0"
        
        # Extract cookies from successful session
        cookie_header = "; ".join([f"{cookie.name}={cookie.value}" for cookie in session.cookies])
        
        headers = {
            "Origin": "https://binomo.com",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8,fr;q=0.7",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Cookie": cookie_header
        }
        
        if self.auth_token:
            headers["authorization-token"] = self.auth_token
        if self.device_id:
            headers["device-id"] = str(self.device_id)
            
        print(f"🔗 Connecting with session cookies...")
        print(f"🍪 Cookies: {cookie_header[:100]}...")
        
        try:
            self.websocket = await websockets.connect(
                uri,
                extra_headers=headers,
                timeout=30
            )
            
            self.connected = True
            print("🎉 WebSocket connected with session cookies!")
            
            asyncio.create_task(self._listen())
            return True
            
        except Exception as e:
            print(f"❌ Session cookie connection failed: {e}")
            return False
    
    async def connect_phoenix_style(self):
        """Connect using Phoenix/Elixir WebSocket pattern"""
        
        # Phoenix WebSocket typically connects without auth, then authenticates via messages
        uri = "wss://ws.binomo.com/?v=2&vsn=2.0.0"
        
        headers = {
            "Origin": "https://binomo.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0"
        }
        
        print("🔗 Trying Phoenix-style connection...")
        
        try:
            self.websocket = await websockets.connect(uri, extra_headers=headers)
            self.connected = True
            print("✅ Phoenix connection established!")
            
            # Send Phoenix join message
            if self.auth_token:
                join_message = f'["1","1","__absinthe__:control","phx_join",{{"query":"subscription {{ auth(token: \\"{self.auth_token}\\") {{ success }} }}"}}]'
                await self.websocket.send(join_message)
                print("📤 Phoenix auth message sent")
            
            asyncio.create_task(self._listen())
            return True
            
        except Exception as e:
            print(f"❌ Phoenix connection failed: {e}")
            return False
    
    async def _listen(self):
        """Listen for WebSocket messages"""
        try:
            while self.connected and self.websocket:
                message = await self.websocket.recv()
                print(f"📥 Received: {message[:200]}...")
                
        except websockets.exceptions.ConnectionClosed:
            print("⚠️ WebSocket connection closed")
            self.connected = False
        except Exception as e:
            print(f"❌ Listen error: {e}")
            self.connected = False
    
    async def close(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False

async def test_websocket_fixes():
    """Test different WebSocket connection approaches"""
    
    print("🧪 Testing WebSocket Connection Fixes")
    print("=" * 60)
    
    # Get authentication from login
    print("🔐 Getting authentication...")
    login_response = BinomoAPI.login(os.getenv("email"), os.getenv("password"))
    session = login_response._session
    
    client = FixedWebSocketConnection(
        auth_token=login_response.authtoken,
        device_id=login_response.user_id
    )
    
    # Test 1: Exact browser-style connection
    print("\n📝 Test 1: Exact browser handshake...")
    success1 = await client.connect_exact_browser_style()
    
    if success1:
        print("✅ Browser-style connection works!")
        await asyncio.sleep(2)
        await client.close()
        return True
    
    # Test 2: Session cookies approach
    print("\n📝 Test 2: Session cookies approach...")
    success2 = await client.connect_with_session_cookies(session)
    
    if success2:
        print("✅ Session cookies connection works!")
        await asyncio.sleep(2)
        await client.close()
        return True
    
    # Test 3: Phoenix framework approach
    print("\n📝 Test 3: Phoenix framework approach...")
    success3 = await client.connect_phoenix_style()
    
    if success3:
        print("✅ Phoenix-style connection works!")
        await asyncio.sleep(2)
        await client.close()
        return True
    
    print("\n❌ All WebSocket approaches failed")
    return False

# Test specific WebSocket protocols
async def test_websocket_protocols():
    """Test different WebSocket protocols and subprotocols"""
    
    print("\n🧪 Testing WebSocket Protocols")
    print("=" * 40)
    
    login_response = BinomoAPI.login(os.getenv("email"), os.getenv("password"))
    
    # Different protocol attempts
    protocols_to_test = [
        ("Basic", "wss://ws.binomo.com/"),
        ("With version", "wss://ws.binomo.com/?v=2"),
        ("With version and vsn", "wss://ws.binomo.com/?v=2&vsn=2.0.0"),
        ("Phoenix channel", "wss://ws.binomo.com/socket/websocket"),
        ("Alternative port", "wss://ws.binomo.com:443/?v=2&vsn=2.0.0")
    ]
    
    for name, uri in protocols_to_test:
        print(f"🔗 Testing {name}: {uri}")
        
        try:
            headers = {
                "Origin": "https://binomo.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            websocket = await websockets.connect(uri, extra_headers=headers, timeout=10)
            print(f"✅ {name} connected successfully!")
            await websocket.close()
            return uri
            
        except Exception as e:
            print(f"❌ {name} failed: {str(e)[:50]}...")
    
    return None

async def main():
    """Run all WebSocket fix tests"""
    
    # Test connection fixes
    websocket_fixed = await test_websocket_fixes()
    
    if not websocket_fixed:
        # Test different protocols
        working_protocol = await test_websocket_protocols()
        
        if working_protocol:
            print(f"\n🎯 Found working protocol: {working_protocol}")
        else:
            print("\n🔍 No working WebSocket protocol found")
            print("This confirms server-side restrictions are in place")
    
    print("\n📋 WebSocket Fix Summary:")
    print("=" * 40)
    if websocket_fixed:
        print("🎉 SUCCESS: WebSocket connection fixed!")
        print("✅ Ready to integrate fix into BinomoAPI")
    else:
        print("⚠️ WebSocket still blocked by server")
        print("💡 Consider alternative approaches:")
        print("   1. Browser automation (selenium)")
        print("   2. Mock trading system for development")
        print("   3. Use API for account management only")

if __name__ == "__main__":
    asyncio.run(main())
