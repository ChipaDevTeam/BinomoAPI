# Error Handling Guide

Comprehensive guide to handling errors and exceptions in BinomoAPI.

## 🎯 Exception Hierarchy

BinomoAPI provides a comprehensive exception hierarchy for precise error handling:

```python
BinomoAPIException
├── AuthenticationError   # Login and authentication issues
├── ConnectionError      # Network and connectivity problems
├── InvalidParameterError # Invalid input parameters
├── TradeError          # Trading operation failures
└── InsufficientBalanceError # Insufficient funds for trading
```

## 🚨 Common Errors

### Authentication Errors

```python
from BinomoAPI import BinomoAPI, AuthenticationError

try:
    login_response = BinomoAPI.login(
        "email@example.com",
        "password"
    )
except AuthenticationError as e:
    print(f"Login failed: {e}")
    # Handle invalid credentials
    # Possible actions:
    # 1. Retry with correct credentials
    # 2. Request password reset
    # 3. Check account status
```

### Connection Errors

```python
from BinomoAPI import BinomoAPI, ConnectionError

async def handle_connection_issues():
    try:
        async with BinomoAPI(...) as api:
            await api.get_balance()
    except ConnectionError as e:
        print(f"Connection error: {e}")
        # Handle connection issues:
        # 1. Check internet connection
        # 2. Verify API endpoint
        # 3. Implement retry logic
```

### Trade Errors

```python
from BinomoAPI import BinomoAPI, TradeError

async def handle_trade_errors(api: BinomoAPI):
    try:
        result = await api.place_call_option(
            asset="EUR/USD",
            duration_seconds=60,
            amount=5.0
        )
    except TradeError as e:
        print(f"Trade failed: {e}")
        # Handle trade failure:
        # 1. Verify asset availability
        # 2. Check market conditions
        # 3. Validate parameters
```

### Balance Errors

```python
from BinomoAPI import BinomoAPI, InsufficientBalanceError

async def handle_balance_errors(api: BinomoAPI):
    try:
        await api.place_call_option(
            asset="EUR/USD",
            duration_seconds=60,
            amount=1000.0
        )
    except InsufficientBalanceError as e:
        print(f"Insufficient funds: {e}")
        # Handle insufficient balance:
        # 1. Check current balance
        # 2. Adjust trade amount
        # 3. Add funds if needed
```

## 🛡️ Best Practices

### Comprehensive Error Handling

```python
from BinomoAPI.exceptions import (
    AuthenticationError,
    ConnectionError,
    TradeError,
    InsufficientBalanceError,
    InvalidParameterError
)

async def professional_error_handling():
    try:
        # Login
        login_response = BinomoAPI.login(
            "email@example.com",
            "password"
        )
        
        async with BinomoAPI(
            auth_token=login_response.authtoken,
            device_id=login_response.user_id,
            demo=True
        ) as api:
            try:
                # Trading operations
                result = await api.place_call_option(
                    asset="EUR/USD",
                    duration_seconds=60,
                    amount=5.0
                )
                
            except InsufficientBalanceError as e:
                logging.error(f"Balance too low: {e}")
                # Implement recovery strategy
                
            except TradeError as e:
                logging.error(f"Trade failed: {e}")
                # Analyze failure reason
                
            except InvalidParameterError as e:
                logging.error(f"Invalid parameters: {e}")
                # Correct parameters
                
    except AuthenticationError as e:
        logging.error(f"Authentication failed: {e}")
        # Handle auth issues
        
    except ConnectionError as e:
        logging.error(f"Connection failed: {e}")
        # Implement retry logic
```

### Retry Logic

```python
import asyncio
from typing import Callable, Any

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> Any:
    """
    Retry a function with exponential backoff.
    """
    retries = 0
    delay = initial_delay
    
    while True:
        try:
            return await func()
            
        except (ConnectionError, TradeError) as e:
            retries += 1
            if retries >= max_retries:
                raise
            
            logging.warning(
                f"Attempt {retries} failed: {e}. "
                f"Retrying in {delay} seconds..."
            )
            
            await asyncio.sleep(delay)
            delay *= 2  # Exponential backoff
```

### Error Logging

```python
import logging

def setup_error_logging():
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    file_handler = logging.FileHandler('errors.log')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    
    # Configure logger
    logger = logging.getLogger('BinomoAPI')
    logger.setLevel(logging.ERROR)
    logger.addHandler(file_handler)
```

## 🔍 Error Analysis

### Trade Error Analysis

```python
async def analyze_trade_error(
    api: BinomoAPI,
    error: TradeError
) -> dict:
    """
    Analyze trade errors and suggest solutions.
    """
    analysis = {
        "error_type": type(error).__name__,
        "message": str(error),
        "suggestions": []
    }
    
    if "insufficient balance" in str(error).lower():
        balance = await api.get_balance()
        analysis["suggestions"].append(
            f"Current balance (${balance.amount}) "
            "is too low for trade"
        )
    
    elif "invalid asset" in str(error).lower():
        assets = api.get_available_assets()
        analysis["suggestions"].append(
            "Asset may be temporarily unavailable. "
            f"Available assets: {[a.name for a in assets]}"
        )
    
    elif "market closed" in str(error).lower():
        analysis["suggestions"].append(
            "Market is currently closed. "
            "Check trading hours."
        )
    
    return analysis
```

### Connection Error Analysis

```python
async def analyze_connection_error(
    error: ConnectionError
) -> dict:
    """
    Analyze connection errors and provide solutions.
    """
    import socket
    
    analysis = {
        "error_type": type(error).__name__,
        "message": str(error),
        "network_status": None,
        "suggestions": []
    }
    
    # Check internet connection
    try:
        socket.create_connection(("8.8.8.8", 53))
        analysis["network_status"] = "connected"
    except OSError:
        analysis["network_status"] = "disconnected"
        analysis["suggestions"].append(
            "No internet connection detected"
        )
    
    # Analyze error message
    if "timeout" in str(error).lower():
        analysis["suggestions"].append(
            "Request timed out. Check network speed."
        )
    elif "refused" in str(error).lower():
        analysis["suggestions"].append(
            "Connection refused. Service may be down."
        )
    
    return analysis
```

## 🔄 Recovery Strategies

### Session Recovery

```python
async def recover_session(api: BinomoAPI) -> bool:
    """
    Attempt to recover a failed session.
    """
    try:
        # Re-authenticate
        login_response = BinomoAPI.login(
            api.email,
            api.password
        )
        
        # Update credentials
        api.auth_token = login_response.authtoken
        api.device_id = login_response.user_id
        
        # Verify recovery
        await api.get_balance()
        return True
        
    except Exception as e:
        logging.error(f"Session recovery failed: {e}")
        return False
```

### Trade Recovery

```python
async def recover_failed_trade(
    api: BinomoAPI,
    original_params: dict
) -> bool:
    """
    Attempt to recover a failed trade.
    """
    try:
        # Verify account status
        balance = await api.get_balance()
        if balance.amount < original_params["amount"]:
            logging.error("Insufficient balance for recovery")
            return False
        
        # Verify asset status
        assets = api.get_available_assets()
        asset = next(
            (a for a in assets 
             if a.name == original_params["asset"]),
            None
        )
        if not asset or not asset.is_active:
            logging.error("Asset not available for recovery")
            return False
        
        # Retry trade
        await api.place_call_option(**original_params)
        return True
        
    except Exception as e:
        logging.error(f"Trade recovery failed: {e}")
        return False
```

Remember to always implement appropriate error handling for your specific use case!
