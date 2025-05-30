#!/usr/bin/env python3
"""
Professional example of how to use the BinomoAPI client

This example demonstrates:
- Authentication with proper error handling
- Using the API as a context manager
- Balance checking
- Placing trades with validation
- Proper logging and exception handling
"""

import asyncio
import logging
from BinomoAPI.api import BinomoAPI
from BinomoAPI.exceptions import (
    AuthenticationError, 
    ConnectionError, 
    InvalidParameterError,
    InsufficientBalanceError,
    TradeError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main example function demonstrating BinomoAPI usage."""
    
    # Replace with your actual credentials
    email = "your_email@example.com"
    password = "your_password"
    device_id = "1b6290ce761c82f3a97189d35d2ed138"
    
    try:
        # Step 1: Authenticate
        logger.info("Attempting to login...")
        login_response = BinomoAPI.login(email, password, device_id)
        
        if not login_response:
            logger.error("Login failed")
            return
            
        logger.info(f"Login successful! User ID: {login_response.user_id}")
        
        # Step 2: Create API client with context manager for proper cleanup
        async with BinomoAPI(
            auth_token=login_response.authtoken,
            device_id=device_id,
            demo=True,  # Use demo account for safety
            enable_logging=True,
            log_level=logging.INFO
        ) as api:
            
            logger.info("BinomoAPI client initialized successfully")
            
            # Step 3: Check available assets
            assets = api.get_available_assets()
            logger.info(f"Available assets: {len(assets)}")
            
            # Show first few assets
            for asset in assets[:5]:
                logger.info(f"Asset: {asset.name} (RIC: {asset.ric})")
            
            # Step 4: Check account balance
            balance = await api.get_balance()
            logger.info(f"Current balance: ${balance.amount:.2f} ({balance.account_type})")
            
            # Step 5: Place a demo trade (if balance is sufficient)
            if balance.amount >= 1.0:  # Minimum $1 trade
                try:
                    # Place a CALL option
                    trade_result = await api.place_call_option(
                        asset="EUR/USD",  # Popular forex pair
                        duration_seconds=60,  # 1 minute
                        amount=1.0,  # $1
                        use_demo=True
                    )
                    
                    logger.info(f"Trade placed successfully: {trade_result}")
                    
                    # Place a PUT option
                    trade_result = await api.place_put_option(
                        asset="EUR/USD",
                        duration_seconds=120,  # 2 minutes
                        amount=1.0,
                        use_demo=True
                    )
                    
                    logger.info(f"PUT trade placed successfully: {trade_result}")
                    
                except InvalidParameterError as e:
                    logger.error(f"Invalid trade parameters: {e}")
                except InsufficientBalanceError as e:
                    logger.error(f"Insufficient balance: {e}")
                except TradeError as e:
                    logger.error(f"Trade execution failed: {e}")
            else:
                logger.warning(f"Balance too low for trading: ${balance.amount:.2f}")
                
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
    except ConnectionError as e:
        logger.error(f"Connection failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def example_with_traditional_syntax():
    """Example using traditional API instantiation (not recommended)."""
    
    try:
        # Login
        login_response = BinomoAPI.login("email", "password")
        if not login_response:
            print("Login failed")
            return
            
        # Create API instance
        api = BinomoAPI(
            auth_token=login_response.authtoken,
            device_id="device_id",
            demo=True,
            enable_logging=True
        )
        
        # Use API...
        # (Remember to call api.close() when done)
        
        # Close connection
        api.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
