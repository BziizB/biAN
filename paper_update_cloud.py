from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import paper_update as base

BINANCE_BASE_URLS = [
    "https://data-api.binance.vision",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
    "https://api.binance.com",
]


def request_klines(symbol: str, end_ms: int):
    params = urllib.parse.urlencode({"symbol": symbol, "interval": "15m", "limit": 1000, "endTime": end_ms})
    last_error: Exception | None = None
    for base_url in BINANCE_BASE_URLS:
        url = f"{base_url}/api/v3/klines?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "paper-trading-monitor/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    return []


def fetch_bars(market, target_bars=base.FETCH_TARGET_BARS):
    symbol = f"{market}USDT"
    end_ms = int(time.time() * 1000)
    all_rows = []
    while len(all_rows) < target_bars:
        data = request_klines(symbol, end_ms)
        if not data:
            break
        chunk = []
        now_ms = int(time.time() * 1000)
        for item in data:
            open_ms = int(item[0])
            if open_ms + base.BAR_MS > now_ms:
                continue
            chunk.append({
                "time": datetime.fromtimestamp(open_ms / 1000, tz=timezone.utc).replace(tzinfo=None),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5]),
            })
        all_rows = chunk + all_rows
        first_open = int(data[0][0])
        if len(data) < 1000:
            break
        end_ms = first_open - 1
        time.sleep(0.05)
    dedup = {row["time"]: row for row in all_rows}
    rows = [dedup[key] for key in sorted(dedup.keys())]
    return rows[-target_bars:]


def main():
    base.ensure_files()
    state = base.load_state()
    state["fetch_errors"] = {}
    all_new_signals = []
    all_new_entries = []
    all_closed = []
    strategies = {}
    latest_processed = None
    for market in base.MARKETS:
        try:
            bars = fetch_bars(market)
            strategy = base.compute_strategy(bars)
            strategies[market] = strategy
            new_signals, new_entries, closed_ids, latest = base.process_market(state, market, strategy)
            all_new_signals.extend(new_signals)
            all_new_entries.extend(new_entries)
            all_closed.extend(closed_ids)
            if latest:
                latest_processed = max(latest_processed, latest) if latest_processed else latest
        except Exception as exc:
            state.setdefault("fetch_errors", {})[market] = str(exc)
            print(f"fetch/process error for {market}: {exc}")
    consistency = base.consistency_check(strategies)
    state["consistency"] = consistency
    report_date = latest_processed or datetime.utcnow()
    warnings = base.evaluate_warnings(base.closed_trades(), report_date, float(consistency.get("mismatch_rate", 0.0)))
    if state.get("fetch_errors"):
        warnings.append(f"Market data fetch errors: {len(state['fetch_errors'])}/{len(base.MARKETS)} markets")
    if latest_processed is None:
        warnings.append("No closed Binance 15M data processed; paper state is stale")
    state["warnings"] = warnings
    state["last_run_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state["last_data_time"] = base.ts_text(latest_processed) if latest_processed else state.get("last_data_time")
    base.save_state(state)
    base.build_report(state, report_date, warnings)
    cumulative = sum(float(t["net_R"]) for t in base.closed_trades())
    open_positions = [m for m, s in state["markets"].items() if s.get("position_status") == "OPEN"]
    print(f"data_end={state.get('last_data_time')}")
    print(f"new_signals={len(all_new_signals)} {' '.join(all_new_signals)}")
    print(f"open_positions={len(open_positions)} {' '.join(open_positions)}")
    print(f"new_entries={len(all_new_entries)} {' '.join(all_new_entries)}")
    print(f"closed_trades={len(all_closed)} {' '.join(all_closed)}")
    print(f"cumulative_paper_net_R={cumulative:.4f}")
    print(f"warning={bool(warnings)}")
    if warnings:
        print("warning_reasons=" + " | ".join(warnings))
    print("conclusion=Current strategy is in paper trading observation stage.")


if __name__ == "__main__":
    main()
