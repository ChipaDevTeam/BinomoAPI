# BinomoAPI Quick Reference

## 🚀 Quick Start

```python
import asyncio
from BinomoAPI import BinomoAPI, AuthenticationError

async def main():
    try:
        # Login
        login_response = BinomoAPI.login("email@example.com", "password")
        
        # Use API with context manager
        async with BinomoAPI(
            auth_token=login_response.authtoken,
            device_id="your-device-id",
            demo=True,
            enable_logging=True
        ) as api:
            
            # Check balance
            balance = await api.get_balance()
            print(f"Balance: ${balance.amount:.2f}")
            
            # Place trades
            result = await api.place_call_option("EUR/USD", 60, 1.0)
            print(f"Trade result: {result}")
            
    except AuthenticationError as e:
        print(f"Login failed: {e}")

asyncio.run(main())
```

## 📋 Common Operations

### Authentication
```python
# Login and get auth data
login_response = BinomoAPI.login(email, password, device_id)
```

### Balance Management
```python
# Get current balance
balance = await api.get_balance()

# Get specific account balance
demo_balance = await api.get_balance("demo")
real_balance = await api.get_balance("real")
```

### Asset Management
```python
# Get all assets
assets = api.get_available_assets()

# Get asset RIC
ric = api.get_asset_ric("EUR/USD")
```

### Trading
```python
# CALL option
await api.place_call_option(
    asset="EUR/USD",
    duration_seconds=60,
    amount=5.0,
    use_demo=True
)

# PUT option
await api.place_put_option(
    asset="GBP/USD", 
    duration_seconds=120,
    amount=10.0
)
```

## 🔧 Configuration

### Environment Variables
```bash
export BINOMO_EMAIL="your_email@example.com"
export BINOMO_PASSWORD="your_password"
export BINOMO_DEMO_MODE="true"
export BINOMO_DEVICE_ID="your-device-id"
```

### Configuration File (binomo_config.json)
```json
{
  "api": {
    "demo_mode": true,
    "enable_logging": true,
    "log_level": "INFO"
  },
  "trading": {
    "default_asset": "EUR/USD",
    "min_trade_amount": 1.0,
    "max_trade_amount": 100.0,
    "risk_percentage": 2.0
  }
}
```

## 🚨 Error Handling

```python
from BinomoAPI import (
    AuthenticationError,
    ConnectionError,
    InvalidParameterError,
    InsufficientBalanceError,
    TradeError
)

try:
    # Your API calls
    pass
except AuthenticationError:
    # Handle login issues
    pass
except InsufficientBalanceError:
    # Handle low balance
    pass
except TradeError:
    # Handle trade failures
    pass
```

## 📊 Data Models

### LoginResponse
```python
login_response.authtoken  # Authentication token
login_response.user_id    # User ID
```

### Balance
```python
balance.amount           # Balance amount (float)
balance.currency         # Currency code
balance.account_type     # "demo" or "real"
```

### Asset
```python
asset.name              # Asset name (e.g., "EUR/USD")
asset.ric               # RIC code
asset.is_active         # Boolean
```

## 🔄 Legacy Compatibility

```python
# Old methods still work but are deprecated
balance = await api.Getbalance()
await api.Call("EUR", 60, 5.0, True)
await api.Put("GBP", 120, 10.0, False)

# Use new methods instead
balance = await api.get_balance()
await api.place_call_option("EUR/USD", 60, 5.0, use_demo=True)
await api.place_put_option("GBP/USD", 120, 10.0, use_demo=False)
```

## 🛠️ Advanced Usage

### Custom Configuration
```python
from BinomoAPI.config_manager import get_config

config = get_config()
config.set("trading", "max_trade_amount", 200.0)
config.save()
```

### Professional Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
```

### Context Managers
```python
# Async context manager (recommended)
async with BinomoAPI(...) as api:
    # Automatic cleanup

# Sync context manager
with BinomoAPI(...) as api:
    # Manual async operations needed
```

## 📚 Examples

- `login_example.py` - Basic usage example
- `advanced_example.py` - Professional trading bot
- `test_professional.py` - Validation tests

## 🔗 Constants

```python
from BinomoAPI import TRADE_DIRECTIONS, ACCOUNT_TYPES, OPTION_TYPES

TRADE_DIRECTIONS["CALL"]    # "call"
TRADE_DIRECTIONS["PUT"]     # "put"
ACCOUNT_TYPES["DEMO"]       # "demo"
ACCOUNT_TYPES["REAL"]       # "real"
```
