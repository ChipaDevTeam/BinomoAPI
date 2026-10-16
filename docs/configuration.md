---
title: Configuration
description: Configure BinomoAPI with environment variables, a JSON config file, logging and device IDs. Covers every BINOMO_* setting for your trading bot.
nav_order: 8
---

# Configuration
{: .no_toc }

BinomoAPI works with no configuration at all. These options help when you run a bot long-term or across several machines.
{: .fs-5 .fw-300 }

1. TOC
{:toc}

---

## Client options

Passed to `BinomoAPI.create_from_login()` or the `BinomoAPI(...)` constructor:

| Option | Default | Description |
|:--|:--|:--|
| `demo` | `True` | Trade on the demo account. Set `False` for real money. |
| `enable_logging` | `False` | Turn on the library's logger. |
| `log_level` | `logging.INFO` | Use `logging.DEBUG` to see every request and WebSocket message. |
| `device_id` | built-in default | Device identifier sent to Binomo. Must match the one used at login. |

## Credentials from environment variables

Keep secrets out of your code:

```bash
export BINOMO_EMAIL="you@example.com"
export BINOMO_PASSWORD="your-password"
```

```python
import os
from BinomoAPI import BinomoAPI

login = BinomoAPI.login(os.environ["BINOMO_EMAIL"], os.environ["BINOMO_PASSWORD"])
```

The repo includes a [`.env.example`](https://github.com/ChipaDevTeam/BinomoAPI/blob/main/.env.example). Copy it to `.env` and load it with `python-dotenv`.

## Device ID

Binomo ties a session to a device ID. The library ships with a default one, which is fine for getting started. For a bot that runs long-term, use your own and keep it stable:

```python
DEVICE_ID = "my-trading-bot-01"

login = BinomoAPI.login(email, password, device_id=DEVICE_ID)
api = BinomoAPI.create_from_login(login, device_id=DEVICE_ID)
```

{: .warning }
> Logging in with one device ID and creating the client with another causes `Session validation failed` errors.

## `BinomoConfig`: file and environment settings

`BinomoAPI.config_manager.BinomoConfig` gives you a single place to keep bot settings. It loads defaults, then `binomo_config.json` if present, then `BINOMO_*` environment variables, with later sources taking precedence.

```python
from BinomoAPI.config_manager import BinomoConfig

config = BinomoConfig()                       # or BinomoConfig("my_config.json")
config.get("trading", "default_asset")        # "EUR/USD"
config.set("trading", "max_trade_amount", 50)
config.save()                                 # writes binomo_config.json

email, password = config.get_credentials()    # BINOMO_EMAIL / BINOMO_PASSWORD
device_id = config.get_device_id()            # generated and stored if missing
config.validate_trade_params(amount=5.0)      # {'valid': True, 'errors': [], 'warnings': []}
config.create_sample_config()                 # writes binomo_config_sample.json
```

{: .note }
> `config_manager` requires Python 3.9 or newer.

### Environment variables

| Variable | Setting | Type |
|:--|:--|:--|
| `BINOMO_EMAIL` | login email (`get_credentials()`) | str |
| `BINOMO_PASSWORD` | login password (`get_credentials()`) | str |
| `BINOMO_DEMO_MODE` | `api.demo_mode` | bool (`true`/`1`/`yes`/`on`) |
| `BINOMO_LOG_LEVEL` | `api.log_level` | str |
| `BINOMO_DEVICE_ID` | `security.device_id` | str |
| `BINOMO_DEFAULT_ASSET` | `trading.default_asset` | str |
| `BINOMO_MIN_TRADE_AMOUNT` | `trading.min_trade_amount` | float |
| `BINOMO_MAX_TRADE_AMOUNT` | `trading.max_trade_amount` | float |
| `BINOMO_RISK_PERCENTAGE` | `trading.risk_percentage` | float |

### Config file

```json
{
  "api": {
    "demo_mode": true,
    "enable_logging": true,
    "log_level": "INFO",
    "connection_timeout": 30
  },
  "trading": {
    "default_asset": "EUR/USD",
    "min_trade_amount": 1.0,
    "max_trade_amount": 100.0,
    "default_duration": 60,
    "risk_percentage": 2.0,
    "max_concurrent_trades": 3
  },
  "security": {
    "device_id": "your-unique-device-id",
    "session_timeout": 3600,
    "auto_logout": true
  }
}
```

`BinomoConfig` stores these values for **your** code to read. The client doesn't apply them automatically, so pass them in yourself:

```python
api = BinomoAPI.create_from_login(
    login,
    device_id=config.get_device_id(),
    demo=config.get("api", "demo_mode"),
    enable_logging=config.get("api", "enable_logging"),
)
```
