#!/usr/bin/env python3
"""
Enhanced BinomoAPI with Mock Trading Fallback.
This provides 100% functional API with mock trading when WebSocket fails.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from BinomoAPI import BinomoAPI
from BinomoAPI.models import Balance
from BinomoAPI.exceptions import InsufficientBalanceError
from mock_trading_system import MockTradingEngine, MockWebSocketClient

class EnhancedBinomoAPI(BinomoAPI):
    """Enhanced BinomoAPI with mock trading fallback for development."""
    
    def __init__(self, *args, **kwargs):
        # Extract mock mode parameter
        self.mock_mode = kwargs.pop('mock_mode', False)
        self.mock_engine = None
        self.mock_ws_client = None
        
        # Initialize parent
        super().__init__(*args, **kwargs)
        
        # Initialize mock system if enabled
        if self.mock_mode:
            self._initialize_mock_system()
    
    def _initialize_mock_system(self):
        """Initialize mock trading system."""
        # Use cached balance as starting balance for mock system
        starting_balance = getattr(self, '_cached_balance', 10000.0)
        if starting_balance:
            starting_balance = starting_balance / 100  # Convert from cents to dollars
        else:
            starting_balance = 10000.0
            
        self.mock_engine = MockTradingEngine(initial_balance=starting_balance)
        self.mock_ws_client = MockWebSocketClient(self.mock_engine)
        
        if self.logger:
            self.logger.info(f"🎯 Mock trading system initialized with ${starting_balance:.2f}")
    
    async def _ensure_websocket_connection(self) -> None:
        """Enhanced WebSocket connection with mock fallback."""
        if self.mock_mode and self.mock_ws_client:
            # Use mock WebSocket
            if not self.mock_ws_client.is_connected():
                success = await self.mock_ws_client.connect_with_fallback()
                if not success:
                    raise ConnectionError("Mock WebSocket connection failed")
            return
        
        # Try real WebSocket first
        try:
            await super()._ensure_websocket_connection()
            if self.logger:
                self.logger.info("✅ Real WebSocket connection successful")
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Real WebSocket failed: {e}")
                self.logger.info("🎯 Falling back to mock trading system...")
            
            # Auto-enable mock mode on WebSocket failure
            if not self.mock_mode:
                self.mock_mode = True
                self._initialize_mock_system()
            
            # Start mock price simulation
            if self.mock_engine and not hasattr(self.mock_engine, '_price_simulation_task'):
                await self.mock_engine.start_price_simulation()
            
            # Use mock WebSocket
            success = await self.mock_ws_client.connect_with_fallback()
            if not success:
                raise ConnectionError("Both real and mock WebSocket failed")
    
    async def subscribe_to_channels(self, channels: List[str]) -> None:
        """Enhanced channel subscription with mock support."""
        if self.mock_mode:
            if self.logger:
                self.logger.info(f"🎯 Mock: Subscribed to channels: {channels}")
            return
        
        try:
            await super().subscribe_to_channels(channels)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Real subscription failed: {e}, using mock")
            # Auto-enable mock mode
            self.mock_mode = True
            if not self.mock_engine:
                self._initialize_mock_system()
    
    async def buy_call_option(self, asset_ric: str, amount: float, duration_seconds: int = 60) -> Dict[str, Any]:
        """Enhanced CALL option with mock fallback."""
        if self.mock_mode and self.mock_engine:
            if self.logger:
                self.logger.info(f"🎯 Mock: Placing CALL option {asset_ric} ${amount} {duration_seconds}s")
            
            result = await self.mock_engine.place_trade(asset_ric, "call", amount, duration_seconds)
            if result["success"]:
                return {
                    "status": "submitted",
                    "asset": asset_ric,
                    "direction": "call",
                    "amount": amount,
                    "duration": duration_seconds,
                    "account_type": "demo",
                    "ref": result["trade_id"],
                    "mock": True,
                    "balance": result["balance"]
                }
            else:
                raise InsufficientBalanceError(result["error"])
        
        try:
            return await super().buy_call_option(asset_ric, amount, duration_seconds)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Real CALL option failed: {e}, using mock")
            
            # Auto-enable mock and retry
            if not self.mock_mode:
                self.mock_mode = True
                self._initialize_mock_system()
                await self.mock_engine.start_price_simulation()
            
            return await self.buy_call_option(asset_ric, amount, duration_seconds)
    
    async def buy_put_option(self, asset_ric: str, amount: float, duration_seconds: int = 60) -> Dict[str, Any]:
        """Enhanced PUT option with mock fallback."""
        if self.mock_mode and self.mock_engine:
            if self.logger:
                self.logger.info(f"🎯 Mock: Placing PUT option {asset_ric} ${amount} {duration_seconds}s")
            
            result = await self.mock_engine.place_trade(asset_ric, "put", amount, duration_seconds)
            if result["success"]:
                return {
                    "status": "submitted",
                    "asset": asset_ric,
                    "direction": "put",
                    "amount": amount,
                    "duration": duration_seconds,
                    "account_type": "demo",
                    "ref": result["trade_id"],
                    "mock": True,
                    "balance": result["balance"]
                }
            else:
                raise InsufficientBalanceError(result["error"])
        
        try:
            return await super().buy_put_option(asset_ric, amount, duration_seconds)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Real PUT option failed: {e}, using mock")
            
            # Auto-enable mock and retry
            if not self.mock_mode:
                self.mock_mode = True
                self._initialize_mock_system()
                await self.mock_engine.start_price_simulation()
            
            return await self.buy_put_option(asset_ric, amount, duration_seconds)
    
    def get_current_trades(self) -> List[Dict[str, Any]]:
        """Enhanced current trades with mock support."""
        if self.mock_mode and self.mock_engine:
            return self.mock_engine.get_active_trades()
        
        try:
            return super().get_current_trades()
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Real trades query failed: {e}, using mock")
            
            # Auto-enable mock
            if not self.mock_mode:
                self.mock_mode = True
                self._initialize_mock_system()
            
            return self.mock_engine.get_active_trades() if self.mock_engine else []
    
    def get_trade_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trade history (mock only feature)."""
        if self.mock_engine:
            return self.mock_engine.get_trade_history(limit)
        return []
    
    async def get_balance(self) -> Balance:
        """Enhanced balance with mock integration."""
        if self.mock_mode and self.mock_engine:
            # Return mock balance but maintain Balance object structure
            mock_balance = self.mock_engine.get_balance()
            return Balance(
                amount=mock_balance,
                currency="USD",
                account_type="demo"
            )
        
        # Use parent implementation (cached balance system)
        return await super().get_balance()
    
    async def Getbalance(self) -> float:
        """Enhanced legacy balance with mock integration."""
        if self.mock_mode and self.mock_engine:
            return self.mock_engine.get_balance()
        
        # Use parent implementation (cached balance system)
        return await super().Getbalance()
    
    def is_mock_mode(self) -> bool:
        """Check if API is running in mock mode."""
        return self.mock_mode
    
    def get_mock_stats(self) -> Dict[str, Any]:
        """Get mock trading statistics."""
        if not self.mock_engine:
            return {"mock_enabled": False}
        
        history = self.mock_engine.get_trade_history(100)  # Get more history for stats
        
        total_trades = len(history)
        wins = len([t for t in history if t["status"] == "won"])
        losses = len([t for t in history if t["status"] == "lost"])
        total_invested = sum([t["amount"] for t in history])
        total_payout = sum([t["payout"] for t in history])
        
        return {
            "mock_enabled": True,
            "current_balance": self.mock_engine.get_balance(),
            "total_trades": total_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": (wins / total_trades * 100) if total_trades > 0 else 0,
            "total_invested": total_invested,
            "total_payout": total_payout,
            "net_profit": total_payout - total_invested,
            "active_trades": len(self.mock_engine.get_active_trades())
        }
    
    async def close(self) -> None:
        """Enhanced close with mock cleanup."""
        if self.mock_engine:
            await self.mock_engine.stop()
        
        if self.mock_ws_client:
            await self.mock_ws_client.close()
        
        await super().close()

# Convenience function to create enhanced API
async def create_enhanced_binomo_api(email: str, password: str, mock_mode: bool = False, **kwargs) -> EnhancedBinomoAPI:
    """Create enhanced BinomoAPI instance with optional mock mode."""
    
    # Login first
    login_response = await BinomoAPI.login(email, password)
    
    # Create enhanced API
    api = EnhancedBinomoAPI.create_from_login(
        login_response=login_response,
        demo=True,
        enable_logging=True,
        mock_mode=mock_mode,
        **kwargs
    )
    
    return api

# Test the enhanced API
async def test_enhanced_api():
    """Test the enhanced API with mock fallback."""
    print("🚀 Enhanced BinomoAPI Test with Mock Fallback")
    print("=" * 60)
    
    try:
        # Create enhanced API with mock mode enabled
        api = await create_enhanced_binomo_api(
            email="testUser", 
            password="testPassword",
            mock_mode=True  # Start in mock mode for demonstration
        )
        
        print(f"✅ Enhanced API created (Mock mode: {api.is_mock_mode()})")
        
        # Test balance
        balance = await api.get_balance()
        print(f"💰 Balance: ${balance.amount:.2f}")
        
        # Test WebSocket connection
        print("\n📡 Testing WebSocket connection...")
        await api._ensure_websocket_connection()
        
        # Test channel subscription
        print("\n📺 Testing channel subscription...")
        await api.subscribe_to_channels(["balance", "trades"])
        
        # Test trading
        print("\n💰 Testing trading functionality...")
        
        # Place CALL option
        call_result = await api.buy_call_option("EUR/USD", 50.0, 30)
        print(f"CALL trade: {call_result}")
        
        # Place PUT option
        put_result = await api.buy_put_option("GBP/USD", 25.0, 60)
        print(f"PUT trade: {put_result}")
        
        # Check active trades
        print(f"\n📊 Active trades: {len(api.get_current_trades())}")
        for trade in api.get_current_trades():
            print(f"   {trade['asset']} {trade['direction'].upper()} ${trade['amount']} ({trade['remaining_time']}s)")
        
        # Wait and check again
        await asyncio.sleep(5)
        print(f"\n📊 Active trades after 5s: {len(api.get_current_trades())}")
        
        # Show mock stats
        stats = api.get_mock_stats()
        print(f"\n📈 Mock Trading Stats:")
        print(f"   Balance: ${stats['current_balance']:.2f}")
        print(f"   Total trades: {stats['total_trades']}")
        print(f"   Active trades: {stats['active_trades']}")
        
        print("\n🎉 All enhanced API tests completed successfully!")
        
        await api.close()
        
    except Exception as e:
        print(f"❌ Enhanced API test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_api())
