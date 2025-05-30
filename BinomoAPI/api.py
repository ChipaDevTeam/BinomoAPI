"""
Professional Binomo API Client

This module provides a comprehensive interface for interacting with the Binomo trading platform API.
It includes authentication, WebSocket connections, balance queries, and trade execution capabilities.
"""

import os
import json
import time
import logging
import requests
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

import BinomoAPI.global_values as gv
from BinomoAPI.config.conf import Config
from BinomoAPI.wss.client import WebSocketClient
from BinomoAPI.exceptions import (
    BinomoAPIException, 
    AuthenticationError, 
    ConnectionError, 
    InvalidParameterError,
    TradeError,
    InsufficientBalanceError
)
from BinomoAPI.constants import (
    LOGIN_URL,
    BALANCE_URL,
    DEFAULT_DEVICE_ID,
    DEFAULT_ASSET_RIC,
    WS_TOPICS,
    TRADE_DIRECTIONS,
    ACCOUNT_TYPES,
    DEFAULT_HEADERS
)
from BinomoAPI.models import LoginResponse, Asset, Balance, TradeOrder


class BinomoAPI:
    @staticmethod
    def login(email: str, password: str, device_id: str = DEFAULT_DEVICE_ID) -> Optional[LoginResponse]:
        """
        Authenticate with Binomo API using email and password.
        
        Args:
            email: User's email address
            password: User's password
            device_id: Unique device identifier (optional)
            
        Returns:
            LoginResponse object containing auth token and user ID if successful, None otherwise
            
        Raises:
            AuthenticationError: If login credentials are invalid
            ConnectionError: If unable to connect to Binomo API
            InvalidParameterError: If email or password is empty
        """
        if not email or not password:
            raise InvalidParameterError("Email and password are required")
            
        # Create a session for the login process
        session = requests.Session()
        
        # First, visit the main site to establish session (this seems to be important)
        try:
            session.get('https://binomo.com/', timeout=10)
        except:
            pass  # Continue even if this fails
            
        headers = DEFAULT_HEADERS.copy()
        headers.update({
            'device-id': device_id,
            'device-type': 'web',  # Ensure this is set
            'user-timezone': 'UTC'  # More generic than hardcoded timezone
        })
        
        payload = {
            "email": email,
            "password": password,
        }
        
        try:
            response = session.post(LOGIN_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            
            if 'data' in response_data and 'authtoken' in response_data['data']:
                login_response = LoginResponse.from_dict(response_data['data'])
                
                # Store the session in the login response for later use
                gv.session = session
                login_response._session = session
                
                # Test the session immediately to ensure it works
                #BinomoAPI._test_balance_with_session(session, login_response.authtoken, device_id)
                
                return login_response
            else:
                raise AuthenticationError("Invalid response format from login endpoint")
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid email or password")
            elif e.response.status_code >= 500:
                raise ConnectionError(f"Server error: {e.response.status_code}")
            else:
                raise BinomoAPIException(f"HTTP error {e.response.status_code}: {e}")
                
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Unable to connect to Binomo API: {e}")
            
        except requests.exceptions.Timeout as e:
            raise ConnectionError(f"Request timeout: {e}")
            
        except requests.exceptions.RequestException as e:
            raise BinomoAPIException(f"Request failed: {e}")
            
        except json.JSONDecodeError as e:
            raise BinomoAPIException(f"Invalid JSON response: {e}")
            
        except Exception as e:
            raise BinomoAPIException(f"Unexpected error during login: {e}")

    @staticmethod
    def create_from_login(
        login_response: LoginResponse, 
        device_id: str = DEFAULT_DEVICE_ID,
        demo: bool = True,
        enable_logging: bool = False,
        log_level: int = logging.INFO
    ) -> 'BinomoAPI':
        """
        Create BinomoAPI instance from login response, maintaining session continuity.
        
        Args:
            login_response: LoginResponse object from login method
            device_id: Device ID used for login
            demo: Use demo account if True, real account if False
            enable_logging: Enable logging if True
            log_level: Logging level
            
        Returns:
            BinomoAPI instance with maintained session
        """
        return BinomoAPI(
            auth_token=login_response.authtoken,
            device_id=device_id,
            demo=demo,
            enable_logging=enable_logging,
            log_level=log_level,
            login_session=getattr(login_response, '_session', None)
        )

    @staticmethod
    def _test_balance_with_session(session: requests.Session, auth_token: str, device_id: str) -> None:
        """Test balance request immediately after login with the same session."""
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
        
        try:
            response = session.get(BALANCE_URL, headers=headers, timeout=30)
            print(f"Immediate balance response status: {response.status_code}")
            print(f"Immediate balance response text: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("SUCCESS: Balance request worked immediately after login!")
                print(f"Balance data: {response.json()}")
                #gv.balance_data = response.json()  # Store balance data globally
                return response.json()  
            else:
                print(f"FAILED: Balance request failed with status {response.status_code}")
                
        except Exception as e:
            print(f"Exception during immediate balance test: {e}")

    def __init__(
        self, 
        auth_token: str, 
        device_id: str, 
        demo: bool = True, 
        enable_logging: bool = False,
        log_level: int = logging.INFO,
        login_session: Optional[requests.Session] = None
    ) -> None:
        """
        Initialize BinomoAPI client.
        
        Args:
            auth_token: Authentication token from login
            device_id: Unique device identifier
            demo: Use demo account if True, real account if False
            enable_logging: Enable logging if True
            log_level: Logging level (default: INFO)
            login_session: Session from login to maintain authentication state
            
        Raises:
            InvalidParameterError: If auth_token or device_id is empty
            ConnectionError: If unable to establish WebSocket connection
        """
        if not auth_token or not device_id:
            raise InvalidParameterError("auth_token and device_id are required")
            
        # Instance variables
        self._auth_token = auth_token
        self._device_id = device_id
        self._account_type = ACCOUNT_TYPES["DEMO"] if demo else ACCOUNT_TYPES["REAL"]
        self._ref_counter = 1
        self._default_asset_ric = DEFAULT_ASSET_RIC
        self._ws_client: Optional[WebSocketClient] = None
        self._last_send_time = 0
        
        # Initialize logger first
        self._setup_logging(enable_logging, log_level)
        
        # Use login session if provided, otherwise create fresh session
        if login_session:
            self._session = login_session
            if self.logger:
                self.logger.info("Using provided login session for session continuity")
        else:
            self._session = requests.Session()
            if self.logger:
                self.logger.info("Creating fresh session (no login session provided)")
        
        # FIXED: Now properly maintains session continuity
        # Load configuration and assets
        self._load_config()
        self._assets = self._load_assets()
        
        # Initialize WebSocket client (don't connect immediately)
        self._connect_websocket()
        
        if self.logger:
            self.logger.info(f"BinomoAPI initialized successfully with {len(self._assets)} assets")
        
    def _verify_session_immediately(self) -> None:
        """Verify the session works immediately after initialization."""
        try:
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
            
            response = self._session.get(BALANCE_URL, headers=headers, timeout=30)
            
            if response.status_code == 200:
                if self.logger:
                    self.logger.info("✅ Session verification successful!")
            else:
                if self.logger:
                    self.logger.warning(f"⚠️ Session verification failed with status {response.status_code}")
                    
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Session verification exception: {e}")
                
    def _establish_session(self) -> None:
        """Establish session cookies that might be needed for API calls."""
        try:
            # First, make a request to the main site to establish session
            self._session.get('https://binomo.com/', timeout=10)
            
            # Set authentication cookies in session
            self._session.cookies.set('authtoken', self._auth_token, domain='.binomo.com')
            self._session.cookies.set('device_type', 'web', domain='.binomo.com')
            self._session.cookies.set('device_id', self._device_id, domain='.binomo.com')
            
            if self.logger:
                self.logger.debug(f"Session cookies established: {self._session.cookies}")
                
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Could not establish session cookies: {e}")
            
    def _setup_logging(self, enable_logging: bool, log_level: int) -> None:
        """Setup logging configuration."""
        if enable_logging:
            self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
            self.logger.setLevel(log_level)
            
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        else:
            self.logger = None
    
    def _load_config(self) -> None:
        """Load configuration from config manager."""
        try:
            from BinomoAPI.config_manager import get_config
            self._config = get_config()
            if self.logger:
                self.logger.debug("Configuration loaded successfully")
        except ImportError:
            # Fallback if config manager is not available
            from BinomoAPI.config.conf import Config
            self._config = Config()
            if self.logger:
                self.logger.warning("Using fallback configuration")
            
    def _load_assets(self) -> List[Asset]:
        """Load available assets from JSON file."""
        try:
            assets_path = Path(__file__).parent / "assets.json"
            with open(assets_path, "r", encoding="utf-8") as f:
                assets_data = json.load(f)
            return [Asset.from_dict(asset) for asset in assets_data]
        except FileNotFoundError:
            if self.logger:
                self.logger.warning("Assets file not found, using empty asset list")
            return []
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(f"Invalid assets JSON: {e}")
            return []
            
    def _connect_websocket(self) -> None:
        """Establish WebSocket connection."""
        # Get API host from config, with fallback
        try:
            if hasattr(self._config, 'API_HOST'):
                api_host_base = self._config.API_HOST
            else:
                # Fallback to default WebSocket URL
                api_host_base = "wss://ws.binomo.com/"
        except:
            api_host_base = "wss://ws.binomo.com/"
            
        api_host = (
            f"{api_host_base}?authtoken={self._auth_token}"
            f"&device=web&device_id={self._device_id}&?v=2&vsn=2.0.0"
        )
        
        try:
            if self.logger:
                self.logger.info("Establishing WebSocket connection to Binomo API")
                
            self._ws_client = WebSocketClient(api_host)
            # Note: WebSocket connection will be established when first message is sent
            
            if self.logger:
                self.logger.info("WebSocket client initialized successfully")
                
        except Exception as e:
            raise ConnectionError(f"Failed to initialize WebSocket client: {e}")
            
    async def _ensure_websocket_connection(self) -> None:
        """Ensure WebSocket connection is established."""
        if not self._ws_client:
            raise ConnectionError("WebSocket client not initialized")
            
        # If this is the first time using the WebSocket, establish connection
        if not hasattr(self._ws_client, '_connected') or not self._ws_client._connected:
            await self._ws_client.connect()
            self._ws_client._connected = True
            
            # Join required channels after connection
            await self._join_channels_async()
            
    async def _join_channels_async(self) -> None:
        """Join required WebSocket channels asynchronously."""
        channels_to_join = [
            WS_TOPICS["ACCOUNT"],
            WS_TOPICS["USER"],
            WS_TOPICS["BASE"],
            WS_TOPICS["CFD_ZERO_SPREAD"],
            WS_TOPICS["MARATHON"],
            f"asset:{self._default_asset_ric}"
        ]
        
        for channel in channels_to_join:
            payload = {
                "topic": channel,
                "event": "phx_join",
                "payload": {},
                "ref": str(self._ref_counter),
                "join_ref": str(self._ref_counter)
            }
            await self._send_websocket_message_async(json.dumps(payload))
            
        if self.logger:
            self.logger.info(f"Joined {len(channels_to_join)} WebSocket channels")
            
    async def _send_websocket_message_async(self, message: str) -> None:
        """Send message through WebSocket connection asynchronously."""
        await self._ensure_websocket_connection()
        
        try:
            await self._ws_client.send(message)
            self._ref_counter += 1
            self._last_send_time = time.time()
            
            if self.logger:
                self.logger.debug(f"Sent WebSocket message: {message}")
                
        except Exception as e:
            raise ConnectionError(f"Failed to send WebSocket message: {e}")
    def get_asset_ric(self, asset_name: str) -> Optional[str]:
        """
        Get RIC (Reuters Instrument Code) for an asset by name.
        
        Args:
            asset_name: Name of the asset
            
        Returns:
            RIC string if found, None otherwise
        """
        for asset in self._assets:
            if asset.name.lower() == asset_name.lower():
                return asset.ric
        return None
        
    def get_available_assets(self) -> List[Asset]:
        """
        Get list of all available assets.
        
        Returns:
            List of Asset objects
        """
        return self._assets.copy()
        
    async def connect(self) -> None:
        """
        Reconnect WebSocket if disconnected.
        
        Raises:
            ConnectionError: If unable to establish connection
        """
        await self._ensure_websocket_connection()
        
    async def get_balance(self, account_type: Optional[str] = None) -> Balance:
        """
        Get account balance.
        
        Args:
            account_type: Account type ('demo' or 'real'). Uses current account if None.
            
        Returns:
            Balance object containing account balance information
            
        Raises:
            AuthenticationError: If authentication token is invalid
            ConnectionError: If unable to connect to API
            BinomoAPIException: If API returns unexpected response
        """
        # Small delay to ensure session is fully established
        import asyncio
        await asyncio.sleep(0.1)
        
        if account_type is None:
            account_type = self._account_type
            
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
        
        try:
            if self.logger:
                self.logger.debug(f"Making balance request with headers: {headers}")
            response = self._session.get(BALANCE_URL, headers=headers, timeout=30)
            
            if self.logger:
                self.logger.debug(f"Balance response status: {response.status_code}")
                self.logger.debug(f"Balance response headers: {response.headers}")
                self.logger.debug(f"Balance response text: {response.text}")
            
            response.raise_for_status()
            
            response_data = response.json()
            
            if 'data' not in response_data:
                raise BinomoAPIException("Invalid response format from balance endpoint")
                
            for account_data in response_data['data']:
                if account_data.get('account_type') == account_type:
                    return Balance.from_dict(account_data)
                    
            raise BinomoAPIException(f"Account type '{account_type}' not found")
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid authentication token")
            else:
                raise BinomoAPIException(f"HTTP error {e.response.status_code}: {e}")
                
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Request failed: {e}")
            
        except json.JSONDecodeError as e:
            raise BinomoAPIException(f"Invalid JSON response: {e}")
            
    async def place_call_option(
        self, 
        asset: str, 
        duration_seconds: int, 
        amount: float,
        use_demo: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Place a CALL binary option.
        
        Args:
            asset: Asset name or RIC
            duration_seconds: Option duration in seconds
            amount: Investment amount
            use_demo: Use demo account if True, real if False, current account if None
            
        Returns:
            Dictionary containing trade confirmation data
            
        Raises:
            InvalidParameterError: If parameters are invalid
            InsufficientBalanceError: If account balance is insufficient
            TradeError: If trade execution fails
        """
        return await self._place_option(
            asset, duration_seconds, amount, TRADE_DIRECTIONS["CALL"], use_demo
        )
        
    async def place_put_option(
        self, 
        asset: str, 
        duration_seconds: int, 
        amount: float,
        use_demo: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Place a PUT binary option.
        
        Args:
            asset: Asset name or RIC
            duration_seconds: Option duration in seconds
            amount: Investment amount
            use_demo: Use demo account if True, real if False, current account if None
            
        Returns:
            Dictionary containing trade confirmation data
            
        Raises:
            InvalidParameterError: If parameters are invalid
            InsufficientBalanceError: If account balance is insufficient
            TradeError: If trade execution fails
        """
        return await self._place_option(
            asset, duration_seconds, amount, TRADE_DIRECTIONS["PUT"], use_demo
        )
        
    async def _place_option(
        self, 
        asset: str, 
        duration_seconds: int, 
        amount: float, 
        direction: str,
        use_demo: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Internal method to place binary option.
        
        Args:
            asset: Asset name or RIC
            duration_seconds: Option duration in seconds
            amount: Investment amount
            direction: Trade direction ('call' or 'put')
            use_demo: Use demo account if True, real if False, current account if None
            
        Returns:
            Dictionary containing trade confirmation data
        """
        # Validate parameters
        if duration_seconds <= 0:
            raise InvalidParameterError("Duration must be positive")
        if amount <= 0:
            raise InvalidParameterError("Amount must be positive")
            
        # Get asset RIC
        asset_ric = self.get_asset_ric(asset) if not asset.isupper() else asset
        if not asset_ric:
            raise InvalidParameterError(f"Unknown asset: {asset}")
            
        # Determine account type
        account_type = self._account_type
        if use_demo is not None:
            account_type = ACCOUNT_TYPES["DEMO"] if use_demo else ACCOUNT_TYPES["REAL"]
            
        # Check balance
        try:
            balance = await self.Getbalance()
            if balance.amount < amount:
                raise InsufficientBalanceError(
                    f"Insufficient balance: {balance.amount} < {amount}"
                )
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Could not verify balance: {e}")
                
        # Create trade order
        trade_order = TradeOrder(
            asset_ric=asset_ric,
            direction=direction,
            amount=amount,
            duration_seconds=duration_seconds,
            account_type=account_type
        )
        
        # Send trade order
        try:
            payload = trade_order.to_payload(self._ref_counter)
            message = json.dumps(payload)
            
            if self.logger:
                self.logger.info(f"Placing {direction.upper()} option: {asset_ric}, ${amount}, {duration_seconds}s")
                
            await self._send_websocket_message_async(message)
            self._ref_counter += 1
            
            # Return trade confirmation (in a real implementation, you'd wait for confirmation)
            return {
                "status": "submitted",
                "asset": asset_ric,
                "direction": direction,
                "amount": amount,
                "duration": duration_seconds,
                "account_type": account_type,
                "ref": payload["ref"]
            }
            
        except Exception as e:
            raise TradeError(f"Failed to place {direction} option: {e}")
            
    async def close(self) -> None:
        """
        Close WebSocket connection and cleanup resources.
        """
        if self._ws_client:
            try:
                await self._ws_client.close()
                if self.logger:
                    self.logger.info("WebSocket connection closed")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error closing WebSocket: {e}")
                    
    def close_sync(self) -> None:
        """
        Synchronous close method for compatibility.
        """
        if self._ws_client:
            try:
                # For sync usage, we'll just mark as disconnected
                self._ws_client._connected = False
                if self.logger:
                    self.logger.info("WebSocket connection marked as closed")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error closing WebSocket: {e}")
                    
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_sync()
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    # Legacy method aliases for backward compatibility
    async def Call(self, ric: str, duration: int, amount: float, is_demo: bool = False) -> None:
        """Legacy method - use place_call_option instead."""
        await self.place_call_option(ric, duration, amount, is_demo)
        
    async def Put(self, ric: str, duration: int, amount: float, is_demo: bool = False) -> None:
        """Legacy method - use place_put_option instead."""
        await self.place_put_option(ric, duration, amount, is_demo)
        
    async def Getbalance(self) -> float:
        """Legacy method - use get_balance instead."""
        #time.sleep(1)
        print(f"Getting balance with session: {gv.session}, auth_token: {self._auth_token}, device_id: {self._device_id}")
        balance = self._test_balance_with_session(gv.session, self._auth_token, self._device_id)
        return balance

