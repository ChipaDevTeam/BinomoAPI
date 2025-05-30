"""
Data models for BinomoAPI
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class LoginResponse:
    """Response data from login request"""
    authtoken: str
    user_id: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoginResponse':
        """Create LoginResponse from dictionary"""
        return cls(
            authtoken=data['authtoken'],
            user_id=data['user_id']
        )

@dataclass
class Asset:
    """Asset information"""
    name: str
    ric: str
    is_active: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Asset':
        """Create Asset from dictionary"""
        return cls(
            name=data['name'],
            ric=data['ric'],
            is_active=data.get('is_active', True)
        )

@dataclass
class Balance:
    """Account balance information"""
    amount: float
    currency: str
    account_type: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Balance':
        """Create Balance from dictionary"""
        return cls(
            amount=data['amount'] / 100,  # Convert from cents
            currency=data.get('currency', 'USD'),
            account_type=data['account_type']
        )

@dataclass
class TradeOrder:
    """Binary options trade order"""
    asset_ric: str
    direction: str
    amount: float
    duration_seconds: int
    option_type: str = "turbo"
    account_type: str = "demo"
    tournament_id: Optional[str] = None
    
    def to_payload(self, ref: int, created_at: Optional[int] = None) -> Dict[str, Any]:
        """Convert to WebSocket payload format"""
        if created_at is None:
            created_at = int(datetime.now().timestamp())
            
        expire_at = created_at + (self.duration_seconds * 1_000_000)
        
        return {
            "topic": "bo",
            "event": "create",
            "payload": {
                "created_at": created_at,
                "ric": self.asset_ric,
                "deal_type": self.account_type,
                "expire_at": expire_at,
                "option_type": self.option_type,
                "trend": self.direction,
                "tournament_id": self.tournament_id,
                "is_state": False,
                "amount": self.amount
            },
            "ref": ref,
            "join_ref": "9"
        }
