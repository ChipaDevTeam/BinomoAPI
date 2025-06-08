# Advanced Usage Guide

## Support
donate in paypal: [Paypal.me](https://paypal.me/ChipaCL?country.x=CL&locale.x=en_US) <br> 
help us in patreon: [Patreon](https://patreon.com/VigoDEV?utm_medium=unknown&utm_source=join_link&utm_campaign=creatorshare_creator&utm_content=copyLink) <br>
👉 [Join us on Discord](https://discord.gg/p7YyFqSmAz) <br>
[Get our services here](https://chipa.tech/shop/) <br>
[Let us create your bot here](https://chipa.tech/product/create-your-bot/) <br>
[Contact us in Telegram](https://t.me/ChipaDevTeam)

Comprehensive guide for advanced features and professional trading with BinomoAPI.

## 🚀 Advanced Trading Patterns

### Professional Trading Setup

```python
import asyncio
import logging
from BinomoAPI import BinomoAPI, TradeError
from BinomoAPI.config_manager import get_config

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)

async def setup_trading_environment(auth_token: str, device_id: str):
    # Initialize with all professional features
    return BinomoAPI(
        auth_token=auth_token,
        device_id=device_id,
        demo=True,
        enable_logging=True,
        log_level=logging.INFO
    )

async def execute_trade_strategy(api: BinomoAPI):
    try:
        balance = await api.get_balance()
        if balance.amount >= 5.0:
            result = await api.place_call_option(
                asset="EUR/USD",
                duration_seconds=60,
                amount=5.0
            )
            logging.info(f"Trade executed: {result}")
    except TradeError as e:
        logging.error(f"Trade failed: {e}")
```

### Multiple Account Management

```python
async def manage_accounts(api: BinomoAPI):
    # Check both account types
    demo_balance = await api.get_balance("demo")
    real_balance = await api.get_balance("real")
    
    # Log balances
    logging.info(f"Demo balance: ${demo_balance.amount}")
    logging.info(f"Real balance: ${real_balance.amount}")
    
    # Trade on specific account
    if demo_balance.amount >= 10.0:
        await api.place_call_option(
            asset="EUR/USD",
            duration_seconds=60,
            amount=10.0,
            use_demo=True  # Explicitly use demo account
        )
```

## 📊 Asset Analysis

### Asset Monitoring

```python
async def monitor_assets(api: BinomoAPI):
    # Get all available assets
    assets = api.get_available_assets()
    
    # Filter active assets
    active_assets = [
        asset for asset in assets 
        if asset.is_active
    ]
    
    # Monitor specific assets
    target_assets = [
        "EUR/USD", "GBP/USD", "USD/JPY"
    ]
    
    for asset in active_assets:
        if asset.name in target_assets:
            ric = api.get_asset_ric(asset.name)
            logging.info(f"Monitoring {asset.name} (RIC: {ric})")
```

## ⚙️ Advanced Configuration

### Custom Configuration Management

```python
def setup_trading_config():
    config = get_config()
    
    # Trading parameters
    config.set("trading", "max_trade_amount", 100.0)
    config.set("trading", "risk_percentage", 2.0)
    config.set("trading", "default_duration", 60)
    
    # Technical parameters
    config.set("technical", "ma_period", 14)
    config.set("technical", "rsi_period", 14)
    config.set("technical", "bollinger_period", 20)
    
    # Save configuration
    config.save()
```

## 🔄 WebSocket Integration

### Real-time Data Handling

```python
async def handle_realtime_data(api: BinomoAPI):
    async def on_price_update(data):
        logging.info(f"Price update: {data}")
    
    async def on_trade_update(data):
        logging.info(f"Trade update: {data}")
    
    # Subscribe to WebSocket feeds
    await api.ws_client.subscribe([
        "price_feed",
        "trade_feed"
    ])
    
    # Set up handlers
    api.ws_client.on_price_update = on_price_update
    api.ws_client.on_trade_update = on_trade_update
```

## 🛡️ Advanced Error Handling

### Comprehensive Error Management

```python
from BinomoAPI.exceptions import (
    AuthenticationError,
    ConnectionError,
    TradeError,
    InsufficientBalanceError
)

async def handle_trading_errors(api: BinomoAPI):
    try:
        # Attempt trade
        result = await api.place_call_option(
            asset="EUR/USD",
            duration_seconds=60,
            amount=5.0
        )
        
    except AuthenticationError as e:
        logging.error(f"Authentication failed: {e}")
        # Attempt reauthorization
        
    except ConnectionError as e:
        logging.error(f"Connection failed: {e}")
        # Implement retry logic
        
    except InsufficientBalanceError as e:
        logging.error(f"Insufficient funds: {e}")
        # Adjust trade amount or notify
        
    except TradeError as e:
        logging.error(f"Trade failed: {e}")
        # Analyze failure and adjust strategy
```

## 📈 Professional Trading Strategies

### Strategy Implementation

```python
class TradingStrategy:
    def __init__(self, api: BinomoAPI):
        self.api = api
        self.config = get_config()
    
    async def analyze_market(self, asset: str):
        # Implement market analysis
        pass
    
    async def execute_trade(self, analysis_result: dict):
        if analysis_result["signal"] == "CALL":
            await self.api.place_call_option(
                asset=analysis_result["asset"],
                duration_seconds=60,
                amount=self.calculate_position_size()
            )
    
    def calculate_position_size(self) -> float:
        balance = await self.api.get_balance()
        risk_percentage = self.config.get(
            "trading", 
            "risk_percentage"
        )
        return balance.amount * (risk_percentage / 100)
```

## 🔍 Monitoring and Logging

### Advanced Logging Setup

```python
def setup_advanced_logging():
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler for all logs
    file_handler = logging.FileHandler('trading.log')
    file_handler.setFormatter(detailed_formatter)
    
    # Error-specific handler
    error_handler = logging.FileHandler('errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
```

## 🚀 Putting It All Together

```python
async def run_professional_trading():
    # Initialize everything
    setup_advanced_logging()
    setup_trading_config()
    
    # Login
    login_response = BinomoAPI.login(
        os.getenv("BINOMO_EMAIL"),
        os.getenv("BINOMO_PASSWORD")
    )
    
    async with await setup_trading_environment(
        login_response.authtoken,
        login_response.user_id
    ) as api:
        # Initialize strategy
        strategy = TradingStrategy(api)
        
        # Monitor assets
        await monitor_assets(api)
        
        # Start real-time data handling
        await handle_realtime_data(api)
        
        # Execute trading strategy
        while True:
            try:
                analysis = await strategy.analyze_market("EUR/USD")
                await strategy.execute_trade(analysis)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logging.error(f"Strategy error: {e}")
                await asyncio.sleep(5)  # Error cooldown

if __name__ == "__main__":
    asyncio.run(run_professional_trading())
```

Remember to always test strategies on a demo account first and implement proper risk management!
