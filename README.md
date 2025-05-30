# BinomoAPI - Professional Python Client

A comprehensive, production-ready Python client for the Binomo trading platform API. This library provides a clean, type-safe interface for authentication, account management, and binary options trading.

## 🚀 Features

- **Professional Authentication**: Secure login with comprehensive error handling
- **Type Safety**: Full type hints and data validation using dataclasses
- **Async/Await Support**: Modern Python async programming patterns
- **Context Manager**: Automatic resource cleanup and connection management
- **Comprehensive Error Handling**: Custom exceptions for different error scenarios
- **Logging Support**: Configurable logging for debugging and monitoring
- **Balance Management**: Real-time account balance checking
- **Asset Management**: Asset discovery and RIC code resolution
- **Binary Options Trading**: CALL and PUT options with validation
- **Demo & Live Trading**: Support for both demo and real accounts

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🔧 Quick Start

### Basic Authentication and Setup

```python
import asyncio
from BinomoAPI.api import BinomoAPI
from BinomoAPI.exceptions import AuthenticationError

async def main():
    try:
        # Authenticate
        login_response = BinomoAPI.login("your_email@example.com", "your_password")
        
        # Create API client
        async with BinomoAPI(
            auth_token=login_response.authtoken,
            device_id="your_device_id",
            demo=True,  # Use demo account
            enable_logging=True
        ) as api:
            
            # Check balance
            balance = await api.get_balance()
            print(f"Balance: ${balance.amount:.2f}")
            
            # Place a trade
            result = await api.place_call_option(
                asset="EUR/USD",
                duration_seconds=60,
                amount=1.0
            )
            print(f"Trade result: {result}")
            
    except AuthenticationError as e:
        print(f"Login failed: {e}")

# Run the example
asyncio.run(main())
```

## 📚 Comprehensive Usage Guide

### 1. Authentication

```python
from BinomoAPI.api import BinomoAPI
from BinomoAPI.exceptions import AuthenticationError, ConnectionError

try:
    # Login with email and password
    login_response = BinomoAPI.login(
        email="your_email@example.com",
        password="your_password",
        device_id="optional_custom_device_id"  # Uses default if not provided
    )
    
    print(f"Auth Token: {login_response.authtoken}")
    print(f"User ID: {login_response.user_id}")
    
except AuthenticationError as e:
    print(f"Invalid credentials: {e}")
except ConnectionError as e:
    print(f"Network error: {e}")
```

### 2. API Client Initialization

```python
# Recommended: Using context manager (automatic cleanup)
async with BinomoAPI(
    auth_token=login_response.authtoken,
    device_id="your_device_id",
    demo=True,  # False for real trading
    enable_logging=True,
    log_level=logging.INFO
) as api:
    # Your trading code here
    pass

# Alternative: Manual management
api = BinomoAPI(auth_token=token, device_id=device_id, demo=True)
try:
    # Your trading code here
    pass
finally:
    api.close()  # Important: Always close connections
```

### 3. Account Balance Management

```python
# Get current account balance
balance = await api.get_balance()
print(f"Amount: ${balance.amount:.2f}")
print(f"Currency: {balance.currency}")
print(f"Account Type: {balance.account_type}")

# Check specific account type
demo_balance = await api.get_balance("demo")
real_balance = await api.get_balance("real")
```

### 4. Asset Management

```python
# Get all available assets
assets = api.get_available_assets()
for asset in assets:
    print(f"Name: {asset.name}, RIC: {asset.ric}, Active: {asset.is_active}")

# Get RIC code for an asset
ric = api.get_asset_ric("EUR/USD")
print(f"EUR/USD RIC: {ric}")
```

### 5. Binary Options Trading

```python
from BinomoAPI.exceptions import InsufficientBalanceError, TradeError

try:
    # Place CALL option
    call_result = await api.place_call_option(
        asset="EUR/USD",  # Asset name or RIC
        duration_seconds=60,  # Duration in seconds
        amount=5.0,  # Investment amount in USD
        use_demo=True  # Optional: override account type
    )
    
    # Place PUT option
    put_result = await api.place_put_option(
        asset="GBP/USD",
        duration_seconds=120,
        amount=10.0
    )
    
    print(f"CALL trade: {call_result}")
    print(f"PUT trade: {put_result}")
    
except InsufficientBalanceError as e:
    print(f"Not enough funds: {e}")
except TradeError as e:
    print(f"Trade failed: {e}")
```

## 🔍 Error Handling

The API uses custom exceptions for different error scenarios:

```python
from BinomoAPI.exceptions import (
    BinomoAPIException,      # Base exception
    AuthenticationError,     # Login/auth failures
    ConnectionError,         # Network issues
    InvalidParameterError,   # Bad parameters
    TradeError,             # Trade execution issues
    InsufficientBalanceError # Low balance
)

try:
    # Your API calls here
    pass
except AuthenticationError:
    print("Check your credentials")
except ConnectionError:
    print("Check your internet connection")
except InvalidParameterError:
    print("Check your input parameters")
except InsufficientBalanceError:
    print("Add funds to your account")
except TradeError:
    print("Trade execution failed")
except BinomoAPIException as e:
    print(f"General API error: {e}")
```

## 📊 Data Models

The API uses structured data models for type safety:

### LoginResponse
```python
@dataclass
class LoginResponse:
    authtoken: str
    user_id: str
```

### Asset
```python
@dataclass
class Asset:
    name: str
    ric: str
    is_active: bool = True
```

### Balance
```python
@dataclass
class Balance:
    amount: float
    currency: str
    account_type: str
```

## 🔧 Configuration

### Logging Configuration

```python
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create API with logging
async with BinomoAPI(
    auth_token=token,
    device_id=device_id,
    enable_logging=True,
    log_level=logging.DEBUG
) as api:
    # All API calls will be logged
    pass
```

### Custom Device ID

```python
# Use your own device ID for consistency
DEVICE_ID = "your-custom-device-id-12345"

login_response = BinomoAPI.login(email, password, DEVICE_ID)
api = BinomoAPI(auth_token=token, device_id=DEVICE_ID)
```

## 🔄 Legacy Compatibility

For backward compatibility with older code:

```python
# Legacy methods still work but are deprecated
balance = await api.Getbalance()  # Use get_balance() instead
await api.Call("EUR", 60, 1.0, True)  # Use place_call_option() instead
await api.Put("EUR", 60, 1.0, True)   # Use place_put_option() instead
```

## 🛡️ Best Practices

1. **Always use context managers** for automatic cleanup
2. **Handle exceptions properly** for robust applications
3. **Use demo accounts** for testing and development
4. **Enable logging** for debugging and monitoring
5. **Validate inputs** before making API calls
6. **Check balances** before placing trades
7. **Use type hints** for better code quality

## 📁 Project Structure

```
BinomoAPI/
├── __init__.py
├── api.py              # Main API client
├── exceptions.py       # Custom exceptions
├── constants.py        # API constants
├── models.py          # Data models
├── assets.json        # Available assets
├── config/
│   ├── __init__.py
│   └── conf.py        # Configuration
└── wss/
    ├── __init__.py
    └── client.py      # WebSocket client
```

## 🔗 API Reference

### Static Methods
- `BinomoAPI.login(email, password, device_id=None) -> LoginResponse`

### Instance Methods
- `get_balance(account_type=None) -> Balance`
- `get_asset_ric(asset_name) -> Optional[str]`
- `get_available_assets() -> List[Asset]`
- `place_call_option(asset, duration_seconds, amount, use_demo=None) -> Dict`
- `place_put_option(asset, duration_seconds, amount, use_demo=None) -> Dict`
- `connect() -> None`
- `close() -> None`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This library is for educational and development purposes. Binary options trading involves financial risk. Always test with demo accounts before using real money. The authors are not responsible for any financial losses.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support and questions, please open an issue on the GitHub repository.
BinomoAPI is the api for the binomo trading platform

## Talk to us
👉 [Join us on Discord](https://discord.gg/p7YyFqSmAz)

## Reference
Inspired by this project: https://github.com/hert0t/Binomo-API

## Support us
donate in paypal: [Paypal.me](https://paypal.me/ChipaCL?country.x=CL&locale.x=en_US) <br> 
help us in patreon: [Patreon](https://patreon.com/VigoDEV?utm_medium=unknown&utm_source=join_link&utm_campaign=creatorshare_creator&utm_content=copyLink) <br>