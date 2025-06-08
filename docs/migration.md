# Migration Guide

## Support
donate in paypal: [Paypal.me](https://paypal.me/ChipaCL?country.x=CL&locale.x=en_US) <br> 
help us in patreon: [Patreon](https://patreon.com/VigoDEV?utm_medium=unknown&utm_source=join_link&utm_campaign=creatorshare_creator&utm_content=copyLink) <br>
👉 [Join us on Discord](https://discord.gg/p7YyFqSmAz) <br>
[Get our services here](https://chipa.tech/shop/) <br>
[Let us create your bot here](https://chipa.tech/product/create-your-bot/) <br>
[Contact us in Telegram](https://t.me/ChipaDevTeam)

Guide for migrating from older versions of BinomoAPI to the latest version.

## 🔄 Version 2.0 to 3.0

### Major Changes

1. Full async/await support
2. Type safety improvements
3. Professional error handling
4. Enhanced logging system
5. Configuration management

### Breaking Changes

#### 1. Async Support

Before (2.x):
```python
# Synchronous API
api = BinomoAPI(auth_token, device_id)
balance = api.get_balance()
result = api.Call("EUR/USD", 60, 5.0)
```

After (3.x):
```python
# Async API
async with BinomoAPI(auth_token, device_id) as api:
    balance = await api.get_balance()
    result = await api.place_call_option(
        asset="EUR/USD",
        duration_seconds=60,
        amount=5.0
    )
```

#### 2. Method Names

Before (2.x):
```python
api.Call("EUR", 60, 5.0, True)
api.Put("GBP", 120, 10.0, False)
api.Getbalance()
```

After (3.x):
```python
await api.place_call_option(
    asset="EUR/USD",
    duration_seconds=60,
    amount=5.0,
    use_demo=True
)
await api.place_put_option(
    asset="GBP/USD",
    duration_seconds=120,
    amount=10.0,
    use_demo=False
)
await api.get_balance()
```

#### 3. Error Handling

Before (2.x):
```python
try:
    result = api.Call("EUR", 60, 5.0)
    if not result:
        print("Trade failed")
except Exception as e:
    print(f"Error: {e}")
```

After (3.x):
```python
from BinomoAPI.exceptions import TradeError, InsufficientBalanceError

try:
    result = await api.place_call_option(
        asset="EUR/USD",
        duration_seconds=60,
        amount=5.0
    )
except InsufficientBalanceError:
    logging.error("Not enough funds")
except TradeError as e:
    logging.error(f"Trade failed: {e}")
```

#### 4. Configuration

Before (2.x):
```python
api = BinomoAPI(
    auth_token,
    device_id,
    demo=True,
    timeout=30
)
```

After (3.x):
```python
from BinomoAPI.config_manager import get_config

config = get_config()
config.set("api", "timeout_seconds", 30)
config.save()

async with BinomoAPI(
    auth_token=auth_token,
    device_id=device_id,
    demo=True
) as api:
    # API uses configuration
```

### Upgrade Steps

1. Install latest version:
```bash
pip install --upgrade BinomoAPI
```

2. Update imports:
```python
# Old imports
from BinomoAPI import BinomoAPI

# New imports
from BinomoAPI import BinomoAPI
from BinomoAPI.exceptions import (
    AuthenticationError,
    TradeError
)
```

3. Update code structure:
```python
import asyncio
from BinomoAPI import BinomoAPI

async def main():
    async with BinomoAPI(...) as api:
        # Your trading code here
        pass

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔄 Version 1.0 to 2.0

### Major Changes

1. WebSocket support
2. Real-time data
3. Basic error handling
4. Demo account support

### Breaking Changes

#### 1. Authentication

Before (1.x):
```python
api = BinomoAPI()
api.login("email", "password")
```

After (2.x):
```python
api = BinomoAPI.login("email", "password")
```

#### 2. Trading Methods

Before (1.x):
```python
api.trade("EUR", "CALL", 60, 5.0)
```

After (2.x):
```python
api.Call("EUR", 60, 5.0)
```

### Upgrade Steps

1. Install version 2.0:
```bash
pip install BinomoAPI==2.0.0
```

2. Update authentication:
```python
# Old style
api = BinomoAPI()
api.login("email", "password")

# New style
api = BinomoAPI.login("email", "password")
```

## 📝 Tips for Smooth Migration

### 1. Gradual Migration

Migrate one component at a time:
1. Update authentication
2. Convert to async/await
3. Implement new error handling
4. Update configuration

### 2. Testing Strategy

1. Create test environment
2. Run old and new versions in parallel
3. Compare results
4. Verify functionality

### 3. Common Issues

#### Async/Await Conversion

Problem:
```python
# This will not work
result = api.place_call_option(...)
```

Solution:
```python
# Use async/await
result = await api.place_call_option(...)
```

#### Method Names

Problem:
```python
# Old method names will raise AttributeError
api.Call(...)
```

Solution:
```python
# Use new method names
await api.place_call_option(...)
```

#### Configuration

Problem:
```python
# Direct configuration no longer works
api = BinomoAPI(..., timeout=30)
```

Solution:
```python
# Use configuration manager
config = get_config()
config.set("api", "timeout_seconds", 30)
config.save()
```

## 🔍 Compatibility Mode

For smoother transition, version 3.0 includes compatibility mode:

```python
from BinomoAPI import BinomoAPI
from BinomoAPI.compat import enable_legacy_mode

# Enable compatibility mode
enable_legacy_mode()

# Old methods will work with warnings
api.Call("EUR", 60, 5.0)  # Works but warns
```

## 📚 Additional Resources

1. [Full Documentation](./index.md)
2. [API Reference](./api-reference.md)
3. [Examples](./examples.md)
4. [Best Practices](./best-practices.md)

## 🤝 Getting Help

If you encounter issues during migration:

1. Check the [FAQ](./faq.md)
2. Join our [Discord community](https://discord.gg/p7YyFqSmAz)
3. Open an [issue on GitHub](https://github.com/yourname/BinomoAPI/issues)
4. Contact support team

Remember to always test thoroughly after migration!
