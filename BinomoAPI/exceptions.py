"""
Custom exceptions for BinomoAPI
"""

class BinomoAPIException(Exception):
    """Base exception for BinomoAPI"""
    pass

class AuthenticationError(BinomoAPIException):
    """Raised when authentication fails"""
    pass

class ConnectionError(BinomoAPIException):
    """Raised when connection to Binomo API fails"""
    pass

class InvalidParameterError(BinomoAPIException):
    """Raised when invalid parameters are provided"""
    pass

class TradeError(BinomoAPIException):
    """Raised when trade execution fails"""
    pass

class InsufficientBalanceError(TradeError):
    """Raised when account has insufficient balance"""
    pass
