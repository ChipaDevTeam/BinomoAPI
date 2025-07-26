import asyncio
import websockets
import logging
import json
import time
import requests
from typing import Optional, Dict, Any, Callable

class EnhancedWebSocketClient:
    """Enhanced WebSocket client with multiple authentication strategies for Binomo API."""
    
    def __init__(self, auth_token: str, device_id: str, session: Optional[requests.Session] = None):
        self.auth_token = auth_token
        self.device_id = device_id
        self.session = session
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._connected = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Authentication strategies to try
        self.auth_strategies = [
            self._auth_strategy_session_cookies,
            self._auth_strategy_wamp_protocol,
            self._auth_strategy_post_connect_auth,
            self._auth_strategy_fresh_token,
            self._auth_strategy_alternative_endpoint
        ]
        
    async def connect_with_fallback(self) -> bool:
        """Try multiple authentication strategies until one works."""
        self.logger.info("Attempting WebSocket connection with authentication fallback...")
        
        for i, strategy in enumerate(self.auth_strategies, 1):
            try:
                self.logger.info(f"Trying authentication strategy {i}/{len(self.auth_strategies)}")
                if await strategy():
                    self.logger.info(f"✅ Authentication strategy {i} successful!")
                    return True
                else:
                    self.logger.warning(f"❌ Authentication strategy {i} failed")
            except Exception as e:
                self.logger.error(f"❌ Authentication strategy {i} exception: {e}")
        
        self.logger.error("❌ All authentication strategies failed")
        return False
    
    async def _auth_strategy_session_cookies(self) -> bool:
        """Strategy 1: Use session cookies and enhanced headers."""
        try:
            self.logger.info("🔧 Strategy 1: Session cookies + enhanced headers")
            
            # Build comprehensive cookie string from session
            cookies_str = ""
            if self.session and self.session.cookies:
                cookies_str = "; ".join([f"{name}={value}" for name, value in self.session.cookies.items()])
            
            # Enhanced URL with all parameters
            ws_url = (
                f"wss://ws.binomo.com?authtoken={self.auth_token}"
                f"&device=web&device_id={self.device_id}&v=2&vsn=2.0.0"
                f"&locale=en&timezone=UTC&platform=web"
            )
            
            # Comprehensive headers matching browser behavior
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
                'Sec-WebSocket-Version': '13',
                'Origin': 'https://binomo.com',
                'Referer': 'https://binomo.com/',
                'Authorization': f'Bearer {self.auth_token}',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Add cookies if available
            if cookies_str:
                headers['Cookie'] = cookies_str
            
            # Add session headers if available
            if self.session and self.session.headers:
                for key, value in self.session.headers.items():
                    if key.lower() in ['authorization-token', 'device-id', 'device-type']:
                        headers[key] = value
            
            return await self._test_connection(ws_url, headers, "Session Cookies")
            
        except Exception as e:
            self.logger.error(f"Strategy 1 failed: {e}")
            return False
    
    async def _auth_strategy_wamp_protocol(self) -> bool:
        """Strategy 2: WAMP protocol with specific authentication."""
        try:
            self.logger.info("🔧 Strategy 2: WAMP protocol authentication")
            
            ws_url = f"wss://ws.binomo.com"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Origin': 'https://binomo.com',
                'Sec-WebSocket-Protocol': 'wamp.2.json',
                'Sec-WebSocket-Version': '13',
                'authorization-token': self.auth_token,
                'device-id': self.device_id,
                'device-type': 'web'
            }
            
            return await self._test_connection(ws_url, headers, "WAMP Protocol")
            
        except Exception as e:
            self.logger.error(f"Strategy 2 failed: {e}")
            return False
    
    async def _auth_strategy_post_connect_auth(self) -> bool:
        """Strategy 3: Connect first, authenticate after."""
        try:
            self.logger.info("🔧 Strategy 3: Post-connection authentication")
            
            ws_url = "wss://ws.binomo.com"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Origin': 'https://binomo.com'
            }
            
            # Connect without authentication
            websocket = await asyncio.wait_for(
                websockets.connect(ws_url, extra_headers=headers),
                timeout=10.0
            )
            
            self.logger.info("✅ WebSocket connected, sending authentication...")
            
            # Send authentication message
            auth_message = {
                "method": "authenticate",
                "params": {
                    "authtoken": self.auth_token,
                    "device_id": self.device_id,
                    "device_type": "web",
                    "version": "2.0.0"
                },
                "ref": int(time.time())
            }
            
            await websocket.send(json.dumps(auth_message))
            self.logger.info("📤 Authentication message sent")
            
            # Wait for authentication response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                self.logger.info(f"📥 Auth response: {response[:100]}...")
                
                # Store successful connection
                self.websocket = websocket
                self._connected = True
                
                # Start background listening
                asyncio.create_task(self._listen())
                
                return True
                
            except asyncio.TimeoutError:
                self.logger.warning("Authentication timeout")
                await websocket.close()
                return False
                
        except Exception as e:
            self.logger.error(f"Strategy 3 failed: {e}")
            return False
    
    async def _auth_strategy_fresh_token(self) -> bool:
        """Strategy 4: Get fresh token and retry."""
        try:
            self.logger.info("🔧 Strategy 4: Fresh token authentication")
            
            if not self.session:
                return False
                
            # Try to refresh the token
            refresh_url = "https://api.binomo.com/passport/v2/refresh"
            refresh_headers = {
                'authorization-token': self.auth_token,
                'device-id': self.device_id,
                'device-type': 'web',
                'Content-Type': 'application/json'
            }
            
            try:
                response = self.session.post(refresh_url, headers=refresh_headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'authtoken' in data['data']:
                        fresh_token = data['data']['authtoken']
                        self.logger.info(f"✅ Got fresh token: {fresh_token[:10]}...")
                        
                        # Try connection with fresh token
                        ws_url = (
                            f"wss://ws.binomo.com?authtoken={fresh_token}"
                            f"&device=web&device_id={self.device_id}&v=2&vsn=2.0.0"
                        )
                        
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Origin': 'https://binomo.com',
                            'Authorization': f'Bearer {fresh_token}'
                        }
                        
                        return await self._test_connection(ws_url, headers, "Fresh Token")
            except:
                pass
                
            return False
            
        except Exception as e:
            self.logger.error(f"Strategy 4 failed: {e}")
            return False
    
    async def _auth_strategy_alternative_endpoint(self) -> bool:
        """Strategy 5: Try alternative WebSocket endpoints."""
        try:
            self.logger.info("🔧 Strategy 5: Alternative endpoints")
            
            endpoints = [
                f"wss://api.binomo.com/ws?authtoken={self.auth_token}",
                f"wss://ws.api.binomo.com?authtoken={self.auth_token}",
                f"wss://trading.binomo.com/ws?authtoken={self.auth_token}"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Origin': 'https://binomo.com',
                'Authorization': f'Bearer {self.auth_token}'
            }
            
            for endpoint in endpoints:
                try:
                    self.logger.info(f"Trying endpoint: {endpoint[:50]}...")
                    if await self._test_connection(endpoint, headers, f"Alt Endpoint"):
                        return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Strategy 5 failed: {e}")
            return False
    
    async def _test_connection(self, url: str, headers: dict, strategy_name: str) -> bool:
        """Test WebSocket connection with given parameters."""
        try:
            self.logger.info(f"Testing {strategy_name}: {url[:60]}...")
            
            websocket = await asyncio.wait_for(
                websockets.connect(url, extra_headers=headers),
                timeout=15.0
            )
            
            self.logger.info(f"✅ {strategy_name} connection established!")
            
            # Store successful connection
            self.websocket = websocket
            self._connected = True
            
            # Start background listening
            asyncio.create_task(self._listen())
            
            return True
            
        except websockets.exceptions.InvalidStatusCode as e:
            self.logger.warning(f"❌ {strategy_name} HTTP error: {e.status_code}")
            return False
        except Exception as e:
            self.logger.warning(f"❌ {strategy_name} failed: {e}")
            return False
    
    async def _listen(self):
        """Listen for incoming messages."""
        try:
            if not self.websocket:
                return
                
            async for message in self.websocket:
                self.logger.debug(f"Received: {message}")
                # Handle messages here
                
        except websockets.exceptions.ConnectionClosed:
            self._connected = False
            self.logger.warning("WebSocket connection closed")
        except Exception as e:
            self._connected = False
            self.logger.error(f"Listening error: {e}")
    
    async def send(self, message: str):
        """Send message through WebSocket."""
        if not self._connected or not self.websocket:
            # Try to connect using fallback strategies
            if not await self.connect_with_fallback():
                raise ConnectionError("Failed to establish WebSocket connection")
        
        try:
            await self.websocket.send(message)
            self.logger.debug(f"Sent: {message}")
        except websockets.exceptions.ConnectionClosed:
            self._connected = False
            self.logger.warning("WebSocket connection closed during send")
            raise
        except Exception as e:
            self.logger.error(f"Send error: {e}")
            raise
    
    async def close(self):
        """Close WebSocket connection."""
        if self.websocket:
            try:
                await self.websocket.close()
                self._connected = False
                self.logger.info("WebSocket connection closed")
            except Exception as e:
                self.logger.error(f"Error closing WebSocket: {e}")
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._connected and self.websocket is not None
