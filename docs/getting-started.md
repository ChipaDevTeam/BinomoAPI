---
title: Getting Started
description: Install the BinomoAPI Python package, log in to Binomo, check your demo balance and place your first automated trade, step by step.
nav_order: 2
---

# Getting started with BinomoAPI
{: .no_toc }

In about five minutes you'll install the library, log in to your Binomo account from Python, read your demo balance and place your first automated trade.
{: .fs-5 .fw-300 }

1. TOC
{:toc}

---

## Requirements

- **Python 3.8 or newer**
- A **Binomo account** that signs in with email and password. Accounts created through Google or Facebook need a password set first.
- Basic familiarity with `async`/`await`. If that's new to you, copy the examples as they are; they run unchanged.

## 1. Install

```bash
pip install BinomoAPI
```

Or install the latest code from GitHub:

```bash
pip install git+https://github.com/ChipaDevTeam/BinomoAPI.git
```

We recommend a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install BinomoAPI python-dotenv
```

## 2. Store your credentials safely

Never hard-code your password. Create a `.env` file next to your script, and add it to `.gitignore`:

```ini
BINOMO_EMAIL=you@example.com
BINOMO_PASSWORD=your-password
```

## 3. Log in

```python
import os
from dotenv import load_dotenv
from BinomoAPI import BinomoAPI

load_dotenv()

login = BinomoAPI.login(os.environ["BINOMO_EMAIL"], os.environ["BINOMO_PASSWORD"])
print("Logged in as user", login.user_id)
```

`BinomoAPI.login()` is a regular (synchronous) function. It returns a [`LoginResponse`](api-reference#loginresponse) that holds your auth token and the HTTP session Binomo just authenticated.

{: .note }
> The login call currently prints diagnostic output, including session cookies, to the console. Don't run it where other people can read your logs.

## 4. Create a client and check your balance

Use `BinomoAPI.create_from_login()` to build the client. It reuses the logged-in session, which is the most reliable way to stay authenticated:

```python
import asyncio

async def main():
    login = BinomoAPI.login(os.environ["BINOMO_EMAIL"], os.environ["BINOMO_PASSWORD"])

    async with BinomoAPI.create_from_login(login, demo=True) as api:
        balance = await api.get_balance()
        print(f"{balance.account_type} balance: {balance.amount:.2f} {balance.currency}")

asyncio.run(main())
```

The `async with` block opens the client and closes the WebSocket connection when you're done, even if an error occurs.

## 5. Place your first trade

Trades are placed by **RIC code**, Binomo's internal identifier for each asset. EUR/USD is `EURO`, EUR/USD (OTC) is `Z-EUR/USD`, Bitcoin is `XBT/USD`. The full table is on the [Asset List](assets).

```python
async with BinomoAPI.create_from_login(login, demo=True) as api:
    trade = await api.place_call_option(
        asset="Z-EUR/USD",    # EUR/USD (OTC), open 24/7
        duration_seconds=60,  # 1-minute expiry
        amount=100,           # see "Trade amounts" below
    )
    print(trade)
```

Output:

```python
{'status': 'submitted', 'asset': 'Z-EUR/USD', 'direction': 'call',
 'amount': 100, 'duration': 60, 'account_type': 'demo', 'ref': '5'}
```

Open Binomo in your browser and the trade appears in your demo account. 🎉

{: .tip }
> Use an **OTC asset** while you develop. OTC markets stay open at weekends and overnight, so your test trades don't fail because a market is closed.

## Trade amounts

`amount` is passed to Binomo unchanged. Binomo counts money in the **smallest unit of your account currency** (cents), the same unit its balance endpoint returns before BinomoAPI divides it by 100. So `amount=100` is a 1.00 stake. Check this on your demo account before you go live.

## Going live

Pass `demo=False` to trade on your real account:

```python
async with BinomoAPI.create_from_login(login, demo=False) as api:
    ...
```

Or keep a demo client and override a single trade with `use_demo=False`. We strongly suggest you read [Trading](trading) and [Best Practices](best-practices) first.

## Next steps

- [Trading](trading): directions, expiry times and how Binomo aligns them
- [Examples](examples): complete bots you can copy
- [Error Handling](error-handling): what can fail and how to recover
- Stuck? Ask in [Discord](https://discord.gg/p7YyFqSmAz). Someone has probably hit the same problem.
