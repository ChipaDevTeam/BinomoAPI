# Configuration Guide

## Support
donate in paypal: [Paypal.me](https://paypal.me/ChipaCL?country.x=CL&locale.x=en_US) <br> 
help us in patreon: [Patreon](https://patreon.com/VigoDEV?utm_medium=unknown&utm_source=join_link&utm_campaign=creatorshare_creator&utm_content=copyLink) <br>
👉 [Join us on Discord](https://discord.gg/p7YyFqSmAz) <br>
[Get our services here](https://chipa.tech/shop/) <br>
[Let us create your bot here](https://chipa.tech/product/create-your-bot/) <br>
[Contact us in Telegram](https://t.me/ChipaDevTeam)

Complete guide to configuring and customizing BinomoAPI for optimal performance.

## 🔧 Basic Configuration

### Environment Variables

Set these environment variables for basic configuration:

```bash
# Required
export BINOMO_EMAIL="your_email@example.com"
export BINOMO_PASSWORD="your_password"

# Optional
export BINOMO_DEMO_MODE="true"
export BINOMO_DEVICE_ID="your-device-id"
export BINOMO_LOG_LEVEL="INFO"
```

### Configuration File

Create `binomo_config.json` in your project root:

```json
{
  "api": {
    "demo_mode": true,
    "enable_logging": true,
    "log_level": "INFO",
    "retry_attempts": 3,
    "timeout_seconds": 30
  },
  "trading": {
    "default_asset": "EUR/USD",
    "min_trade_amount": 1.0,
    "max_trade_amount": 100.0,
    "risk_percentage": 2.0,
    "default_duration": 60
  },
  "technical": {
    "ma_period": 14,
    "rsi_period": 14,
    "bollinger_period": 20,
    "bollinger_stddev": 2
  },
  "websocket": {
    "ping_interval": 30,
    "reconnect_attempts": 3,
    "buffer_size": 1000
  }
}
```

## ⚙️ Configuration Management

### Using the Config Manager

```python
from BinomoAPI.config_manager import get_config

# Get configuration instance
config = get_config()

# Read values
demo_mode = config.get("api", "demo_mode")
max_amount = config.get("trading", "max_trade_amount")

# Update values
config.set("trading", "risk_percentage", 3.0)
config.set("technical", "rsi_period", 21)

# Save changes
config.save()
```

### Configuration Sections

#### API Configuration

```python
api_config = {
    "demo_mode": True,        # Use demo account
    "enable_logging": True,   # Enable logging
    "log_level": "INFO",     # Logging level
    "retry_attempts": 3,     # API call retries
    "timeout_seconds": 30    # API timeout
}
```

#### Trading Configuration

```python
trading_config = {
    "default_asset": "EUR/USD",     # Default trading pair
    "min_trade_amount": 1.0,        # Minimum trade size
    "max_trade_amount": 100.0,      # Maximum trade size
    "risk_percentage": 2.0,         # Risk per trade
    "default_duration": 60          # Option duration
}
```

#### Technical Analysis Configuration

```python
technical_config = {
    "ma_period": 14,              # Moving average period
    "rsi_period": 14,            # RSI period
    "bollinger_period": 20,      # Bollinger period
    "bollinger_stddev": 2        # Bollinger std dev
}
```

#### WebSocket Configuration

```python
websocket_config = {
    "ping_interval": 30,         # Keep-alive interval
    "reconnect_attempts": 3,     # Reconnection tries
    "buffer_size": 1000         # Data buffer size
}
```

## 📝 Logging Configuration

### Basic Logging Setup

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

### Advanced Logging Configuration

```python
def setup_logging():
    # Create logger
    logger = logging.getLogger('BinomoAPI')
    logger.setLevel(logging.INFO)
    
    # Create handlers
    file_handler = logging.FileHandler('trading.log')
    error_handler = logging.FileHandler('errors.log')
    console_handler = logging.StreamHandler()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set formatters
    file_handler.setFormatter(detailed_formatter)
    error_handler.setFormatter(detailed_formatter)
    console_handler.setFormatter(detailed_formatter)
    
    # Set levels
    file_handler.setLevel(logging.INFO)
    error_handler.setLevel(logging.ERROR)
    console_handler.setLevel(logging.WARNING)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger
```

## 🔐 Security Configuration

### API Security Settings

```python
security_config = {
    "ssl_verify": True,           # Verify SSL certificates
    "api_key_rotation": True,     # Rotate API keys
    "max_requests_per_min": 60,   # Rate limiting
    "ip_whitelist": [            # IP restrictions
        "192.168.1.1",
        "10.0.0.1"
    ]
}
```

### Authentication Configuration

```python
auth_config = {
    "token_expiry": 3600,        # Token lifetime
    "refresh_before": 300,       # Refresh window
    "max_failed_attempts": 3,    # Login attempts
    "lockout_duration": 900      # Lockout period
}
```

## 🎯 Trading Strategy Configuration

### Risk Management Settings

```python
risk_config = {
    "max_daily_trades": 10,      # Daily trade limit
    "max_concurrent_trades": 3,   # Concurrent trades
    "max_daily_loss": 5.0,       # Loss limit (%)
    "trailing_stop": 1.0,        # Trailing stop (%)
    "take_profit": 2.0          # Take profit (%)
}
```

### Strategy Parameters

```python
strategy_config = {
    "signal_threshold": 0.75,    # Signal strength
    "trend_period": 14,         # Trend analysis
    "momentum_period": 10,      # Momentum
    "volatility_period": 20     # Volatility
}
```

## 📊 Performance Configuration

### Optimization Settings

```python
performance_config = {
    "cache_size": 1000,         # Cache size
    "batch_size": 100,          # Batch processing
    "thread_pool": 4,           # Thread pool size
    "queue_size": 5000         # Queue capacity
}
```

## 🔄 Dynamic Configuration

### Runtime Configuration Updates

```python
async def update_configuration(api: BinomoAPI):
    config = get_config()
    
    # Update based on market conditions
    volatility = await get_market_volatility()
    if volatility > 0.5:
        config.set("trading", "risk_percentage", 1.0)
    else:
        config.set("trading", "risk_percentage", 2.0)
    
    # Update based on balance
    balance = await api.get_balance()
    if balance.amount > 1000:
        config.set("trading", "max_trade_amount", 50.0)
    
    # Save changes
    config.save()
```

Remember to always validate configuration changes and maintain secure values for sensitive settings!
