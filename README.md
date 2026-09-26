# AI Trading & Finance Multi-Agent Desk

A safe, paper-trading prototype that orchestrates market research, quant signals, risk checks, execution, portfolio valuation, and compliance audit logging.

## Run

```bash
python af.py --symbol RELIANCE --capital 250000
python af.py --symbol RELIANCE --capital 250000 --json
```

The prototype uses deterministic synthetic market data and never places live orders.

## Optional Sarvam narrative

The research agent can ask Sarvam-105B to rewrite its market narrative. Install the SDK and set a new key through the environment:

```powershell
pip install sarvamai
$env:SARVAM_API_KEY="your-key"
python af.py
```

Never commit API keys. This is a prototype for paper trading, not investment advice.
