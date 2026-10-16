---
title: Best Practices
description: Run a safe, reliable Binomo trading bot. Covers risk limits, demo testing, credential security, session handling and logging for BinomoAPI.
nav_order: 9
---

# Best practices for Binomo trading bots
{: .no_toc }

A good strategy can be wiped out by a bot that crashes, leaks a password or trades without limits. These practices keep your bot safe.
{: .fs-5 .fw-300 }

1. TOC
{:toc}

---

## Risk management

- **Start on demo, stay there until the numbers say otherwise.** Run every new strategy for hundreds of demo trades before you risk real money.
- **Use a fixed, small stake.** A common rule is no more than 1–2% of your balance per trade.
- **Set hard stops in code:** a maximum number of trades per session, a daily loss limit and a minimum balance. See the [signal bot example](examples#signal-bot-with-risk-limits).
- **Avoid martingale** (doubling after a loss). A short losing streak can wipe out the account.
- **Check your balance yourself before each trade.** Compare `balance.amount * 100` with your stake, which is in minor units.

{: .warning }
> Binary options are high-risk. Most retail traders lose money. Nothing in this library or its docs is financial advice.

## Credentials and security

- Load credentials from environment variables or a `.env` file, and **never commit them**. Add `.env` to `.gitignore`.
- Treat the auth token like a password. Debug logs and the login console output contain it.
- Redact tokens and cookies before you share logs in issues or on Discord.
- Use a separate device ID per bot so sessions don't clash.

## Session and connection handling

- Create the client with **`create_from_login()`** so the authenticated session is reused.
- Use **`async with`** so the WebSocket is always closed, even after an exception.
- Call **`await api.connect()`** once at startup so your first trade isn't delayed.
- For bots that run for hours, catch `AuthenticationError` and **log in again** ([example](error-handling#re-login-when-the-session-expires)).
- Retry network errors with **exponential backoff**, never in a tight loop ([example](error-handling#retry-with-exponential-backoff)).

## Trading mechanics

- **Pass RIC codes** (`"EURO"`), not display names (`"EUR/USD"`). See the [Asset List](assets).
- **Prefer OTC assets for testing.** They're open 24/7.
- **Mind expiry alignment.** A 60-second trade expires on the next whole minute that is at least 30 seconds away. [Details](trading#how-expiry-time-is-calculated).
- **Send orders sequentially** over one client rather than in parallel.
- `"submitted"` means sent, not accepted or won. Check the result on Binomo.

## Logging and monitoring

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
```

Log every trade receipt (`ref`, asset, direction, amount, time) so you can match it against your Binomo history later.

## Respect the platform

Automated trading may be restricted by Binomo's terms of service, and that is your responsibility. Keep request rates reasonable: the 5-minute balance cache exists for a reason.
