---
title: Binomo API for Python
description: BinomoAPI is a free, open-source Python library for building Binomo trading bots. Log in, read your balance, list assets and place CALL/PUT trades in a few lines of code.
nav_order: 1
permalink: /
---

# Binomo API for Python
{: .fs-9 }

Build your own Binomo trading bot in Python. BinomoAPI handles login, sessions, the WebSocket connection and trade payloads, so you can work on your strategy.
{: .fs-6 .fw-300 }

[Get started in 5 minutes](getting-started){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[Join the Discord](https://discord.gg/p7YyFqSmAz){: .btn .fs-5 .mb-4 .mb-md-0 .mr-2 }
[Star on GitHub](https://github.com/ChipaDevTeam/BinomoAPI){: .btn .fs-5 .mb-4 .mb-md-0 }

[![PyPI version](https://img.shields.io/pypi/v/BinomoAPI.svg)](https://pypi.org/project/BinomoAPI/)
[![Python versions](https://img.shields.io/pypi/pyversions/BinomoAPI.svg)](https://pypi.org/project/BinomoAPI/)
[![Downloads](https://static.pepy.tech/badge/binomoapi)](https://pepy.tech/project/binomoapi)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ChipaDevTeam/BinomoAPI/blob/main/LICENSE)
[![Discord](https://img.shields.io/badge/chat-Discord-5865F2?logo=discord&logoColor=white)](https://discord.gg/p7YyFqSmAz)

---

## Install

```bash
pip install BinomoAPI
```

## Your first trade

```python
import asyncio
import os
from BinomoAPI import BinomoAPI

async def main():
    login = BinomoAPI.login(os.environ["BINOMO_EMAIL"], os.environ["BINOMO_PASSWORD"])

    async with BinomoAPI.create_from_login(login, demo=True) as api:
        balance = await api.get_balance()
        print(f"Demo balance: {balance.amount:.2f} {balance.currency}")

        # "EURO" is the RIC code for EUR/USD; see the asset list
        trade = await api.place_call_option(asset="EURO", duration_seconds=60, amount=100)
        print(trade)

asyncio.run(main())
```

That's the whole loop: **log in, open a client, check the balance, trade.** Everything runs on your **demo account** until you pass `demo=False`.

## What you can do with it

| | |
|:--|:--|
| **Authenticate** | Email/password login with the session kept alive for later requests. |
| **Read balances** | Demo and real account balances, cached for 5 minutes to avoid extra requests. |
| **Discover assets** | 52 bundled assets (forex, OTC, crypto, stocks, indices, metals), each with its RIC code. No login needed. |
| **Trade binary options** | CALL (up) and PUT (down) turbo options over Binomo's WebSocket API. |
| **Handle errors cleanly** | A small exception hierarchy: `AuthenticationError`, `TradeError` and more. |
| **Use modern Python** | `async`/`await`, type hints, dataclass models and async context managers. |

## Where to go next

- **New here?** Start with [Getting Started](getting-started): install, log in and place a demo trade.
- **Building a bot?** Read [Trading](trading) to learn how expiry times work, then grab code from [Examples](examples).
- **Need an asset code?** The [Asset List](assets) has every supported asset and its RIC.
- **Looking up a method?** See the [API Reference](api-reference).
- **Something broke?** Try the [FAQ](faq) and [Error Handling](error-handling), or ask on [Discord](https://discord.gg/p7YyFqSmAz).

## Join the community

BinomoAPI is built in the open by [ChipaDevTeam](https://github.com/ChipaDevTeam). Traders and developers share strategies, bots and fixes in our community:

- 💬 **[Discord](https://discord.gg/p7YyFqSmAz)**: get help, show off your bot, follow releases
- ✈️ **[Telegram](https://t.me/ChipaDevTeam)**: talk to the team directly
- ⭐ **[GitHub](https://github.com/ChipaDevTeam/BinomoAPI)**: star the repo, report issues, send pull requests

More ways to get involved are on the [Community](community) page, including a bot built for you by the team.

{: .warning }
> BinomoAPI is an **unofficial** library and is not affiliated with Binomo. Binary options are high-risk and you can lose your whole stake. Test on a demo account first, and only trade money you can afford to lose.
