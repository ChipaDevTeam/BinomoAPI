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
            
        headers = DEFAULT_HEADERS.copy()
        headers.update({
            'device-id': device_id,
            'user-timezone': 'UTC'  # More generic than hardcoded timezone
        })
        
        payload = {
            "email": email,
            "password": password,
        }
        
        try:
            response = requests.post(LOGIN_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            
            if 'data' in response_data and 'authtoken' in response_data['data']:
                return LoginResponse.from_dict(response_data['data'])
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

    def __init__(
        self, 
        auth_token: str, 
        device_id: str, 
        demo: bool = True, 
        enable_logging: bool = False,
        log_level: int = logging.INFO
    ) -> None:
        """
        Initialize BinomoAPI client.
        
        Args:
            auth_token: Authentication token from login
            device_id: Unique device identifier
            demo: Use demo account if True, real account if False
            enable_logging: Enable logging if True
            log_level: Logging level (default: INFO)
            
        Raises:
            InvalidParameterError: If auth_token or device_id is empty
            ConnectionError: If unable to establish WebSocket connection
        """
        if not auth_token or not device_id:
            raise InvalidParameterError("auth_token and device_id are required")
            
        # Initialize logger
        self._setup_logging(enable_logging, log_level)
        
        # Instance variables
        self._auth_token = auth_token
        self._device_id = device_id
        self._account_type = ACCOUNT_TYPES["DEMO"] if demo else ACCOUNT_TYPES["REAL"]
        self._config = Config()
        self._ref_counter = 1
        self._default_asset_ric = DEFAULT_ASSET_RIC
        self._ws_client: Optional[WebSocketClient] = None
        self._last_send_time = 0
        
        # Load assets
        self._assets = self._load_assets()
        
        # Initialize WebSocket connection
        self._connect_websocket()
        
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
        api_host = (
            f"{self._config.API_HOST}?authtoken={self._auth_token}"
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
        if account_type is None:
            account_type = self._account_type
            
        headers = {
            'device-id': self._device_id,
            'device-type': 'web',
            'authorization-token': self._auth_token,
            'User-Agent': DEFAULT_HEADERS['user-agent']
        }
        
        try:
            response = requests.get(BALANCE_URL, headers=headers, timeout=30)
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
            balance = await self.get_balance(account_type)
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
        balance = await self.get_balance()
        return balance.amount

