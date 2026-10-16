---
title: Migration Guide
description: Upgrade older BinomoAPI code (Call, Put, Getbalance) to the BinomoAPI 2.x methods place_call_option, place_put_option and get_balance.
nav_order: 10
---

# Migrating to BinomoAPI 2.x
{: .no_toc }

Version 2 renamed the trading and balance methods, added typed return values and replaced generic errors with specific exceptions. Old method names still work, so you can migrate one call at a time.
{: .fs-5 .fw-300 }

1. TOC
{:toc}

---

## Upgrade

```bash
pip install --upgrade BinomoAPI
```

## Method renames

| Before | After |
|:--|:--|
| `await api.Call(ric, duration, amount, is_demo)` | `await api.place_call_option(ric, duration, amount, use_demo=is_demo)` |
| `await api.Put(ric, duration, amount, is_demo)` | `await api.place_put_option(ric, duration, amount, use_demo=is_demo)` |
| `await api.Getbalance()` | `await api.get_balance()` |

### Return values changed

- `get_balance()` returns a [`Balance`](api-reference#balance) object with `amount` in **major units** (e.g. `1000.00`). `Getbalance()` returned a bare number in **minor units** (`100000`), or `None`.
- `place_call_option()` and `place_put_option()` return a [receipt dict](trading#what-a-trade-returns). `Call()` and `Put()` returned `None`.

```python
# Before
cents = await api.Getbalance()
print(cents / 100)

# After
balance = await api.get_balance()
print(balance.amount, balance.currency)
```

## Creating the client

Build the client from the login response so the authenticated session is reused:

```python
# Before
login = BinomoAPI.login(email, password)
api = BinomoAPI(auth_token=login.authtoken, device_id=DEVICE_ID, demo=True)

# After
login = BinomoAPI.login(email, password)
async with BinomoAPI.create_from_login(login, demo=True) as api:
    ...
```

## Exceptions

Catch specific errors instead of `Exception`:

```python
# Before
try:
    await api.Call("EURO", 60, 100, True)
except Exception as e:
    print(e)

# After
from BinomoAPI import TradeError, InvalidParameterError
try:
    await api.place_call_option("EURO", 60, 100, use_demo=True)
except InvalidParameterError as e:
    print("Fix your input:", e)
except TradeError as e:
    print("Order failed:", e)
```

See [Error Handling](error-handling) for the full hierarchy.

## Assets without logging in

New in 2.x: list assets and RIC codes without creating a client.

```python
BinomoAPI.get_assets()
BinomoAPI.get_otc_assets()
```

## Deprecation timeline

`Call`, `Put` and `Getbalance` remain available in 2.x and may be removed in a future major release. Migrate when you can.
