#!/usr/bin/env python3
"""
Mock Trading System for BinomoAPI Development.
Since WebSocket authentication is server-side restricted, this provides a complete
mock trading environment for development and testing purposes.
"""

import asyncio
import json
import time
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class TradeDirection(Enum):
    CALL = "call"
    PUT = "put"

class TradeStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"

@dataclass
class MockTrade:
    """Mock trade object for development."""
    id: str
    asset: str
    direction: TradeDirection
    amount: float
    duration: int
    start_time: float
    end_time: float
    start_price: float
    end_price: Optional[float] = None
    status: TradeStatus = TradeStatus.PENDING
    payout: float = 0.0

class MockTradingEngine:
    """Mock trading engine that simulates Binomo trading behavior."""
    
    def __init__(self, initial_balance: float = 8000.0):
        self.balance = initial_balance
        self.trades: Dict[str, MockTrade] = {}
        self.active_trades: List[str] = []
        self.price_data: Dict[str, float] = {}
        self.payout_percentage = 0.85  # 85% payout on wins
        
        # Initialize mock price data
        self._initialize_mock_prices()
        
        # Start price simulation
        self._price_simulation_task = None
    
    def _initialize_mock_prices(self):
        """Initialize mock price data for common assets."""
        self.price_data = {
            "EUR/USD": 1.0845 + random.uniform(-0.01, 0.01),
            "GBP/USD": 1.2651 + random.uniform(-0.01, 0.01),
            "USD/JPY": 149.23 + random.uniform(-1.0, 1.0),
            "AUD/USD": 0.6543 + random.uniform(-0.01, 0.01),
            "USD/CAD": 1.3421 + random.uniform(-0.01, 0.01),
            "XBT/USD": 43250.0 + random.uniform(-500, 500),
            "ETH/USD": 2450.0 + random.uniform(-50, 50),
            "ADA/USD": 0.4523 + random.uniform(-0.05, 0.05),
        }
    
    async def start_price_simulation(self):
        """Start realistic price simulation."""
        self._price_simulation_task = asyncio.create_task(self._simulate_prices())
    
    async def _simulate_prices(self):
        """Simulate realistic price movements."""
        while True:
            try:
                for asset in self.price_data:
                    # Small random price movements
                    change_percent = random.uniform(-0.002, 0.002)  # ±0.2%
                    self.price_data[asset] *= (1 + change_percent)
                
                # Check for trade expirations
                await self._check_trade_expirations()
                
                await asyncio.sleep(1)  # Update every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Price simulation error: {e}")
                await asyncio.sleep(1)
    
    async def _check_trade_expirations(self):
        """Check for expired trades and calculate results."""
        current_time = time.time()
        expired_trades = []
        
        for trade_id in self.active_trades:
            trade = self.trades[trade_id]
            if current_time >= trade.end_time:
                expired_trades.append(trade_id)
        
        for trade_id in expired_trades:
            await self._settle_trade(trade_id)
    
    async def _settle_trade(self, trade_id: str):
        """Settle an expired trade."""
        trade = self.trades[trade_id]
        current_price = self.price_data.get(trade.asset, trade.start_price)
        
        trade.end_price = current_price
        trade.status = TradeStatus.ACTIVE  # Mark as completed
        
        # Determine win/loss
        if trade.direction == TradeDirection.CALL:
            won = current_price > trade.start_price
        else:  # PUT
            won = current_price < trade.start_price
        
        if won:
            trade.status = TradeStatus.WON
            trade.payout = trade.amount * (1 + self.payout_percentage)
            self.balance += trade.payout
            print(f"🎉 Trade {trade_id} WON! Payout: ${trade.payout:.2f}")
        else:
            trade.status = TradeStatus.LOST
            trade.payout = 0.0
            print(f"😞 Trade {trade_id} LOST. Amount lost: ${trade.amount:.2f}")
        
        # Remove from active trades
        if trade_id in self.active_trades:
            self.active_trades.remove(trade_id)
    
    async def place_trade(self, asset: str, direction: str, amount: float, duration: int) -> Dict[str, Any]:
        """Place a mock trade."""
        if self.balance < amount:
            return {
                "success": False,
                "error": f"Insufficient balance: ${self.balance:.2f} < ${amount:.2f}"
            }
        
        # Generate trade ID
        trade_id = f"mock_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Get current price
        current_price = self.price_data.get(asset, 1.0)
        if asset not in self.price_data:
            # Add new asset with random price
            self.price_data[asset] = random.uniform(0.5, 2.0)
            current_price = self.price_data[asset]
        
        # Create trade
        trade = MockTrade(
            id=trade_id,
            asset=asset,
            direction=TradeDirection(direction.lower()),
            amount=amount,
            duration=duration,
            start_time=time.time(),
            end_time=time.time() + duration,
            start_price=current_price,
            status=TradeStatus.ACTIVE
        )
        
        # Deduct amount from balance
        self.balance -= amount
        
        # Store trade
        self.trades[trade_id] = trade
        self.active_trades.append(trade_id)
        
        print(f"📈 Mock trade placed: {direction.upper()} {asset} ${amount} for {duration}s")
        print(f"   Trade ID: {trade_id}")
        print(f"   Start price: {current_price:.6f}")
        print(f"   Remaining balance: ${self.balance:.2f}")
        
        return {
            "success": True,
            "trade_id": trade_id,
            "asset": asset,
            "direction": direction,
            "amount": amount,
            "duration": duration,
            "start_price": current_price,
            "balance": self.balance
        }
    
    def get_balance(self) -> float:
        """Get current mock balance."""
        return self.balance
    
    def get_active_trades(self) -> List[Dict[str, Any]]:
        """Get list of active trades."""
        active = []
        for trade_id in self.active_trades:
            trade = self.trades[trade_id]
            remaining_time = max(0, trade.end_time - time.time())
            current_price = self.price_data.get(trade.asset, trade.start_price)
            
            # Calculate current P&L
            if trade.direction == TradeDirection.CALL:
                winning = current_price > trade.start_price
            else:
                winning = current_price < trade.start_price
            
            active.append({
                "id": trade.id,
                "asset": trade.asset,
                "direction": trade.direction.value,
                "amount": trade.amount,
                "start_price": trade.start_price,
                "current_price": current_price,
                "remaining_time": int(remaining_time),
                "winning": winning
            })
        
        return active
    
    def get_trade_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trade history."""
        completed_trades = [
            trade for trade in self.trades.values() 
            if trade.status in [TradeStatus.WON, TradeStatus.LOST]
        ]
        
        # Sort by start time (newest first)
        completed_trades.sort(key=lambda t: t.start_time, reverse=True)
        
        history = []
        for trade in completed_trades[:limit]:
            history.append({
                "id": trade.id,
                "asset": trade.asset,
                "direction": trade.direction.value,
                "amount": trade.amount,
                "start_price": trade.start_price,
                "end_price": trade.end_price,
                "status": trade.status.value,
                "payout": trade.payout,
                "profit": trade.payout - trade.amount if trade.status == TradeStatus.WON else -trade.amount
            })
        
        return history
    
    async def stop(self):
        """Stop the mock trading engine."""
        if self._price_simulation_task:
            self._price_simulation_task.cancel()
            try:
                await self._price_simulation_task
            except asyncio.CancelledError:
                pass

class MockWebSocketClient:
    """Mock WebSocket client that simulates successful connections."""
    
    def __init__(self, trading_engine: MockTradingEngine):
        self.trading_engine = trading_engine
        self._connected = False
        self.logger = None
    
    async def connect_with_fallback(self) -> bool:
        """Simulate successful WebSocket connection."""
        print("🔌 Mock WebSocket: Simulating successful connection...")
        await asyncio.sleep(0.5)  # Simulate connection delay
        self._connected = True
        print("✅ Mock WebSocket: Connected successfully!")
        return True
    
    async def send(self, message: str):
        """Simulate sending WebSocket message."""
        if not self._connected:
            raise ConnectionError("Mock WebSocket not connected")
        
        print(f"📤 Mock WebSocket: Sent message: {message[:100]}...")
        await asyncio.sleep(0.1)  # Simulate network delay
    
    async def close(self):
        """Simulate closing WebSocket."""
        self._connected = False
        print("🔌 Mock WebSocket: Connection closed")
    
    def is_connected(self) -> bool:
        """Check if mock WebSocket is connected."""
        return self._connected

async def demo_mock_trading_system():
    """Demonstrate the mock trading system."""
    print("🎯 Mock Trading System Demo")
    print("=" * 50)
    
    # Create mock trading engine
    engine = MockTradingEngine(initial_balance=10000.0)
    
    print(f"💰 Starting balance: ${engine.get_balance():.2f}")
    
    # Start price simulation
    await engine.start_price_simulation()
    
    try:
        # Place some demo trades
        print("\n📈 Placing demo trades...")
        
        # Place CALL trade
        result1 = await engine.place_trade("EUR/USD", "call", 50.0, 30)
        print(f"Trade 1: {result1}")
        
        await asyncio.sleep(2)
        
        # Place PUT trade
        result2 = await engine.place_trade("GBP/USD", "put", 25.0, 60)
        print(f"Trade 2: {result2}")
        
        await asyncio.sleep(2)
        
        # Place Bitcoin trade
        result3 = await engine.place_trade("XBT/USD", "call", 100.0, 45)
        print(f"Trade 3: {result3}")
        
        # Monitor trades for a while
        print("\n👁️ Monitoring trades...")
        for i in range(15):
            active = engine.get_active_trades()
            print(f"\n⏰ Time {i+1}/15 - Active trades: {len(active)}")
            for trade in active:
                status = "📈 Winning" if trade["winning"] else "📉 Losing"
                print(f"   {trade['id']}: {trade['asset']} {trade['direction'].upper()} "
                      f"${trade['amount']} - {status} ({trade['remaining_time']}s left)")
            
            await asyncio.sleep(3)
        
        # Show final results
        print(f"\n💰 Final balance: ${engine.get_balance():.2f}")
        
        history = engine.get_trade_history()
        print(f"\n📊 Trade History ({len(history)} trades):")
        for trade in history:
            status_emoji = "🎉" if trade["status"] == "won" else "😞"
            print(f"   {status_emoji} {trade['asset']} {trade['direction'].upper()} "
                  f"${trade['amount']} -> {trade['status'].upper()} "
                  f"(P&L: ${trade['profit']:+.2f})")
        
    finally:
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(demo_mock_trading_system())
