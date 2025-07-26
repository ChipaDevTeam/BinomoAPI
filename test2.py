from BinomoAPI import BinomoAPI

import asyncio
import time
import os
import dotenv
import logging

dotenv.load_dotenv()

email = os.getenv("email")
password = os.getenv("password")

async def main():
    login_response = BinomoAPI.login(email, password)
    print(f"Login successful! {login_response}")
    print(f"Auth Token: {login_response.authtoken}")
    print(f"User ID: {login_response.user_id}")
    
    # Check if balance was captured during login
    if hasattr(login_response, 'balance') and login_response.balance is not None:
        print(f"Balance from login: ${login_response.balance}")

    # NO DELAY - Test balance immediately after login but before creating API instance
    print("\n=== Testing balance IMMEDIATELY after login (no delay) ===")
    balance_test = BinomoAPI._test_balance_with_session(
        login_response._session, 
        login_response.authtoken, 
        login_response.user_id
    )
    print(f"Immediate balance test result: {balance_test}")

    # Create API client using the login session for continuity
    print("\n=== Creating BinomoAPI instance ===")
    api = BinomoAPI.create_from_login(
        login_response=login_response,
        device_id=login_response.user_id,
        demo=True,
    )
    print("BinomoAPI client initialized successfully")
    
    # Test balance again
    print("\n=== Testing balance after API instance creation ===")
    try:
        # Try the modern get_balance method instead of legacy Getbalance
        balance_obj = await api.get_balance()
        print(f"Demo Balance Object: {balance_obj}")
        print(f"Demo Balance: ${balance_obj.amount}")  # Use 'amount' field, not 'balance'
    except Exception as e:
        print(f"get_balance error: {e}")
        # Fallback to legacy method
        try:
            balance = await api.Getbalance()
            print(f"Legacy Demo Balance: ${balance}")
        except Exception as e2:
            print(f"Legacy balance error: {e2}")
    
    # Clean up
    await api.close()

if __name__ == "__main__":
    asyncio.run(main())