---
title: API Reference
description: Complete reference for the BinomoAPI Python client, covering login, create_from_login, get_balance, place_call_option, place_put_option, asset helpers, data models, exceptions and constants.
nav_order: 6
---

# API reference
{: .no_toc }

Every public class, method and model in BinomoAPI 2.x.
{: .fs-5 .fw-300 }

1. TOC
{:toc}

---

## Imports

Everything public is importable from the package root:

```python
from BinomoAPI import (
    BinomoAPI,
    LoginResponse, Asset, Balance, TradeOrder,
    BinomoAPIException, AuthenticationError, ConnectionError,
    InvalidParameterError, TradeError, InsufficientBalanceError,
    TRADE_DIRECTIONS, ACCOUNT_TYPES, OPTION_TYPES,
)
```

---

## Authentication

### `BinomoAPI.login()`

```python
BinomoAPI.login(email: str, password: str, device_id: str = DEFAULT_DEVICE_ID) -> LoginResponse
```

Sign in with email and password. **Synchronous.** It tries Binomo's v2 sign-in endpoint and falls back to v1 if v2 rejects the request with HTTP 422.

| Parameter | Description |
|:--|:--|
| `email`, `password` | Binomo account credentials. |
| `device_id` | Identifier Binomo associates with the session. Use the **same** value when you create the client. |

**Raises:** `InvalidParameterError` (empty credentials), `AuthenticationError` (wrong credentials, or the request was rejected), `ConnectionError` (network failure, timeout or 5xx response), `BinomoAPIException` (anything else).

### `BinomoAPI.create_from_login()`

```python
BinomoAPI.create_from_login(
    login_response: LoginResponse,
    device_id: str = DEFAULT_DEVICE_ID,
    demo: bool = True,
    enable_logging: bool = False,
    log_level: int = logging.INFO,
) -> BinomoAPI
```

**Recommended** way to build a client. It reuses the authenticated HTTP session from `login()` and pre-caches the balance fetched during login.

```python
login = BinomoAPI.login(email, password)
async with BinomoAPI.create_from_login(login, demo=True) as api:
    ...
```

---

## The client

### `BinomoAPI(...)`

```python
BinomoAPI(
    auth_token: str,
    device_id: str,
    demo: bool = True,
    enable_logging: bool = False,
    log_level: int = logging.INFO,
    login_session: Optional[requests.Session] = None,
)
```

Direct constructor. Use it when you already hold a token, for example one saved from an earlier login. Without `login_session` a fresh HTTP session is created.

| Parameter | Description |
|:--|:--|
| `auth_token` | `LoginResponse.authtoken`. |
| `device_id` | The device ID used at login. |
| `demo` | `True` for the demo account, `False` for real money. |
| `enable_logging`, `log_level` | Turn on the `BinomoAPI` logger. |
| `login_session` | A `requests.Session` from `login()`, so the authenticated session is reused. |

**Raises:** `InvalidParameterError` if `auth_token` or `device_id` is empty.

### Context managers

```python
async with BinomoAPI.create_from_login(login) as api:   # preferred: awaits close()
    ...

with BinomoAPI.create_from_login(login) as api:         # sync: calls close_sync()
    ...
```

### `connect()`

```python
async def connect() -> bool
```

Open the WebSocket and join the trading channels. Optional, because trading methods connect on first use. Call it up front to pay the connection cost before your first trade.

### `close()` / `close_sync()`

```python
async def close() -> None
def close_sync() -> None
```

Close the WebSocket. Called for you by the context managers.

---

## Account

### `get_balance()`

```python
async def get_balance(account_type: Optional[str] = None) -> Balance
```

Return the balance of `"demo"` or `"real"`. Defaults to the client's account. Results are cached for **5 minutes**.

**Raises:** `AuthenticationError` (session invalid or token rejected), `ConnectionError`, `BinomoAPIException` (unexpected response or unknown account type).

---

## Trading

### `place_call_option()` / `place_put_option()`

```python
async def place_call_option(asset: str, duration_seconds: int, amount: float,
                            use_demo: Optional[bool] = None) -> Dict[str, Any]
async def place_put_option(asset: str, duration_seconds: int, amount: float,
                           use_demo: Optional[bool] = None) -> Dict[str, Any]
```

Send a turbo binary option predicting the price goes up (CALL) or down (PUT).

| Parameter | Description |
|:--|:--|
| `asset` | **RIC code**, e.g. `"EURO"`. See [Asset List](assets). |
| `duration_seconds` | Expiry step; the expiry is aligned to clock boundaries ([details](trading#how-expiry-time-is-calculated)). |
| `amount` | Stake in minor currency units (`100` = 1.00). |
| `use_demo` | Override the client's account for this trade. |

**Returns** a submission receipt:

```python
{"status": "submitted", "asset": "EURO", "direction": "call", "amount": 100,
 "duration": 60, "account_type": "demo", "ref": "5"}
```

**Raises:** `InvalidParameterError` (non-positive duration or amount, unknown asset), `TradeError` (sending failed).

---

## Assets

These are **static methods**, so no login is needed. Results come from the bundled `assets.json` and are cached after the first call.

| Method | Returns |
|:--|:--|
| `BinomoAPI.get_assets()` | `List[Asset]`, every supported asset |
| `BinomoAPI.get_asset_names()` | `List[str]`, every asset name |
| `BinomoAPI.get_otc_assets()` | `List[Asset]`, OTC assets only (24/7) |
| `BinomoAPI.get_standard_assets()` | `List[Asset]`, non-OTC assets only |

Instance helpers:

| Method | Returns |
|:--|:--|
| `api.get_available_assets()` | `List[Asset]`, a copy of the client's asset list |
| `api.get_asset_ric(name)` | `Optional[str]`, the RIC for an exact (case-insensitive) name match |

---

## Data models

### `LoginResponse`

```python
@dataclass
class LoginResponse:
    authtoken: str
    user_id: str
    balance: Optional[float]   # set after login: balance in minor units, if it could be read
```

### `Balance`

```python
@dataclass
class Balance:
    amount: float        # major units, e.g. 1000.00
    currency: str
    account_type: str    # "demo" or "real"
```

### `Asset`

```python
@dataclass
class Asset:
    name: str
    ric: str
    is_active: bool = True
    id: Optional[int] = None
    asset_type: Optional[int] = None

    @property
    def is_otc(self) -> bool: ...   # True if the name ends with "(OTC)"
```

### `TradeOrder`

The internal order model. `to_payload()` builds the WebSocket message. You only need it if you're sending orders yourself.

```python
@dataclass
class TradeOrder:
    asset_ric: str
    direction: str             # "call" or "put"
    amount: float
    duration_seconds: int
    option_type: str = "turbo"
    account_type: str = "demo"
    tournament_id: Optional[str] = None
```

---

## Exceptions

```
BinomoAPIException
├── AuthenticationError
├── ConnectionError
├── InvalidParameterError
└── TradeError
    └── InsufficientBalanceError
```

See [Error Handling](error-handling) for when each one is raised and how to recover.

---

## Constants

```python
TRADE_DIRECTIONS = {"CALL": "call", "PUT": "put"}
ACCOUNT_TYPES    = {"DEMO": "demo", "REAL": "real"}
OPTION_TYPES     = {"TURBO": "turbo", "CLASSIC": "classic"}
```

---

## Legacy methods

These are kept for v1 code and are **deprecated**. See [Migration](migration).

| Legacy | Use instead |
|:--|:--|
| `await api.Call(ric, duration, amount, is_demo)` | `place_call_option()` |
| `await api.Put(ric, duration, amount, is_demo)` | `place_put_option()` |
| `await api.Getbalance()` | `get_balance()`. Note that `Getbalance()` returns raw minor units, or `None`. |
