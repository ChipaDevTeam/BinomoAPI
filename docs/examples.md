# Examples

Collection of practical examples and code snippets for BinomoAPI.

## 🚀 Basic Examples

### Simple Trading Bot

```python
import asyncio
from BinomoAPI import BinomoAPI, AuthenticationError

async def simple_trading_bot():
    try:
        # Login
        login_response = BinomoAPI.login(
            "your_email@example.com",
            "your_password"
        )
        
        async with BinomoAPI(
            auth_token=login_response.authtoken,
            device_id=login_response.user_id,
            demo=True
        ) as api:
            # Check balance
            balance = await api.get_balance()
            print(f"Starting balance: ${balance.amount}")
            
            # Place a trade
            if balance.amount >= 1.0:
                result = await api.place_call_option(
                    asset="EUR/USD",
                    duration_seconds=60,
                    amount=1.0
                )
                print(f"Trade result: {result}")
    
    except AuthenticationError as e:
        print(f"Login failed: {e}")

if __name__ == "__main__":
    asyncio.run(simple_trading_bot())
```

### Multi-Asset Monitor

```python
import asyncio
import logging
from BinomoAPI import BinomoAPI

async def monitor_multiple_assets():
    login_response = BinomoAPI.login(
        "your_email@example.com",
        "your_password"
    )
    
    async with BinomoAPI(
        auth_token=login_response.authtoken,
        device_id=login_response.user_id,
        demo=True,
        enable_logging=True
    ) as api:
        # Get all assets
        assets = api.get_available_assets()
        
        # Monitor specific pairs
        target_pairs = ["EUR/USD", "GBP/USD", "USD/JPY"]
        
        for asset in assets:
            if asset.name in target_pairs and asset.is_active:
                print(f"Monitoring {asset.name}")
                # Add your monitoring logic here

if __name__ == "__main__":
    asyncio.run(monitor_multiple_assets())
```

## 🔄 Advanced Examples

### Professional Trading Bot

```python
import asyncio
import logging
from datetime import datetime
from BinomoAPI import BinomoAPI
from BinomoAPI.exceptions import (
    AuthenticationError,
    TradeError,
    InsufficientBalanceError
)

class TradingBot:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_bot.log'),
                logging.StreamHandler()
            ]
        )
    
    async def initialize_api(self):
        try:
            login_response = BinomoAPI.login(
                self.email,
                self.password
            )
            logging.info("Login successful")
            
            return BinomoAPI(
                auth_token=login_response.authtoken,
                device_id=login_response.user_id,
                demo=True,
                enable_logging=True
            )
        except AuthenticationError as e:
            logging.error(f"Login failed: {e}")
            raise
    
    async def check_trading_conditions(self, api: BinomoAPI):
        # Get balance
        balance = await api.get_balance()
        logging.info(f"Current balance: ${balance.amount}")
        
        # Check if we can trade
        if balance.amount < 1.0:
            raise InsufficientBalanceError(
                "Balance too low for trading"
            )
        
        # Get asset status
        assets = api.get_available_assets()
        target_asset = next(
            (a for a in assets if a.name == "EUR/USD"),
            None
        )
        
        if not target_asset or not target_asset.is_active:
            raise TradeError("Target asset not available")
        
        return True
    
    async def execute_trade_strategy(self, api: BinomoAPI):
        try:
            # Validate conditions
            await self.check_trading_conditions(api)
            
            # Place trade
            result = await api.place_call_option(
                asset="EUR/USD",
                duration_seconds=60,
                amount=1.0
            )
            
            logging.info(f"Trade executed: {result}")
            return result
            
        except InsufficientBalanceError as e:
            logging.error(f"Balance error: {e}")
        except TradeError as e:
            logging.error(f"Trade error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
    
    async def run(self):
        try:
            async with await self.initialize_api() as api:
                while True:
                    current_time = datetime.now().strftime(
                        "%H:%M:%S"
                    )
                    logging.info(
                        f"Running trading cycle at {current_time}"
                    )
                    
                    await self.execute_trade_strategy(api)
                    
                    # Wait before next cycle
                    await asyncio.sleep(60)
        
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
        except Exception as e:
            logging.error(f"Bot error: {e}")

if __name__ == "__main__":
    bot = TradingBot(
        email="your_email@example.com",
        password="your_password"
    )
    asyncio.run(bot.run())
```

### Market Analysis Bot

```python
import asyncio
import logging
from typing import Dict, List
from BinomoAPI import BinomoAPI

class MarketAnalyzer:
    def __init__(self, api: BinomoAPI):
        self.api = api
        self.assets: List[str] = [
            "EUR/USD",
            "GBP/USD",
            "USD/JPY"
        ]
        self.analysis: Dict = {}
    
    async def analyze_asset(self, asset: str):
        """
        Implement your market analysis logic here.
        This is a placeholder implementation.
        """
        # Get asset data
        ric = self.api.get_asset_ric(asset)
        
        # Your analysis logic here
        analysis_result = {
            "asset": asset,
            "ric": ric,
            "timestamp": datetime.now().isoformat(),
            "signal": "NEUTRAL"
        }
        
        self.analysis[asset] = analysis_result
        return analysis_result
    
    async def analyze_all_assets(self):
        tasks = []
        for asset in self.assets:
            tasks.append(self.analyze_asset(asset))
        
        results = await asyncio.gather(*tasks)
        return results

async def run_market_analysis():
    login_response = BinomoAPI.login(
        "your_email@example.com",
        "your_password"
    )
    
    async with BinomoAPI(
        auth_token=login_response.authtoken,
        device_id=login_response.user_id,
        demo=True
    ) as api:
        analyzer = MarketAnalyzer(api)
        results = await analyzer.analyze_all_assets()
        
        for result in results:
            print(f"Analysis for {result['asset']}: {result}")

if __name__ == "__main__":
    asyncio.run(run_market_analysis())
```

## 📊 Data Analysis Examples

### Historical Data Analysis

```python
import asyncio
import pandas as pd
from BinomoAPI import BinomoAPI

async def analyze_historical_data():
    login_response = BinomoAPI.login(
        "your_email@example.com",
        "your_password"
    )
    
    async with BinomoAPI(
        auth_token=login_response.authtoken,
        device_id=login_response.user_id,
        demo=True
    ) as api:
        # Get historical data
        data = await api.get_historical_data(
            asset="EUR/USD",
            timeframe="1h",
            count=100
        )
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(data)
        
        # Calculate indicators
        df['SMA20'] = df['close'].rolling(window=20).mean()
        df['SMA50'] = df['close'].rolling(window=50).mean()
        
        # Print analysis
        print(df.tail())

if __name__ == "__main__":
    asyncio.run(analyze_historical_data())
```

### Real-time Analysis

```python
import asyncio
from BinomoAPI import BinomoAPI

async def analyze_realtime_data():
    login_response = BinomoAPI.login(
        "your_email@example.com",
        "your_password"
    )
    
    async with BinomoAPI(
        auth_token=login_response.authtoken,
        device_id=login_response.user_id,
        demo=True
    ) as api:
        async def on_price_update(data):
            # Implement your real-time analysis here
            print(f"New price data: {data}")
        
        # Subscribe to price updates
        await api.ws_client.subscribe(["price_feed"])
        api.ws_client.on_price_update = on_price_update
        
        # Keep running
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(analyze_realtime_data())
```

## 🔧 Utility Examples

### Configuration Management

```python
from BinomoAPI.config_manager import get_config

def setup_trading_config():
    config = get_config()
    
    # Set trading parameters
    config.set("trading", "max_trade_amount", 100.0)
    config.set("trading", "risk_percentage", 2.0)
    
    # Set technical parameters
    config.set("technical", "ma_period", 14)
    config.set("technical", "rsi_period", 14)
    
    # Save configuration
    config.save()

if __name__ == "__main__":
    setup_trading_config()
```

### Logging Setup

```python
import logging

def setup_trading_logs():
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler('trading.log')
    file_handler.setFormatter(detailed_formatter)
    
    # Error handler
    error_handler = logging.FileHandler('errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

if __name__ == "__main__":
    setup_trading_logs()
```

Remember to replace the email/password placeholders with your actual credentials and always test on a demo account first!
