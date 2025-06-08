# Getting Started with BinomoAPI

## Support
donate in paypal: [Paypal.me](https://paypal.me/ChipaCL?country.x=CL&locale.x=en_US) <br> 
help us in patreon: [Patreon](https://patreon.com/VigoDEV?utm_medium=unknown&utm_source=join_link&utm_campaign=creatorshare_creator&utm_content=copyLink) <br>
👉 [Join us on Discord](https://discord.gg/p7YyFqSmAz) <br>
[Get our services here](https://chipa.tech/shop/) <br>
[Let us create your bot here](https://chipa.tech/product/create-your-bot/) <br>
[Contact us in Telegram](https://t.me/ChipaDevTeam)

Welcome to BinomoAPI! This guide will help you get up and running with automated trading on the Binomo platform using Python.

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- A Binomo trading account

### Install from PyPI

```bash
pip install BinomoAPI
```

### Install from Source

```bash
git clone https://github.com/yourname/BinomoAPI.git
cd BinomoAPI
pip install -e .
```

## 🔑 Basic Setup

### Environment Variables

Set up your credentials securely using environment variables:

```bash
export BINOMO_EMAIL="your_email@example.com"
export BINOMO_PASSWORD="your_password"
export BINOMO_DEMO_MODE="true"  # Use demo account by default
```

### Configuration File

Create a `binomo_config.json` file (optional):

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

## 🚀 Your First Trade

Here's a complete example of making your first trade:

```python
import asyncio
from BinomoAPI import BinomoAPI, AuthenticationError, TradeError

async def main():
    try:
        # Login to get authentication data
        login_response = BinomoAPI.login(
            "your_email@example.com",
            "your_password"
        )
        print(f"Login successful! User ID: {login_response.user_id}")
        
        # Initialize API client
        async with BinomoAPI(
            auth_token=login_response.authtoken,
            device_id=login_response.user_id,
            demo=True,  # Use demo account
            enable_logging=True
        ) as api:
            # Check balance
            balance = await api.get_balance()
            print(f"Demo account balance: ${balance.amount}")
            
            # Place a trade
            if balance.amount >= 1.0:
                result = await api.place_call_option(
                    asset="EUR/USD",
                    duration_seconds=60,
                    amount=1.0
                )
                print(f"Trade placed successfully: {result}")
            else:
                print("Insufficient balance for trading")
                
    except AuthenticationError as e:
        print(f"Login failed: {e}")
    except TradeError as e:
        print(f"Trade failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 Understanding Results

### Login Response

The `login_response` object contains:
- `authtoken`: Authentication token for API calls
- `user_id`: Your unique user identifier

### Balance Information

The `balance` object includes:
- `amount`: Current balance amount
- `currency`: Currency code
- `account_type`: "demo" or "real"

### Trade Results

Trade results contain:
- Trade ID
- Execution status
- Entry price
- Expiry time
- Potential profit

## 🎯 Next Steps

1. Explore more [advanced trading features](./advanced-usage.md)
2. Learn about [error handling](./error-handling.md)
3. Check out complete [code examples](./examples.md)
4. Read the [API reference](./api-reference.md)

## 🚨 Common Issues

### Authentication Fails
- Verify your credentials
- Check network connection
- Ensure account is active

### Trade Execution Fails
- Verify sufficient balance
- Check asset availability
- Validate trade parameters

### WebSocket Connection Issues
- Check internet connection
- Verify WebSocket endpoint
- Ensure proper authentication

## 🤝 Getting Help

- Check the [FAQ](./faq.md)
- Join our [Discord community](https://discord.gg/p7YyFqSmAz)
- Open an [issue on GitHub](https://github.com/yourname/BinomoAPI/issues)

Remember to always use the demo account first when testing new trading strategies!
