---
title: Trading
description: Place CALL and PUT binary options on Binomo from Python. Learn how expiry times are aligned, how to pick demo or real accounts, and what the trade response means.
nav_order: 3
---

# Trading binary options with Python
{: .no_toc }

How CALL/PUT trades work in BinomoAPI, how Binomo sets expiry times, and how to read what comes back.
{: .fs-5 .fw-300 }

1. TOC
{:toc}

---

## CALL and PUT

| Method | You predict | Binomo name |
|:--|:--|:--|
| `place_call_option()` | the price will be **higher** at expiry | "Up" |
| `place_put_option()` | the price will be **lower** at expiry | "Down" |

Both take the same arguments:

```python
await api.place_call_option(
    asset="EURO",          # RIC code, see the Asset List
    duration_seconds=60,   # expiry step in seconds
    amount=100,            # stake, in minor currency units (cents)
    use_demo=None,         # None = client default, True = demo, False = real
)
```

Trades are sent as Binomo **turbo** options over the WebSocket connection. The client connects and joins the required channels on the first trade, so you don't need to call `connect()` first.

## Choosing the asset

Always pass the asset's **RIC code** (`"EURO"`, `"Z-EUR/USD"`, `"XBT/USD"`), not its display name. All RICs are listed on the [Asset List](assets), which also shows how to look one up by name.

{: .warning }
> A display name such as `"EUR/USD"` is sent to Binomo unchanged and the trade is rejected. Convert names to RICs first.

## How expiry time is calculated

Binomo expiries snap to fixed clock boundaries rather than "now + duration". BinomoAPI follows the same rule:

1. Round **up** to the next multiple of `duration_seconds` on the Unix clock.
2. If that is less than **30 seconds** away, add another `duration_seconds` until it isn't.

So a 60-second trade always expires at the top of a minute, and the actual time to expiry varies:

| You send at | `duration_seconds` | Expires at | Time in trade |
|:--|:--|:--|:--|
| 12:00:10 | 60 | 12:01:00 | 50 s |
| 12:00:45 | 60 | 12:02:00 | 75 s |
| 12:00:10 | 300 | 12:05:00 | 4 min 50 s |
| 12:03:40 | 300 | 12:05:00 | 1 min 20 s |

{: .tip }
> If your strategy needs a precise holding time, send the order just after a boundary, for example in the first few seconds of each minute for 60-second trades.

## Demo vs. real account

The account is chosen when you create the client:

```python
api = BinomoAPI.create_from_login(login, demo=True)   # demo (default)
api = BinomoAPI.create_from_login(login, demo=False)  # real money
```

Any single trade can override it:

```python
await api.place_put_option("EURO", 60, 100, use_demo=False)  # this trade only: real
```

## What a trade returns

`place_call_option()` and `place_put_option()` return as soon as the order has been **sent**:

```python
{
    "status": "submitted",
    "asset": "EURO",
    "direction": "call",
    "amount": 100,
    "duration": 60,
    "account_type": "demo",
    "ref": "5",
}
```

`"submitted"` means the order left your machine. It does **not** mean Binomo accepted the trade or that it won. Binomo replies asynchronously on the WebSocket, and the replies are kept on the client for debugging:

```python
await asyncio.sleep(3)  # give the server time to answer
for message in api._ws_client._last_messages:
    print(message)
```

{: .note }
> `_ws_client` is an internal attribute and may change between releases. A public API for trade results and outcomes is on the roadmap. Follow progress or help out on [GitHub](https://github.com/ChipaDevTeam/BinomoAPI/issues).

## Checking your balance before trading

```python
balance = await api.get_balance()            # client's account type
real = await api.get_balance("real")         # a specific account
print(balance.amount, balance.currency)      # in major units, e.g. 1000.00
```

Balances are cached for **5 minutes**, so read them freely in a loop without flooding Binomo. Compare against your stake yourself before trading. `balance.amount` is in major units and the trade `amount` is in minor units:

```python
if balance.amount * 100 < stake:
    print("Not enough balance, skipping trade")
```

## Input validation

Before anything is sent, BinomoAPI raises [`InvalidParameterError`](error-handling) if:

- `duration_seconds` is zero or negative
- `amount` is zero or negative
- `asset` is empty or unknown

Network or WebSocket failures while sending raise [`TradeError`](error-handling).

## Next

- [Examples](examples): scheduled, signal-driven and multi-asset bots
- [Best Practices](best-practices): keep your bot (and your balance) safe
