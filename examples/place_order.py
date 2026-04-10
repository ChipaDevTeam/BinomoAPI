import asyncio
import dotenv
import os
import json

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
                asset="Z-CRY/IDX",
                duration_seconds=60,
                amount=100000,
                use_demo=True
            )

            print(f"Trade placed: {result}")

            # Wait for server response
            await asyncio.sleep(3)
            
            # Print all received messages
            if hasattr(api, '_ws_client') and api._ws_client:
                print(f"\n=== Server responses ({len(api._ws_client._last_messages)}) ===")
                for msg in api._ws_client._last_messages:
                    print(json.dumps(msg, indent=2))
            balance = await api.get_balance()
            print(f"Balance after trade: ${balance.amount:.2f}")
            
    except AuthenticationError as e:
        print(f"Login failed: {e}")

asyncio.run(main())
