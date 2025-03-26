from BinomoAPI.api import BinomoAPI
import asyncio
import time

AuthToken = "ff459844-6a5f-4ff0-ab3c-ad3df2df1132"
device_id = "7c1d96c0f3da0549db91a550a676dbd1"

async def main():
    api = BinomoAPI(AuthToken, device_id, demo=True, AddLogging=True)
    balance = await api.Getbalance()
    print(balance)
    time.sleep(1)
    api.Call("Z-CRY/IDX", 60, 1000, is_demo=True)
    time.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
