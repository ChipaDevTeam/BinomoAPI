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

    # Small delay to ensure login session is fully established
    await asyncio.sleep(0.1)

    # Create API client using the login session for continuity
    api = BinomoAPI.create_from_login(
        login_response=login_response,
        device_id=login_response.user_id,
        demo=True,
    )
    print("BinomoAPI client initialized successfully")
    
    try:
        balance = await api.Getbalance()
        print(f"Demo Balance: ${balance}")
    except Exception as e:
        print(f"Balance error: {e}")
    
    # Clean up
    await api.close()

if __name__ == "__main__":
    asyncio.run(main())