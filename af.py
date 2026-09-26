"""Paper-only AI trading desk prototype.

Run: python af.py | python af.py --symbol RELIANCE --capital 250000 --json
Optional Sarvam narrative: set SARVAM_API_KEY and install sarvamai.
"""
from __future__ import annotations
import argparse, json, math, os, random, statistics, uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

def ts() -> str: return datetime.now(timezone.utc).isoformat(timespec="seconds")

@dataclass
class Bar: symbol: str; close: float; volume: int; time: str
@dataclass
class Brief: symbol: str; price: float; trend: str; volatility: float; narrative: str; confidence: float; sources: List[str]
@dataclass
class Signal: symbol: str; action: str; entry: float; stop: float; target: float; quantity: int; rr: float; reasoning: List[str]; confidence: float
@dataclass
class Risk: approved: bool; quantity: int; risk_amount: float; reasons: List[str]
@dataclass
class Fill: order_id: str; symbol: str; side: str; quantity: int; price: float; status: str; time: str

class Audit:
    def __init__(self): self.events: List[Dict[str, Any]] = []
    def add(self, agent: str, event: str, payload: Any): self.events.append({"time": ts(), "agent": agent, "event": event, "payload": payload})

class MarketDataAgent:
    def history(self, symbol: str, days: int = 60) -> List[Bar]:
        rng, price, result = random.Random(symbol), 1000.0, []
        for i in range(days):
            price *= 1 + (0.0018 if i > days * .38 else .0002) + rng.gauss(0, .012)
            result.append(Bar(symbol, round(max(price, 1), 2), rng.randint(80000, 220000), f"D-{days-i}"))
        return result

class ResearchAgent:
    def analyze(self, bars: List[Bar]) -> Brief:
        closes = [b.close for b in bars]; fast, slow = statistics.mean(closes[-10:]), statistics.mean(closes[-30:])
        returns = [closes[i] / closes[i-1] - 1 for i in range(1, len(closes))]
        vol = statistics.pstdev(returns) * math.sqrt(252)
        trend = "bullish" if fast > slow * 1.01 else "bearish" if fast < slow * .99 else "neutral"
        confidence = round(min(.95, max(.45, .55 + abs(fast / slow - 1) * 8)), 2)
        narrative = f"10-day average {fast:.2f} vs 30-day average {slow:.2f}; annualized volatility {vol:.1%}."
        api_key = os.getenv("SARVAM_API_KEY")
        if api_key:
            try:
                from sarvamai import SarvamAI
                client = SarvamAI(api_subscription_key=api_key)
                response = client.chat.completions(model="sarvam-105b", messages=[{"role":"user", "content": "Rewrite this market observation in one cautious sentence: " + narrative}], temperature=.2, max_tokens=100)
                narrative = response.choices[0].message.content.strip()
            except Exception as exc: narrative += f" (Sarvam unavailable: {type(exc).__name__})"
        return Brief(bars[-1].symbol, closes[-1], trend, vol, narrative, confidence, ["synthetic OHLCV demo feed", "moving averages", "realized volatility"])

class QuantSignalAgent:
    def generate(self, brief: Brief, capital: float) -> Signal:
        entry, stop_pct = brief.price, min(.08, max(.025, brief.volatility / math.sqrt(252) * 2.2))
        if brief.trend == "bullish" and brief.confidence >= .58:
            action, stop, target = "BUY", entry * (1-stop_pct), entry * (1+2*stop_pct); why = ["fast average above slow average", "confidence clears threshold"]
        elif brief.trend == "bearish" and brief.confidence >= .58:
            action, stop, target = "SELL", entry * (1+stop_pct), entry * (1-2*stop_pct); why = ["fast average below slow average", "confidence clears threshold"]
        else: action, stop, target, why = "HOLD", entry, entry, ["trend is not strong enough"]
        risk_per_share = abs(entry-stop); qty = int(capital*.01/risk_per_share) if risk_per_share else 0
        return Signal(brief.symbol, action, round(entry,2), round(stop,2), round(target,2), qty, round(abs(target-entry)/risk_per_share,2) if risk_per_share else 0, why, brief.confidence)

class RiskAgent:
    def approve(self, signal: Signal, cash: float) -> Risk:
        if signal.action == "HOLD": return Risk(False, 0, 0, ["no actionable signal"])
        per_share, budget = abs(signal.entry-signal.stop), cash*.01; qty = min(signal.quantity, int(budget/per_share) if per_share else 0); amount = qty*per_share
        reasons = (["risk/reward below 1.5"] if signal.rr < 1.5 else []) + (["zero quantity under risk budget"] if qty == 0 else [])
        return Risk(not reasons, qty, round(amount,2), reasons or ["within 1% portfolio risk budget"])

class PaperExecutionAgent:
    def execute(self, signal: Signal, risk: Risk) -> Optional[Fill]:
        return Fill(str(uuid.uuid4())[:8], signal.symbol, signal.action, risk.quantity, signal.entry, "PAPER_FILLED", ts()) if risk.approved else None

class DeskManager:
    def __init__(self, capital: float): self.cash, self.start, self.audit, self.position = capital, capital, Audit(), 0
    def run(self, symbol: str) -> Dict[str, Any]:
        brief = ResearchAgent().analyze(MarketDataAgent().history(symbol)); self.audit.add("research", "brief", asdict(brief))
        signal = QuantSignalAgent().generate(brief, self.cash); self.audit.add("quant", "signal", asdict(signal))
        risk = RiskAgent().approve(signal, self.cash); self.audit.add("risk", "decision", asdict(risk))
        fill = PaperExecutionAgent().execute(signal, risk)
        if fill:
            direction = 1 if fill.side == "BUY" else -1
            self.position += direction * fill.quantity
            self.cash -= direction * fill.quantity * fill.price
            self.audit.add("execution", "paper_fill", asdict(fill))
        compliance = {"status": "PASS" if risk.approved or signal.action == "HOLD" else "REVIEW", "paper_only": True, "reasoning_logged": True}
        self.audit.add("compliance", "review", compliance)
        equity = self.cash + self.position * brief.price
        return {"mode":"PAPER_ONLY", "research":asdict(brief), "signal":asdict(signal), "risk":asdict(risk), "fill":asdict(fill) if fill else None, "portfolio":{"cash":round(self.cash,2),"position":self.position,"equity":round(equity,2),"pnl":round(equity-self.start,2)}, "compliance":compliance, "audit_events":self.audit.events}

def main():
    p = argparse.ArgumentParser(); p.add_argument("--symbol", default="NIFTY-DEMO"); p.add_argument("--capital", type=float, default=100000); p.add_argument("--json", action="store_true"); a = p.parse_args()
    out = DeskManager(a.capital).run(a.symbol.upper())
    if a.json: print(json.dumps(out, indent=2)); return
    print(f"AI Trading Desk | {out['mode']} | {a.symbol.upper()}")
    print(f"Research: {out['research']['trend']} | confidence {out['research']['confidence']:.0%}")
    print(f"Signal: {out['signal']['action']} {out['signal']['quantity']} @ {out['signal']['entry']:.2f}")
    print(f"Risk: {'APPROVED' if out['risk']['approved'] else 'REJECTED'} — {', '.join(out['risk']['reasons'])}")
    print(f"Fill: {out['fill']['status'] if out['fill'] else 'none'} | Cash: {out['portfolio']['cash']:.2f} | Audit events: {len(out['audit_events'])}")

if __name__ == "__main__": main()
