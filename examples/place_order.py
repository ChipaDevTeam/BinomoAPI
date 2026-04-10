import asyncio
import dotenv
import os

from BinomoAPI import BinomoAPI
from BinomoAPI.exceptions import AuthenticationError

dotenv.load_dotenv()

EMAIL = os.getenv("BINOMO_EMAIL")
PASSWORD = os.getenv("BINOMO_PASSWORD")


async def main():
    try:
        login_response = BinomoAPI.login(EMAIL, PASSWORD)
        session = login_response._session
        device_id = session.cookies.get("device_id")
        print(f"Device ID: {device_id}")

        async with BinomoAPI(
            auth_token=login_response.authtoken,
            demo=True,
            enable_logging=True,
            device_id = device_id
        ) as api:
            
            balance = await api.get_balance()
            print(f"Balance: ${balance.amount:.2f}")
            
            result = await api.place_call_option(
                asset="EURO",
                duration_seconds=60,
                amount=1000,
                use_demo=True
            )

            print(f"Trade placed: {result}")

            await asyncio.sleep(15) 
            balance = await api.get_balance()
            print(f"Balance after trade: ${balance.amount:.2f}")
            
    except AuthenticationError as e:
        print(f"Login failed: {e}")

asyncio.run(main())
