---
title: Error Handling
description: How to handle BinomoAPI errors in your Binomo trading bot, including login failures, network errors, invalid parameters and failed trades, with retry patterns.
nav_order: 7
---

# Error handling
{: .no_toc }

Every error BinomoAPI raises derives from `BinomoAPIException`, so a single `except` catches them all, and the subclasses let you react precisely.
{: .fs-5 .fw-300 }

1. TOC
{:toc}

---

## Exception hierarchy

| Exception | Raised when | What to do |
|:--|:--|:--|
| `BinomoAPIException` | Base class; also unexpected HTTP or JSON responses | Log it; retry later |
| `AuthenticationError` | Wrong email/password, login rejected (HTTP 401/422), token expired | Check credentials; log in again |
| `ConnectionError` | Network down, timeout, Binomo 5xx, WebSocket failed | Back off and retry |
| `InvalidParameterError` | Empty credentials, non-positive amount or duration, unknown asset | Fix your input; don't retry |
| `TradeError` | The order couldn't be sent | Reconnect, then retry once |
| `InsufficientBalanceError` | Subclass of `TradeError`, reserved for balance failures | Stop trading |

{: .warning }
> BinomoAPI's `ConnectionError` is **not** Python's built-in `ConnectionError`. Import it explicitly with `from BinomoAPI import ConnectionError`, or catch `BinomoAPIException`.

## A robust template

```python
import asyncio
from BinomoAPI import (
    BinomoAPI, BinomoAPIException, AuthenticationError,
    ConnectionError, InvalidParameterError, TradeError,
)

async def run(email, password):
    try:
        login = BinomoAPI.login(email, password)
    except AuthenticationError as e:
        raise SystemExit(f"Login failed, check your credentials: {e}")

    async with BinomoAPI.create_from_login(login, demo=True) as api:
        try:
            await api.place_call_option("EURO", 60, 100)
        except InvalidParameterError as e:
            print("Bad input:", e)                 # bug in your code; don't retry
        except TradeError as e:
            print("Order not sent:", e)            # retry after reconnecting
        except ConnectionError as e:
            print("Network problem:", e)
        except BinomoAPIException as e:
            print("Unexpected API error:", e)
```

## Retry with exponential backoff

Transient errors such as timeouts, 5xx responses or a dropped WebSocket usually clear up on their own. Retry those, but never retry `InvalidParameterError` or `AuthenticationError` in a loop:

```python
import asyncio
from BinomoAPI import ConnectionError, TradeError

async def with_retry(make_call, attempts=3, base_delay=1.0):
    for attempt in range(1, attempts + 1):
        try:
            return await make_call()
        except (ConnectionError, TradeError):
            if attempt == attempts:
                raise
            await asyncio.sleep(base_delay * 2 ** (attempt - 1))

result = await with_retry(lambda: api.place_put_option("EURO", 60, 100))
```

## Re-login when the session expires

Long-running bots eventually lose their session. Catch `AuthenticationError`, log in again and rebuild the client:

```python
async def get_balance_with_relogin(api, email, password):
    try:
        return api, await api.get_balance()
    except AuthenticationError:
        await api.close()
        login = BinomoAPI.login(email, password)
        api = BinomoAPI.create_from_login(login, demo=True)
        return api, await api.get_balance()
```

## Debug logging

Turn on logging to see every request, response and WebSocket message:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

api = BinomoAPI.create_from_login(login, enable_logging=True, log_level=logging.DEBUG)
```

{: .note }
> Debug logs include your auth token and request headers. Don't paste them publicly. Redact the token before you share logs in an issue or on Discord.

## Common errors

| Message | Cause | Fix |
|:--|:--|:--|
| `Invalid email or password` | Wrong credentials, or the account uses Google/Facebook sign-in | Set a password on Binomo and use it |
| `Login rejected by Binomo (422 ...)` | Binomo rejected the request, often after many attempts or a new captcha | Log in once in the browser, wait a few minutes, retry |
| `Unknown asset: ...` | You passed a name instead of a RIC | Use the RIC from the [Asset List](assets) |
| `Session validation failed` | Token expired or a different `device_id` was used | Log in again; keep the `device_id` consistent |
| `WebSocket connection failed` | Network issue or Binomo maintenance | Retry with backoff |

Still stuck? Search the [FAQ](faq), [open an issue](https://github.com/ChipaDevTeam/BinomoAPI/issues), or ask in [Discord](https://discord.gg/p7YyFqSmAz).
