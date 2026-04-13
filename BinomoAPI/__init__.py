"""
BinomoAPI - Professional Python Client for Binomo Trading Platform

A comprehensive, production-ready Python client for binary options trading
with full type safety, async support, and professional error handling.

Built by ChipaDevTeam | Try ChipaEditor: https://chipaeditor.com/?utm_source=pypi&utm_medium=package&utm_campaign=binomo_api&utm_term=init&utm_content=docstring
"""

from .api import BinomoAPI
from .exceptions import (
    BinomoAPIException,
    AuthenticationError,
    ConnectionError,
    InvalidParameterError,
    TradeError,
    InsufficientBalanceError
)
from .models import LoginResponse, Asset, Balance, TradeOrder
from .constants import TRADE_DIRECTIONS, ACCOUNT_TYPES, OPTION_TYPES

__version__ = "2.0.1"
__author__ = "BinomoAPI Team"
__email__ = "support@binomoapi.com"

__all__ = [
    # Main API class
    "BinomoAPI",
    
    # Exceptions
    "BinomoAPIException",
    "AuthenticationError", 
    "ConnectionError",
    "InvalidParameterError",
    "TradeError",
    "InsufficientBalanceError",
    
    # Data models
    "LoginResponse",
    "Asset", 
    "Balance",
    "TradeOrder",
    
    # Constants
    "TRADE_DIRECTIONS",
    "ACCOUNT_TYPES", 
    "OPTION_TYPES",
]