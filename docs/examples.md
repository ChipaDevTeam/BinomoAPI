---
title: Examples
description: Copy-paste Python examples for Binomo trading bots built with BinomoAPI, including scheduled trades, signal bots with stop-loss limits, multi-asset trading and asset discovery.
nav_order: 5
redirect_from:
  - /advanced-usage
  - /advanced-usage.html
---

# Binomo trading bot examples
{: .no_toc }

Complete scripts you can run as they are. Each one uses the **demo account**. Put `BINOMO_EMAIL` and `BINOMO_PASSWORD` in a `.env` file first, as described in [Getting Started](getting-started#2-store-your-credentials-safely).
{: .fs-5 .fw-300 }

1. TOC
{:toc}

---

## List every asset (no login)

```python
from BinomoAPI import BinomoAPI

for asset in BinomoAPI.get_assets():
    tag = "OTC" if asset.is_otc else "   "
    print(f"{tag}  {asset.name.strip():<16} {asset.ric}")
```

## Check demo and real balances

```python
import asyncio, os
from dotenv import load_dotenv
from BinomoAPI import BinomoAPI

load_dotenv()

async def main():
    login = BinomoAPI.login(os.environ["BINOMO_EMAIL"], os.environ["BINOMO_PASSWORD"])
    async with BinomoAPI.create_from_login(login) as api:
        for account in ("demo", "real"):
            b = await api.get_balance(account)
            print(f"{account:>4}: {b.amount:,.2f} {b.currency}")

asyncio.run(main())
```

## Place one CALL and one PUT

```python
import asyncio, os
from dotenv import load_dotenv
from BinomoAPI import BinomoAPI, TradeError

load_dotenv()

async def main():
    login = BinomoAPI.login(os.environ["BINOMO_EMAIL"], os.environ["BINOMO_PASSWORD"])
    async with BinomoAPI.create_from_login(login, demo=True) as api:
        try:
            up = await api.place_call_option("Z-EUR/USD", 60, 100)
            down = await api.place_put_option("Z-GBP/USD", 60, 100)
            print(up, down, sep="\n")
        except TradeError as e:
            print("Trade failed:", e)

asyncio.run(main())
```

## Trade at the start of every minute

60-second trades expire on minute boundaries (see [how expiry works](trading#how-expiry-time-is-calculated)). Sending right after the minute ticks over gives you the longest, most consistent holding time.

```python
import asyncio, os, time
from dotenv import load_dotenv
from BinomoAPI import BinomoAPI

load_dotenv()

async def wait_for_next_minute(offset: float = 1.0) -> None:
    await asyncio.sleep(60 - (time.time() % 60) + offset)

async def main():
    login = BinomoAPI.login(os.environ["BINOMO_EMAIL"], os.environ["BINOMO_PASSWORD"])
    async with BinomoAPI.create_from_login(login, demo=True) as api:
        for _ in range(5):
            await wait_for_next_minute()
            print(await api.place_call_option("Z-EUR/USD", 60, 100))

asyncio.run(main())
```

## Signal bot with risk limits

A template for any strategy: plug your own logic into `get_signal()`. The bot enforces a fixed stake, a maximum number of trades and a minimum balance. These limits matter more than the strategy.

```python
import asyncio, os, random, time
from typing import Optional
from dotenv import load_dotenv
from BinomoAPI import BinomoAPI, BinomoAPIException

load_dotenv()

ASSET = "Z-EUR/USD"
STAKE = 100              # 1.00 in minor units
MAX_TRADES = 20
MIN_BALANCE = 50.00      # stop when the balance falls below this (major units)

def get_signal() -> Optional[str]:
    """Return 'call', 'put' or None. Replace with your strategy."""
    return random.choice(["call", "put", None])

async def main():
    login = BinomoAPI.login(os.environ["BINOMO_EMAIL"], os.environ["BINOMO_PASSWORD"])
    async with BinomoAPI.create_from_login(login, demo=True) as api:
        trades = 0
        while trades < MAX_TRADES:
            balance = await api.get_balance()
            if balance.amount < MIN_BALANCE:
                print("Balance below limit, stopping.")
                break

            signal = get_signal()
            if signal is None:
                await asyncio.sleep(5)
                continue

            try:
                place = api.place_call_option if signal == "call" else api.place_put_option
                result = await place(ASSET, 60, STAKE)
                trades += 1
                print(f"[{time.strftime('%H:%M:%S')}] #{trades} {signal.upper()} {result['status']}")
            except BinomoAPIException as e:
                print("Error, backing off:", e)
                await asyncio.sleep(10)

            await asyncio.sleep(60)  # one trade per minute

asyncio.run(main())
```

## Trade several assets

Orders go out one after another over a single connection, which takes milliseconds. Send them sequentially rather than with `asyncio.gather` so each order gets its own message reference.

```python
import asyncio, os
from dotenv import load_dotenv
from BinomoAPI import BinomoAPI

load_dotenv()

ORDERS = [
    ("Z-EUR/USD", "call"),
    ("Z-GBP/USD", "put"),
    ("Z-USD/JPY", "call"),
]

async def main():
    login = BinomoAPI.login(os.environ["BINOMO_EMAIL"], os.environ["BINOMO_PASSWORD"])
    async with BinomoAPI.create_from_login(login, demo=True) as api:
        await api.connect()  # open the WebSocket once, up front
        for ric, direction in ORDERS:
            place = api.place_call_option if direction == "call" else api.place_put_option
            print(ric, direction, await place(ric, 60, 100))

asyncio.run(main())
```

## Read the server's replies

Binomo answers trade orders asynchronously on the WebSocket. Until a public results API lands, you can inspect the raw replies:

```python
trade = await api.place_call_option("Z-CRY/IDX", 60, 100)
await asyncio.sleep(3)
for msg in api._ws_client._last_messages:
    print(msg)
```

## Load settings from the environment

```python
from BinomoAPI.config_manager import BinomoConfig

config = BinomoConfig()              # reads binomo_config.json and BINOMO_* env vars
email, password = config.get_credentials()
stake_limit = config.get("trading", "max_trade_amount")
check = config.validate_trade_params(amount=5.0)
print(check)   # {'valid': True, 'errors': [], 'warnings': []}
```

See [Configuration](configuration) for every option.

---

Built something cool? **Share it in [Discord](https://discord.gg/p7YyFqSmAz)** or open a pull request to add it to [`examples/`](https://github.com/ChipaDevTeam/BinomoAPI/tree/main/examples). If you'd rather have a bot built for you, [the team builds custom bots](https://chipatrade.com/services/bot-development).
