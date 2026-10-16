<div align="center">

# BinomoAPI: Binomo API for Python

**Build your own Binomo trading bot in Python.** Log in, read your demo or real balance, list every asset and RIC code, and place CALL/PUT binary options in a few lines of async code.

[![PyPI version](https://img.shields.io/pypi/v/BinomoAPI.svg)](https://pypi.org/project/BinomoAPI/)
[![Python versions](https://img.shields.io/pypi/pyversions/BinomoAPI.svg)](https://pypi.org/project/BinomoAPI/)
[![Downloads](https://static.pepy.tech/badge/binomoapi)](https://pepy.tech/project/binomoapi)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ChipaDevTeam/BinomoAPI/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen.svg)](https://chipadevteam.github.io/BinomoAPI/)
[![Discord](https://img.shields.io/badge/chat-Discord-5865F2?logo=discord&logoColor=white)](https://discord.gg/p7YyFqSmAz)

[**Documentation**](https://chipadevteam.github.io/BinomoAPI/) · [**Getting Started**](https://chipadevteam.github.io/BinomoAPI/getting-started) · [**Examples**](https://chipadevteam.github.io/BinomoAPI/examples) · [**Asset List**](https://chipadevteam.github.io/BinomoAPI/assets) · [**Discord**](https://discord.gg/p7YyFqSmAz)

</div>

---

> **📈 Trading crypto too?** [ChipaX](https://exchange.chipatrade.com/trade/BTC?ref=Z1RN8GBS) is our own perpetuals exchange, and it has a Python API.
> `pip install chipax` gives you perps on real [Hyperliquid](https://hyperliquid.xyz) liquidity, plus a free **$100,000 paper account** that charges the same fees and enforces the same leverage caps as live trading. No deposit or KYC to practise. → [chipax-python](https://github.com/ChipaDevTeam/chipax-python)

## Why BinomoAPI?

Binomo has no public trading API. BinomoAPI is a free, open-source Python library that talks to the same endpoints the Binomo web app uses, so you can automate your strategy without browser automation.

- ⚡ **Async and fast:** built on `asyncio` and WebSockets
- 🔐 **Login and sessions handled:** email/password sign-in, with the authenticated session reused for later requests
- 💰 **Demo and real accounts:** switch with one flag, or per trade
- 📊 **52 bundled assets:** forex, 24/7 OTC pairs, crypto, indices, stocks, gold and silver, with their RIC codes
- 🧱 **Typed and tidy:** dataclass models, type hints and a clear exception hierarchy
- 🆓 **MIT licensed:** use it in personal or commercial projects

## Installation

```bash
pip install BinomoAPI
```

Requires Python 3.8+.

## Quick start

```python
import asyncio
import os
from BinomoAPI import BinomoAPI

async def main():
    login = BinomoAPI.login(os.environ["BINOMO_EMAIL"], os.environ["BINOMO_PASSWORD"])

    async with BinomoAPI.create_from_login(login, demo=True) as api:
        balance = await api.get_balance()
        print(f"Demo balance: {balance.amount:.2f} {balance.currency}")

        trade = await api.place_call_option(
            asset="Z-EUR/USD",    # RIC code for EUR/USD (OTC), open 24/7
            duration_seconds=60,
            amount=100,           # stake in minor units: 100 = 1.00
        )
        print(trade)  # {'status': 'submitted', 'asset': 'Z-EUR/USD', 'direction': 'call', ...}

asyncio.run(main())
```

👉 **New to BinomoAPI?** The [Getting Started guide](https://chipadevteam.github.io/BinomoAPI/getting-started) walks you from install to first trade in five minutes.

## Usage

### List assets and RIC codes (no login needed)

```python
from BinomoAPI import BinomoAPI

for asset in BinomoAPI.get_assets():
    print(asset.name.strip(), asset.ric, "OTC" if asset.is_otc else "")

BinomoAPI.get_otc_assets()        # 24/7 OTC assets only
BinomoAPI.get_standard_assets()   # market-hours assets only
```

Trades take the **RIC code** (`"EURO"` for EUR/USD, `"XBT/USD"` for Bitcoin), not the display name. See the [full asset list](https://chipadevteam.github.io/BinomoAPI/assets).

### Check balances

```python
demo = await api.get_balance("demo")
real = await api.get_balance("real")
print(demo.amount, real.amount)
```

### CALL (up) and PUT (down)

```python
await api.place_call_option("EURO", duration_seconds=60, amount=100)
await api.place_put_option("EURO", duration_seconds=300, amount=100, use_demo=False)  # real account
```

Expiry times snap to clock boundaries, just as they do in the Binomo app. [Learn how expiry is calculated](https://chipadevteam.github.io/BinomoAPI/trading#how-expiry-time-is-calculated).

### Handle errors

```python
from BinomoAPI import AuthenticationError, InvalidParameterError, TradeError, BinomoAPIException

try:
    await api.place_call_option("EURO", 60, 100)
except InvalidParameterError as e:
    print("Fix your input:", e)
except TradeError as e:
    print("Order failed:", e)
except BinomoAPIException as e:
    print("API error:", e)
```

More in the docs: [Trading](https://chipadevteam.github.io/BinomoAPI/trading) · [Examples](https://chipadevteam.github.io/BinomoAPI/examples) · [API Reference](https://chipadevteam.github.io/BinomoAPI/api-reference) · [Error Handling](https://chipadevteam.github.io/BinomoAPI/error-handling) · [Configuration](https://chipadevteam.github.io/BinomoAPI/configuration) · [FAQ](https://chipadevteam.github.io/BinomoAPI/faq)

## Example bots

| Example | What it shows |
|:--|:--|
| [Trade every minute](https://chipadevteam.github.io/BinomoAPI/examples#trade-at-the-start-of-every-minute) | Align orders to Binomo's expiry boundaries |
| [Signal bot with risk limits](https://chipadevteam.github.io/BinomoAPI/examples#signal-bot-with-risk-limits) | Plug in your strategy, with stake, trade-count and balance stops |
| [Multiple assets](https://chipadevteam.github.io/BinomoAPI/examples#trade-several-assets) | One client, several pairs |
| [`examples/place_order.py`](https://github.com/ChipaDevTeam/BinomoAPI/blob/main/examples/place_order.py) | Runnable script that also prints the server's replies |

## Community

Join traders and developers building Binomo bots with BinomoAPI:

- 💬 **[Discord](https://discord.gg/p7YyFqSmAz)**: help, strategies, release news
- ✈️ **[Telegram](https://t.me/ChipaDevTeam)**: talk to the team
- 🐛 **[Issues](https://github.com/ChipaDevTeam/BinomoAPI/issues)**: bugs and feature requests
- ⭐ **Star this repo** so other traders can find it

### Need a custom bot?

ChipaDevTeam builds trading bots around your strategy. **[Get our services](https://chipatrade.com/services/bot-development)**.

### More from ChipaDevTeam

- 🚀 **[ChipaEditor](https://chipaeditor.com/?utm_source=github&utm_medium=readme&utm_campaign=binomo_api&utm_term=products&utm_content=community)**: AI-powered strategy editor
- 📈 **[ChipaX](https://exchange.chipatrade.com/trade/BTC?ref=Z1RN8GBS)**: perpetuals exchange with a [Python SDK](https://github.com/ChipaDevTeam/chipax-python) and a free $100k paper account

### Support the project

BinomoAPI is free. If it saves you time, you can help keep it maintained: [Patreon](https://patreon.com/VigoDEV) · [PayPal](https://paypal.me/ChipaCL)

## Contributing

Pull requests are welcome, whether new assets, examples, fixes or docs. See the [contributing guide](https://chipadevteam.github.io/BinomoAPI/contributing).

## Credits

Inspired by [hert0t/Binomo-API](https://github.com/hert0t/Binomo-API).

## License

[MIT](https://github.com/ChipaDevTeam/BinomoAPI/blob/main/LICENSE) © ChipaDevTeam

## Disclaimer

BinomoAPI is an **unofficial** project and is not affiliated with, endorsed by or connected to Binomo. Binary options trading carries a high risk of losing your entire stake. This software is provided for educational and research purposes, without warranty. Test on a demo account, check that automated trading is allowed under Binomo's terms and your local laws, and never trade money you can't afford to lose.
