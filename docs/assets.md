---
title: Asset List & RIC Codes
description: Every Binomo asset supported by BinomoAPI, with its RIC code and asset ID. Covers forex, OTC pairs, crypto, indices, stocks, gold and silver.
nav_order: 4
---

# Binomo asset list and RIC codes
{: .no_toc }

Binomo identifies each tradable asset by a **RIC code** (Reuters Instrument Code), such as `EURO` for EUR/USD or `XBT/USD` for Bitcoin. Pass the RIC as the `asset` argument of `place_call_option()` and `place_put_option()`.
{: .fs-5 .fw-300 }

BinomoAPI ships with **52 assets**. They are listed below and are also available from code, without logging in.

1. TOC
{:toc}

---

## Get the asset list in Python

```python
from BinomoAPI import BinomoAPI

for asset in BinomoAPI.get_assets():
    print(f"{asset.name.strip():<16} {asset.ric:<18} OTC={asset.is_otc}")

BinomoAPI.get_otc_assets()       # only the OTC (24/7) assets
BinomoAPI.get_standard_assets()  # everything else
BinomoAPI.get_asset_names()      # just the names
```

### Look up a RIC by name

```python
def ric_for(name: str) -> str:
    for asset in BinomoAPI.get_assets():
        if asset.name.strip().lower() == name.lower():
            return asset.ric
    raise KeyError(name)

ric_for("EUR/USD")        # 'EURO'
ric_for("EUR/USD (OTC)")  # 'Z-EUR/USD'
```

{: .note }
> Some names in the bundled list have a trailing space (for example `"EUR/USD "`), so call `.strip()` before you compare names, as the helper above does.

## OTC vs. standard assets

**OTC** ("over the counter") assets are Binomo's synthetic quotes for popular pairs. They stay open **24/7, including weekends**, which makes them the best choice for testing a bot. **Standard** assets follow real market hours, so a trade on a closed market is rejected.

## Forex (OTC, 24/7)

| Asset | RIC (use this in trades) | Asset ID |
|:--|:--|--:|
| AUD/CAD (OTC) | `Z-AUD/CAD` | 244 |
| EUR/CAD (OTC) | `Z-EUR/CAD` | 302 |
| EUR/USD (OTC) | `Z-EUR/USD` | 235 |
| GBP/JPY (OTC) | `Z-GBP/JPY` | 237 |
| GBP/USD (OTC) | `Z-GBP/USD` | 241 |
| USD/JPY (OTC) | `Z-USD/JPY` | 299 |

## Forex

| Asset | RIC (use this in trades) | Asset ID |
|:--|:--|--:|
| AUD/CAD | `AUD/CAD` | 206 |
| AUD/JPY | `AUD/JPY` | 210 |
| AUD/NZD | `AUD/NZD-AFX` | 337 |
| AUD/USD | `AUD/USD` | 205 |
| CHF/JPY | `CHF/JPY` | 212 |
| EUR/CAD | `EUR/CAD` | 215 |
| EUR/GBP | `EUR/GBP` | 225 |
| EUR/JPY | `EUR/JPY` | 223 |
| EUR/MXN | `EUR/MXN-AFX` | 342 |
| EUR/NZD | `EUR/NZD-HSFX` | 339 |
| EUR/USD | `EURO` | 187 |
| GBP/JPY | `GBP/JPY` | 207 |
| GBP/NZD | `GBP/NZD-AFX` | 340 |
| NZD/JPY | `NZD/JPY` | 94 |
| NZD/USD | `NZD/USD` | 208 |
| USD/CAD | `USD/CAD` | 224 |
| USD/CHF | `USD/CHF` | 217 |
| USD/JPY | `USD/JPY` | 209 |
| USD/NOK | `USD/NOK` | 220 |

## Crypto

| Asset | RIC (use this in trades) | Asset ID |
|:--|:--|--:|
| ADA/USD | `ADA/USD-CXDXF` | 358 |
| ALTHBTC | `ALTHBTC/BTC-CXDXF` | 343 |
| BCH/USDT | `BCH/USDT-CXDXF` | 330 |
| BSV/USDT | `BSV/USDT-CXDXF` | 364 |
| Bitcoin | `XBT/USD` | 276 |
| LTC/USDT | `LTC/USDT-CXDXF` | 362 |
| Litecoin | `LTC/USD` | 277 |

## Indices

| Asset | RIC (use this in trades) | Asset ID |
|:--|:--|--:|
| AEX | `AEX` | 285 |
| Altcoin IDX | `ALTHUOB/BTC-CXDX` | 341 |
| CAC | `CAC` | 286 |
| Crypto IDX | `Z-CRY/IDX` | 347 |
| Dow Jones IA | `INDU` | 293 |
| EUR IDX | `EURX-DXF` | 335 |
| JPY IDX | `JPYX-DXF` | 336 |
| NASDAQ 100 | `NDX` | 294 |

## Stocks

| Asset | RIC (use this in trades) | Asset ID |
|:--|:--|--:|
| AIG | `AIG` | 267 |
| Boeing | `BA` | 257 |
| Coca Cola | `COKE` | 245 |
| Google | `GOOG` | 227 |
| IBM | `IBM` | 247 |
| JD | `JD` | 24 |
| McDonalds | `MCD` | 259 |
| Microsoft | `MSFT` | 255 |
| PayPal | `PYPL` | 22 |
| Vodafone | `VOD` | 262 |

## Metals

| Asset | RIC (use this in trades) | Asset ID |
|:--|:--|--:|
| Gold | `XAU/USD-HSFX` | 232 |
| Silver | `XAG/USD-AFX` | 231 |

## Asset missing?

Binomo adds and removes assets over time. If one you trade is missing or a RIC has changed, [open an issue](https://github.com/ChipaDevTeam/BinomoAPI/issues/new) or post it in [Discord](https://discord.gg/p7YyFqSmAz). The list lives in [`BinomoAPI/assets.json`](https://github.com/ChipaDevTeam/BinomoAPI/blob/main/BinomoAPI/assets.json), and pull requests are welcome.
