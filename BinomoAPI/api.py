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
from BinomoAPI.wss.enhanced_client import EnhancedWebSocketClient
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
            
            # Debug: Print cookies after login response
            print(f"Login response cookies: {dict(session.cookies)}")
            print(f"Login response headers: {dict(response.headers)}")
            
            response_data = response.json()
            
            if 'data' in response_data and 'authtoken' in response_data['data']:
                login_response = LoginResponse.from_dict(response_data['data'])
                
                # Store the session in the login response for later use
                gv.session = session
                login_response._session = session
                
                # Set additional session headers that might be needed for persistence
                session.headers.update({
                    'authorization-token': login_response.authtoken,
                    'device-id': device_id,
                    'device-type': 'web',
                    'origin': 'https://binomo.com',
                    'referer': 'https://binomo.com/'
                })
                
                # Set cookies manually in the session for persistence
                session.cookies.set('authtoken', login_response.authtoken, domain='.binomo.com')
                session.cookies.set('device_type', 'web', domain='.binomo.com')
                session.cookies.set('device_id', device_id, domain='.binomo.com')
                
                # Capture the exact working session state
                print(f"Working session cookies after login: {dict(session.cookies)}")
                print(f"Working session headers: {dict(session.headers)}")
                
                # Test the session immediately to ensure it works and capture balance
                test_result = BinomoAPI._test_balance_with_session(session, login_response.authtoken, device_id)
                if test_result is not None:
                    print(f"✅ Login test balance successful: {test_result}")
                    # Store the balance in the login response for immediate use
                    login_response.balance = test_result
                else:
                    print("⚠️ Login test balance failed, but continuing...")
                    login_response.balance = None
                
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
        api = BinomoAPI(
            auth_token=login_response.authtoken,
            device_id=device_id,
            demo=demo,
            enable_logging=enable_logging,
            log_level=log_level,
            login_session=getattr(login_response, '_session', None)
        )
        
        # If login response has balance, cache it immediately
        if hasattr(login_response, 'balance') and login_response.balance is not None:
            import time
            api._cached_balance = login_response.balance
            api._cached_balance_timestamp = time.time()
            if enable_logging:
                balance_dollars = login_response.balance / 100
                print(f"✅ Pre-cached balance from login: ${balance_dollars}")
        
        return api

    @staticmethod
    def _test_balance_with_session(session: requests.Session, auth_token: str, device_id: str) -> Optional[float]:
        """Test balance request immediately after login with the same session."""
        # Debug: Print session cookies
        print(f"Session cookies: {dict(session.cookies)}")
        
        # Use session's default headers but override specific ones
        headers = session.headers.copy()
        headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'authorization-token': auth_token,
            'cache-control': 'no-cache',
            'device-id': device_id,
            'device-type': 'web',
            'origin': 'https://binomo.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://binomo.com/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'user-timezone': 'UTC'
        })
        
        try:
            # Let the session handle cookies automatically
            response = session.get(BALANCE_URL, headers=headers, timeout=30)
            print(f"Immediate balance response status: {response.status_code}")
            print(f"Immediate balance response text: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("SUCCESS: Balance request worked immediately after login!")
                balance_data = response.json()
                print(f"Balance data: {balance_data}")
                
                # Try to extract balance value from response
                if 'data' in balance_data and isinstance(balance_data['data'], list):
                    for account in balance_data['data']:
                        if account.get('account_type') == 'demo':  # Look for demo account
                            balance_value = account.get('balance', 0)
                            print(f"Found demo balance: {balance_value}")
                            return float(balance_value)
                
                # If no demo account found, return first available balance
                if 'data' in balance_data and isinstance(balance_data['data'], list) and balance_data['data']:
                    balance_value = balance_data['data'][0].get('balance', 0)
                    print(f"Using first available balance: {balance_value}")
                    return float(balance_value)
                    
                return None
            else:
                print(f"FAILED: Balance request failed with status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exception during immediate balance test: {e}")
            return None

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
        
        # Cache for balance and other data that might be hard to retrieve
        self._cached_balance: Optional[float] = None
        self._cached_balance_timestamp: Optional[float] = None
        self._balance_cache_ttl = 300  # 5 minutes cache TTL
        
        # Initialize logger first
        self._setup_logging(enable_logging, log_level)
        
        # Use login session if provided, otherwise create fresh session
        if login_session:
            self._session = login_session
            if self.logger:
                self.logger.info("Using provided login session for session continuity")
            # Don't establish additional session cookies - preserve login state
            # Validate the session immediately and try to cache balance
            self._validate_session()
            self._try_cache_balance_from_session()
        else:
            self._session = requests.Session()
            if self.logger:
                self.logger.info("Creating fresh session (no login session provided)")
            # Establish session cookies only for fresh sessions
            self._establish_session()
        
        # FIXED: Now properly maintains session continuity
        # Load configuration and assets
        self._load_config()
        self._assets = self._load_assets()
        
        # Initialize WebSocket client (don't connect immediately)
        self._connect_websocket()
        
        if self.logger:
            self.logger.info(f"BinomoAPI initialized successfully with {len(self._assets)} assets")
        
    def _try_cache_balance_from_session(self) -> None:
        """Try to cache balance from the current session immediately."""
        try:
            import time
            balance = self._test_balance_with_session(self._session, self._auth_token, self._device_id)
            if balance is not None:
                self._cached_balance = balance
                self._cached_balance_timestamp = time.time()
                if self.logger:
                    self.logger.info(f"✅ Cached balance from session: ${balance/100}")
            else:
                if self.logger:
                    self.logger.warning("⚠️ Could not cache balance from session")
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to cache balance: {e}")
    
    def _get_cached_balance(self) -> Optional[float]:
        """Get cached balance if still valid."""
        if self._cached_balance is None or self._cached_balance_timestamp is None:
            return None
            
        import time
        if time.time() - self._cached_balance_timestamp > self._balance_cache_ttl:
            # Cache expired
            self._cached_balance = None
            self._cached_balance_timestamp = None
            return None
            
        return self._cached_balance
    
    def _validate_session(self) -> bool:
        """Validate that the session is working properly."""
        try:
            # Simple request to check if session is valid
            headers = self._session.headers.copy()
            headers.update({
                'accept': 'application/json',
                'authorization-token': self._auth_token,
                'device-id': self._device_id,
                'device-type': 'web'
            })
            
            # Try a simple endpoint to validate session
            response = self._session.get(BALANCE_URL, headers=headers, timeout=10)
            
            if response.status_code == 200:
                if self.logger:
                    self.logger.info("✅ Session validation successful")
                return True
            else:
                if self.logger:
                    self.logger.warning(f"⚠️ Session validation failed with status {response.status_code}")
                # Try to refresh session
                return self._refresh_session()
                
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Session validation exception: {e}")
            return self._refresh_session()
    
    def _refresh_session(self) -> bool:
        """Attempt to refresh the session authentication."""
        try:
            if self.logger:
                self.logger.info("Attempting to refresh session...")
                
            # Re-establish session state
            self._session.headers.update({
                'authorization-token': self._auth_token,
                'device-id': self._device_id,
                'device-type': 'web',
                'origin': 'https://binomo.com',
                'referer': 'https://binomo.com/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Re-set cookies
            self._session.cookies.set('authtoken', self._auth_token, domain='.binomo.com')
            self._session.cookies.set('device_type', 'web', domain='.binomo.com')
            self._session.cookies.set('device_id', self._device_id, domain='.binomo.com')
            
            # Visit main site to refresh session
            try:
                self._session.get('https://binomo.com/', timeout=10)
            except:
                pass
                
            if self.logger:
                self.logger.info("Session refresh completed")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Session refresh failed: {e}")
            return False
    
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
        """Establish WebSocket connection with enhanced authentication."""
        try:
            if self.logger:
                self.logger.info("Establishing WebSocket connection with enhanced authentication")
                
            # Create enhanced WebSocket client with multiple auth strategies
            self._ws_client = EnhancedWebSocketClient(
                auth_token=self._auth_token,
                device_id=self._device_id,
                session=getattr(self, '_session', None)
            )
            
            if self.logger:
                self.logger.info("Enhanced WebSocket client initialized successfully")
                
        except Exception as e:
            raise ConnectionError(f"Failed to initialize enhanced WebSocket client: {e}")
            
    async def _ensure_websocket_connection(self) -> None:
        """Ensure WebSocket connection is established with fallback authentication."""
        if not self._ws_client:
            raise ConnectionError("WebSocket client not initialized")
            
        # If not connected, try enhanced authentication
        if not hasattr(self._ws_client, '_connected') or not self._ws_client._connected:
            if self.logger:
                self.logger.info("Attempting WebSocket connection with authentication fallback...")
            
            success = await self._ws_client.connect_with_fallback()
            if not success:
                raise ConnectionError("All WebSocket authentication strategies failed")
            
            if self.logger:
                self.logger.info("✅ WebSocket connection established successfully!")
            
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
        # Validate session before connecting
        if not self._validate_session():
            if self.logger:
                self.logger.warning("Session validation failed before WebSocket connection")
            
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
        if account_type is None:
            account_type = self._account_type
            
        # First try cached balance
        cached_balance = self._get_cached_balance()
        if cached_balance is not None:
            if self.logger:
                self.logger.info(f"Using cached balance: ${cached_balance/100}")
            # Create a Balance object from cached data  
            # Balance.from_dict expects 'amount' in cents, so use cached_balance directly
            balance_data = {
                'amount': cached_balance,  # This is already in cents
                'currency': 'CLP',  # Default currency based on API response
                'account_type': account_type
            }
            return Balance.from_dict(balance_data)
        
        # Validate session before making request
        if not self._validate_session():
            raise AuthenticationError("Session validation failed - unable to authenticate")
            
        # Small delay to ensure session is fully established
        import asyncio
        await asyncio.sleep(0.1)
            
        # Use session's default headers but override specific ones
        headers = self._session.headers.copy()
        headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'authorization-token': self._auth_token,
            'cache-control': 'no-cache',
            'device-id': self._device_id,
            'device-type': 'web',
            'origin': 'https://binomo.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://binomo.com/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'user-timezone': 'UTC'
        })
        
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
        
    async def Getbalance(self) -> Optional[float]:
        """Legacy method - use get_balance instead."""
        # First try to get cached balance
        cached_balance = self._get_cached_balance()
        if cached_balance is not None:
            if self.logger:
                self.logger.info(f"Using cached balance: ${cached_balance/100}")
            return cached_balance
            
        # Try to validate session and get fresh balance
        if self._validate_session():
            print(f"Getting balance with session: {self._session}, auth_token: {self._auth_token}, device_id: {self._device_id}")
            balance = self._test_balance_with_session(self._session, self._auth_token, self._device_id)
            if balance is not None:
                # Update cache
                import time
                self._cached_balance = balance
                self._cached_balance_timestamp = time.time()
                return balance
        
        if self.logger:
            self.logger.warning("Session validation failed and no cached balance available")
        return None

