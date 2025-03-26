from BinomoAPI.api import BinomoAPI
import asyncio
import time
import os
import dotenv

dotenv.load_dotenv()

AuthToken = os.getenv("AuthToken")
device_id = os.getenv("device_id")

async def main():
    api = BinomoAPI(AuthToken, device_id, demo=True, AddLogging=True)
    balance = await api.Getbalance()
    print(balance)
    time.sleep(1)
    api.Call("Z-CRY/IDX", 60, 1000, is_demo=True)
    time.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
