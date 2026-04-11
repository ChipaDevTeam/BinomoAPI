# API Reference

## Support
donate in paypal: [Paypal.me](https://paypal.me/ChipaCL?country.x=CL&locale.x=en_US) <br> 
help us in patreon: [Patreon](https://patreon.com/VigoDEV?utm_medium=unknown&utm_source=join_link&utm_campaign=creatorshare_creator&utm_content=copyLink) <br>
👉 [Join us on Discord](https://discord.gg/p7YyFqSmAz) <br>
[Get our services here](https://https://chipatrade.com/shop/) <br>
[Let us create your bot here](https://chipatrade.com/services/bot-development) <br>
[Contact us in Telegram](https://t.me/ChipaDevTeam)

Complete reference documentation for the BinomoAPI Python client.

## 🔐 Authentication

### BinomoAPI.login

```python
@staticmethod
def login(email: str, password: str) -> LoginResponse:
    """
    Authenticate with Binomo platform.
    
    Args:
        email (str): Your Binomo account email
        password (str): Your Binomo account password
    
    Returns:
        LoginResponse: Object containing authtoken and user_id
        
    Raises:
        AuthenticationError: If login fails
    """
```

### BinomoAPI Constructor

```python
def __init__(
    self,
    auth_token: str,
    device_id: str,
    demo: bool = True,
    enable_logging: bool = False,
    log_level: str = "INFO"
) -> None:
    """
    Initialize BinomoAPI client.
    
    Args:
        auth_token (str): Authentication token from login
        device_id (str): Unique device identifier
        demo (bool): Use demo account if True
        enable_logging (bool): Enable debug logging
        log_level (str): Logging level (DEBUG/INFO/WARNING/ERROR)
    """
```

## 💰 Balance Operations

### get_balance

```python
async def get_balance(
    self,
    account_type: Optional[str] = None
) -> Balance:
    """
    Get account balance.
    
    Args:
        account_type (str, optional): "demo" or "real"
    
    Returns:
        Balance: Current balance information
        
    Raises:
        ConnectionError: On network issues
    """
```

## 📈 Trading Operations

### place_call_option

```python
async def place_call_option(
    self,
    asset: str,
    duration_seconds: int,
    amount: float,
    use_demo: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Place a CALL option trade.
    
    Args:
        asset (str): Asset name (e.g., "EUR/USD")
        duration_seconds (int): Option duration in seconds
        amount (float): Trade amount
        use_demo (bool, optional): Override default account type
        
    Returns:
        dict: Trade result information
        
    Raises:
        TradeError: If trade fails
        InsufficientBalanceError: If balance too low
    """
```

### place_put_option

```python
async def place_put_option(
    self,
    asset: str,
    duration_seconds: int,
    amount: float,
    use_demo: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Place a PUT option trade.
    
    Args:
        asset (str): Asset name (e.g., "EUR/USD")
        duration_seconds (int): Option duration in seconds
        amount (float): Trade amount
        use_demo (bool, optional): Override default account type
        
    Returns:
        dict: Trade result information
        
    Raises:
        TradeError: If trade fails
        InsufficientBalanceError: If balance too low
    """
```

## 🎯 Asset Management

### get_available_assets

```python
def get_available_assets(self) -> List[Asset]:
    """
    Get list of available trading assets.
    
    Returns:
        List[Asset]: Available assets and their properties
    """
```

### get_asset_ric

```python
def get_asset_ric(
    self,
    asset_name: str
) -> str:
    """
    Get RIC code for an asset.
    
    Args:
        asset_name (str): Asset name (e.g., "EUR/USD")
        
    Returns:
        str: RIC code for the asset
        
    Raises:
        InvalidParameterError: If asset not found
    """
```

## ⚙️ Configuration Management

### get_config

```python
@staticmethod
def get_config() -> Config:
    """
    Get configuration manager instance.
    
    Returns:
        Config: Configuration manager object
    """
```

### Config Methods

```python
class Config:
    def get(self, section: str, key: str) -> Any: ...
    def set(self, section: str, key: str, value: Any) -> None: ...
    def save(self) -> None: ...
```

## 🚨 Exception Hierarchy

```python
BinomoAPIException
├── AuthenticationError   # Login/auth issues
├── ConnectionError      # Network problems
├── InvalidParameterError # Bad input
├── TradeError          # Trade execution fails
└── InsufficientBalanceError # Not enough funds
```

## 📊 Data Models

### LoginResponse

```python
@dataclass
class LoginResponse:
    authtoken: str  # Authentication token
    user_id: str    # User identifier
```

### Balance

```python
@dataclass
class Balance:
    amount: float       # Balance amount
    currency: str       # Currency code
    account_type: str   # "demo" or "real"
```

### Asset

```python
@dataclass
class Asset:
    name: str          # Asset name
    ric: str          # RIC code
    is_active: bool   # Trading availability
```

## 🔄 Constants

```python
TRADE_DIRECTIONS = {
    "CALL": "call",
    "PUT": "put"
}

ACCOUNT_TYPES = {
    "DEMO": "demo",
    "REAL": "real"
}

OPTION_TYPES = {
    "TURBO": "turbo",
    "BINARY": "binary"
}
```

## 📝 Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
```

## 🔗 WebSocket Client

```python
class WebSocketClient:
    async def connect(self) -> None: ...
    async def subscribe(self, channels: List[str]) -> None: ...
    async def send_message(self, message: Dict[str, Any]) -> None: ...
    async def close(self) -> None: ...
```

Remember to handle all operations within an async context manager for proper resource management:

```python
async with BinomoAPI(...) as api:
    # Your trading code here
    pass  # Resources automatically cleaned up
```
