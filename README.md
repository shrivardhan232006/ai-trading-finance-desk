# AI Trading & Finance Multi-Agent Desk

An AI-assisted trading and wealth-management control room that models the complete investment workflow: market research → signal generation → risk approval → paper execution → portfolio review → audit.

> **Current status:** working paper-trading prototype. It uses deterministic synthetic market data and never places live orders.

## Why this project?

Trading decisions often become fragmented across news, charts, risk spreadsheets, broker screens, and post-trade journals. This project explores how specialized agents can collaborate around one decision trail while keeping position sizing, risk limits, and human oversight explicit.

The design is intentionally safety-first: every signal includes entry, stop loss, target, quantity, risk/reward, and reasoning; every approved or rejected decision is written to an audit trail.

## Features

- **Market Research Agent** — calculates trend, realized volatility, confidence, narrative, and source metadata from market bars.
- **Quant Signal Agent** — generates BUY, SELL, or HOLD decisions using moving-average trend confirmation and volatility-adjusted stops and targets.
- **Risk Management Agent** — limits trade risk to 1% of available capital and rejects weak risk/reward or zero-sized trades.
- **Paper Execution Agent** — simulates fills with order IDs and timestamps.
- **Portfolio Agent** — tracks cash, long/short paper positions, equity, and P&L.
- **Compliance Agent** — checks that the flow stayed paper-only and that reasoning was logged.
- **Audit trail** — records each research brief, signal, risk decision, fill, and compliance review.
- **Browser dashboard** — displays the full desk cycle through a lightweight local web UI.
- **Optional Sarvam integration** — uses Sarvam-105B to rewrite the generated research narrative when `SARVAM_API_KEY` is configured.

## Architecture

```text
Browser dashboard
       │
       ▼
Python HTTP server ──► Desk Manager
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   Research           Quant Signal       Risk Management
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                   Paper Execution
                           │
                 Portfolio + Compliance
                           │
                     Audit events
```

## Quick start

Run the command-line desk:

```bash
python trading-bot.py --symbol RELIANCE --capital 250000
```

Get machine-readable output:

```bash
python trading-bot.py --symbol RELIANCE --capital 250000 --json
```

Start the dashboard:

```bash
python trading-bot.py --serve --port 8000
```

Then open [http://localhost:8000](http://localhost:8000). Enter a symbol and capital amount, then select **Run desk** to execute one paper-trading cycle.

## Optional Sarvam narrative

The core prototype runs without external dependencies. To enable Sarvam-105B narrative generation, install the official SDK and provide the key through an environment variable:

```powershell
pip install sarvamai
$env:SARVAM_API_KEY="your-new-key"
python trading-bot.py --symbol RELIANCE
```

Never hard-code or commit API keys. If a key has previously been exposed, revoke it and create a replacement before use.

## Example workflow

1. The market-data adapter creates a reproducible 60-bar demo history.
2. Research calculates 10-day and 30-day averages plus annualized realized volatility.
3. Quant converts the trend into a signal with volatility-adjusted stop and target levels.
4. Risk sizes the position against a 1% capital-risk budget.
5. Execution creates a simulated fill only when risk approves the trade.
6. Portfolio updates cash, position, equity, and P&L.
7. Compliance records the result and exposes the full reasoning trail to the dashboard.

## Safety boundaries

This repository is for engineering and experimentation, not financial advice. It does not connect to Zerodha, Interactive Brokers, exchanges, or any live brokerage account. Synthetic data is not suitable for evaluating real strategy performance. Before any live use, the system would need licensed data, historical backtesting, paper-trading validation, broker integration, authentication, monitoring, stronger portfolio constraints, and regulatory review.

## Roadmap

- Add pluggable NSE/BSE and broker data adapters.
- Add historical backtesting with transaction costs and slippage.
- Add sector concentration, correlation, drawdown, and stress-test controls.
- Add human approval gates for configurable risk thresholds.
- Add persistent storage for fills, journals, and portfolio history.
- Add authentication and role-based access for a shared dashboard.
- Add broker adapters only behind an explicit, separately configured live-trading mode.

## Files

| File | Purpose |
| --- | --- |
| `trading-bot.py` | Multi-agent orchestration, CLI, paper engine, and local API server |
| `index.html` | Dashboard markup |
| `styles.css` | Dashboard styling and responsive layout |
| `app.js` | Dashboard interactions and API rendering |

## License

This project is currently shared as an educational prototype. Add a license before accepting external contributions or redistributing it.
