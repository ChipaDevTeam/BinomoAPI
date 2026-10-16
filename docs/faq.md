---
title: FAQ
description: Answers to common questions about the Binomo API for Python, including whether Binomo has an official API, building a trading bot, login errors, real accounts, assets and trade results.
nav_order: 11
faq:
  - q: Does Binomo have an official API?
    a: >-
      No. Binomo doesn't publish a public trading API. BinomoAPI is an unofficial, open-source Python
      library that talks to the same HTTP and WebSocket endpoints the Binomo web app uses.
  - q: How do I build a Binomo trading bot in Python?
    a: >-
      Install the library with `pip install BinomoAPI`, log in with `BinomoAPI.login()`, create a client with
      `BinomoAPI.create_from_login()` and call `place_call_option()` or `place_put_option()` whenever your
      strategy produces a signal. The [Getting Started](getting-started) guide and [Examples](examples)
      walk through it step by step.
  - q: Is BinomoAPI free?
    a: >-
      Yes. BinomoAPI is free and open source under the MIT License. You can use it in personal and commercial
      projects. If it saves you time, consider [supporting the project](community#support-the-project).
  - q: Can I trade on a real account, not just demo?
    a: >-
      Yes. Pass `demo=False` when you create the client, or `use_demo=False` on a single trade. Test on the demo
      account first. Binary options carry a high risk of loss.
  - q: Why does login fail with a 422 error?
    a: >-
      Binomo rejected the sign-in request. Common causes are a wrong password, an account that signs in through
      Google or Facebook (set a password on Binomo first), or too many attempts in a short time. Log in once in
      your browser, wait a few minutes and try again.
  - q: Can I log in with Google or Facebook?
    a: >-
      Not directly. BinomoAPI uses email and password. Set a password in your Binomo account settings and use
      your account email with it.
  - q: Which assets can I trade?
    a: >-
      BinomoAPI includes 52 assets, covering forex pairs, OTC pairs that are open 24/7, crypto, indices, stocks,
      gold and silver. See the [Asset List](assets) for every name and RIC code.
  - q: Why is my trade rejected when I pass "EUR/USD"?
    a: >-
      Trades must use the asset's RIC code, not its display name. EUR/USD is `EURO` and EUR/USD (OTC) is
      `Z-EUR/USD`. Look up any RIC on the [Asset List](assets).
  - q: How do I know whether my trade won?
    a: >-
      `place_call_option()` and `place_put_option()` return as soon as the order is sent, with status "submitted".
      Binomo's replies arrive on the WebSocket and can be inspected for debugging. A public trade-result API is
      on the roadmap. Until then, check your trade history on Binomo or follow progress in
      [Discord](https://discord.gg/p7YyFqSmAz).
  - q: Why does my 60-second trade last longer than 60 seconds?
    a: >-
      Binomo expiries snap to clock boundaries. A 60-second trade expires at the next full minute that is at
      least 30 seconds away, so the time in trade is between 30 and 90 seconds.
      [Read how expiry is calculated](trading#how-expiry-time-is-calculated).
  - q: Does it work on Windows, macOS and Linux?
    a: >-
      Yes. BinomoAPI is pure Python and runs anywhere Python 3.8 or newer runs, including servers and Raspberry Pi.
  - q: Is using a trading bot on Binomo allowed?
    a: >-
      That depends on Binomo's terms of service and the laws where you live, and it is your responsibility to check
      both. BinomoAPI is provided for educational and research purposes.
  - q: Can someone build a custom Binomo bot for me?
    a: >-
      Yes. ChipaDevTeam builds custom trading bots and strategies.
      [Tell us what you need](https://chipatrade.com/services/bot-development).
  - q: Where can I get help?
    a: >-
      Ask in our [Discord](https://discord.gg/p7YyFqSmAz), message the team on [Telegram](https://t.me/ChipaDevTeam)
      or [open a GitHub issue](https://github.com/ChipaDevTeam/BinomoAPI/issues).
---

# Frequently asked questions
{: .no_toc }

1. TOC
{:toc}

---

{% for item in page.faq %}
### {{ item.q }}

{{ item.a | markdownify }}
{% endfor %}
