#!/usr/bin/env python3
"""
Advanced Professional Example for BinomoAPI

This example demonstrates advanced features of the professional BinomoAPI client:
- Proper async/await usage
- Advanced error handling and recovery
- Trading strategies implementation
- Portfolio management
- Real-time monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

from BinomoAPI import (
    BinomoAPI, 
    AuthenticationError, 
    ConnectionError, 
    InvalidParameterError,
    InsufficientBalanceError,
    TradeError,
    LoginResponse,
    Balance,
    Asset,
    TRADE_DIRECTIONS,
    ACCOUNT_TYPES
)

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('binomo_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingBot:
    """Advanced trading bot with portfolio management."""
    
    def __init__(self, email: str, password: str, device_id: str = None):
        self.email = email
        self.password = password
        self.device_id = device_id
        self.api: BinomoAPI = None
        self.login_response: LoginResponse = None
        self.portfolio: Dict[str, Any] = {
            "initial_balance": 0,
            "current_balance": 0,
            "trades": [],
            "profit_loss": 0
        }
        
    async def authenticate(self) -> bool:
        """Authenticate and initialize API client."""
        try:
            logger.info("🔐 Authenticating with Binomo API...")
            self.login_response = BinomoAPI.login(self.email, self.password, self.device_id)
            
            if not self.login_response:
                logger.error("❌ Authentication failed")
                return False
                
            logger.info(f"✅ Authentication successful! User ID: {self.login_response.user_id}")
            return True
            
        except AuthenticationError as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected authentication error: {e}")
            return False
            
    async def initialize_api(self, demo: bool = True) -> bool:
        """Initialize API client."""
        try:
            self.api = BinomoAPI(
                auth_token=self.login_response.authtoken,
                device_id=self.device_id or "professional-bot-2024",
                demo=demo,
                enable_logging=True,
                log_level=logging.INFO
            )
            
            # Initialize portfolio
            balance = await self.api.get_balance()
            self.portfolio["initial_balance"] = balance.amount
            self.portfolio["current_balance"] = balance.amount
            
            logger.info(f"💰 Initial balance: ${balance.amount:.2f} ({balance.account_type})")
            return True
            
        except Exception as e:
            logger.error(f"❌ API initialization failed: {e}")
            return False
            
    async def get_portfolio_status(self) -> Dict[str, Any]:
        """Get current portfolio status."""
        try:
            balance = await self.api.get_balance()
            self.portfolio["current_balance"] = balance.amount
            self.portfolio["profit_loss"] = balance.amount - self.portfolio["initial_balance"]
            
            return {
                "initial_balance": self.portfolio["initial_balance"],
                "current_balance": balance.amount,
                "profit_loss": self.portfolio["profit_loss"],
                "profit_loss_percent": (self.portfolio["profit_loss"] / self.portfolio["initial_balance"]) * 100,
                "total_trades": len(self.portfolio["trades"]),
                "account_type": balance.account_type
            }
        except Exception as e:
            logger.error(f"❌ Error getting portfolio status: {e}")
            return {}
            
    async def execute_strategy(self, strategy_name: str = "basic_scalping") -> None:
        """Execute a trading strategy."""
        logger.info(f"📈 Starting {strategy_name} strategy...")
        
        if strategy_name == "basic_scalping":
            await self._basic_scalping_strategy()
        elif strategy_name == "trend_following":
            await self._trend_following_strategy()
        else:
            logger.warning(f"⚠️ Unknown strategy: {strategy_name}")
            
    async def _basic_scalping_strategy(self) -> None:
        """Basic scalping strategy for demonstration."""
        assets_to_trade = ["EUR/USD", "GBP/USD", "USD/JPY"]
        trade_amount = 1.0
        duration = 60  # 1 minute trades
        
        for asset in assets_to_trade:
            try:
                # Check if we have sufficient balance
                balance = await self.api.get_balance()
                if balance.amount < trade_amount:
                    logger.warning(f"⚠️ Insufficient balance for {asset}: ${balance.amount:.2f}")
                    break
                    
                # Simulate analysis (in real bot, you'd have actual analysis)
                direction = TRADE_DIRECTIONS["CALL"]  # Simplified for demo
                
                # Place trade
                trade_result = await self.api.place_call_option(
                    asset=asset,
                    duration_seconds=duration,
                    amount=trade_amount
                )
                
                # Record trade
                trade_record = {
                    "timestamp": datetime.now().isoformat(),
                    "asset": asset,
                    "direction": direction,
                    "amount": trade_amount,
                    "duration": duration,
                    "result": trade_result
                }
                self.portfolio["trades"].append(trade_record)
                
                logger.info(f"✅ {direction.upper()} trade placed: {asset} ${trade_amount}")
                
                # Wait between trades
                await asyncio.sleep(2)
                
            except InsufficientBalanceError as e:
                logger.error(f"💸 Insufficient balance: {e}")
                break
            except TradeError as e:
                logger.error(f"❌ Trade error for {asset}: {e}")
                continue
            except Exception as e:
                logger.error(f"❌ Unexpected error trading {asset}: {e}")
                continue
                
    async def _trend_following_strategy(self) -> None:
        """Trend following strategy (placeholder)."""
        logger.info("📊 Trend following strategy would analyze market trends here...")
        # Implementation would include technical analysis
        
    async def monitor_trades(self, duration_minutes: int = 5) -> None:
        """Monitor active trades."""
        logger.info(f"👀 Monitoring trades for {duration_minutes} minutes...")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            try:
                status = await self.get_portfolio_status()
                logger.info(
                    f"📊 Portfolio: Balance=${status.get('current_balance', 0):.2f}, "
                    f"P&L=${status.get('profit_loss', 0):.2f} "
                    f"({status.get('profit_loss_percent', 0):.1f}%), "
                    f"Trades={status.get('total_trades', 0)}"
                )
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error during monitoring: {e}")
                await asyncio.sleep(5)
                
    def save_portfolio_report(self, filename: str = None) -> None:
        """Save portfolio report to file."""
        if not filename:
            filename = f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        try:
            with open(filename, 'w') as f:
                json.dump(self.portfolio, f, indent=2, default=str)
            logger.info(f"📝 Portfolio report saved: {filename}")
        except Exception as e:
            logger.error(f"❌ Error saving report: {e}")
            
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.api:
            await self.api.close()
            logger.info("🧹 API resources cleaned up")

async def run_trading_session():
    """Run a complete trading session."""
    bot = TradingBot(
        email="your_email@example.com",  # Replace with actual credentials
        password="your_password",
        device_id="professional-trading-bot-v2"
    )
    
    try:
        # Step 1: Authenticate
        if not await bot.authenticate():
            return
            
        # Step 2: Initialize API
        if not await bot.initialize_api(demo=True):
            return
            
        # Step 3: Show initial portfolio
        initial_status = await bot.get_portfolio_status()
        logger.info(f"🎯 Starting trading session with ${initial_status['current_balance']:.2f}")
        
        # Step 4: Execute trading strategy
        await bot.execute_strategy("basic_scalping")
        
        # Step 5: Monitor trades
        await bot.monitor_trades(duration_minutes=2)
        
        # Step 6: Final portfolio status
        final_status = await bot.get_portfolio_status()
        logger.info(
            f"🏁 Trading session complete!\n"
            f"   Initial Balance: ${final_status['initial_balance']:.2f}\n"
            f"   Final Balance: ${final_status['current_balance']:.2f}\n"
            f"   Profit/Loss: ${final_status['profit_loss']:.2f} ({final_status['profit_loss_percent']:.1f}%)\n"
            f"   Total Trades: {final_status['total_trades']}"
        )
        
        # Step 7: Save report
        bot.save_portfolio_report()
        
    except Exception as e:
        logger.error(f"❌ Trading session error: {e}")
    finally:
        await bot.cleanup()

async def simple_demo():
    """Simple demonstration of the professional API."""
    logger.info("🚀 Starting simple BinomoAPI demonstration...")
    
    try:
        # Login
        login_response = BinomoAPI.login("demo@example.com", "demo_password")
        if not login_response:
            logger.error("❌ Demo login failed (expected for demo credentials)")
            return
            
        # Use async context manager
        async with BinomoAPI(
            auth_token=login_response.authtoken,
            device_id="demo-device",
            demo=True,
            enable_logging=True
        ) as api:
            
            # Get assets
            assets = api.get_available_assets()
            logger.info(f"📊 Found {len(assets)} available assets")
            
            # Show top 5 assets
            for asset in assets[:5]:
                logger.info(f"   {asset.name} (RIC: {asset.ric})")
                
            # Check balance
            balance = await api.get_balance()
            logger.info(f"💰 Account balance: ${balance.amount:.2f}")
            
            # Demo trade (would fail with demo credentials)
            try:
                result = await api.place_call_option(
                    asset="EUR/USD",
                    duration_seconds=60,
                    amount=1.0
                )
                logger.info(f"✅ Demo trade result: {result}")
            except Exception as e:
                logger.info(f"ℹ️ Demo trade failed as expected: {e}")
                
    except Exception as e:
        logger.error(f"❌ Demo error: {e}")

def main():
    """Main function with multiple demo options."""
    print("🎯 BinomoAPI Professional Demo")
    print("1. Simple Demo (safe)")
    print("2. Full Trading Session (requires real credentials)")
    
    choice = input("Choose demo (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(simple_demo())
    elif choice == "2":
        print("\n⚠️ Warning: This will use real API calls!")
        confirm = input("Continue? (yes/no): ").strip().lower()
        if confirm == "yes":
            asyncio.run(run_trading_session())
        else:
            print("✅ Demo cancelled")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
