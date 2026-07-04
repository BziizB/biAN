from __future__ import annotations

import csv
import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path.cwd()
PAPER_DIR = ROOT / "paper_trading"
STATE_PATH = PAPER_DIR / "state.json"
TRADES_PATH = PAPER_DIR / "paper_trades.csv"
SIGNALS_PATH = PAPER_DIR / "paper_signals.csv"
REPORT_PATH = PAPER_DIR / "paper_daily_report.md"
MISMATCH_PATH = PAPER_DIR / "mismatch_report.csv"

MARKETS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "LINK", "AVAX", "LTC"]
BAR_MINUTES = 15
BAR_MS = BAR_MINUTES * 60 * 1000
SWING_SIZE = 50
ADX_THRESHOLD = 30.0
ATR_PERIOD = 14
SL_ATR = 3.0
TP_R = 3.0
MAX_HOLDING_BARS = 64
FEE_RATE = 0.0006
SLIPPAGE_RATE = 0.0002
FETCH_TARGET_BARS = 96 * 100
HISTORICAL_MAX_DD_R = 39.87957723494097

TRADE_COLUMNS = [
    "trade_id", "market", "direction", "signal_time", "entry_time", "entry_price",
    "atr_at_entry", "stop_loss", "take_profit", "exit_time", "exit_price", "exit_reason",
    "gross_R", "cost_R", "net_R", "bars_held", "adx_at_signal", "bos_level",
    "mfe_R", "mae_R", "status",
]
SIGNAL_COLUMNS = [
    "signal_id", "market", "signal_time", "close", "atr14", "adx", "swing_high_level",
    "swing_low_level", "bos_direction", "signal_valid", "skip_reason", "position_exists",
]
MISMATCH_COLUMNS = [
    "market", "signal_time", "paper_signal_valid", "research_signal_valid", "paper_atr14",
    "research_atr14", "paper_adx", "research_adx", "paper_bos_level", "research_bos_level",
    "signal_time_offset_bars", "pivot_repaint_suspect", "indicator_mismatch", "mismatch",
    "mismatch_reason",
]


def ts_text(value):
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        return value[:19]
    return value.strftime("%Y-%m-%d %H:%M:%S")


def parse_time(text):
    if not text:
        return None
    return datetime.strptime(str(text)[:19], "%Y-%m-%d %H:%M:%S")


def finite_float(value):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def read_table(path, columns):
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_table(path, columns, rows):
    PAPER_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def ensure_files():
    PAPER_DIR.mkdir(parents=True, exist_ok=True)
    for path, cols in [(TRADES_PATH, TRADE_COLUMNS), (SIGNALS_PATH, SIGNAL_COLUMNS), (MISMATCH_PATH, MISMATCH_COLUMNS)]:
        if not path.exists():
            write_table(path, cols, [])


def append_unique(path, columns, row, key):
    rows = read_table(path, columns)
    if str(row.get(key, "")) in {str(item.get(key, "")) for item in rows}:
        return False
    rows.append(row)
    write_table(path, columns, rows)
    return True


def upsert_trade(row):
    rows = read_table(TRADES_PATH, TRADE_COLUMNS)
    found = False
    for i, item in enumerate(rows):
        if str(item.get("trade_id")) == str(row.get("trade_id")):
            rows[i] = row
            found = True
            break
    if not found:
        rows.append(row)
    write_table(TRADES_PATH, TRADE_COLUMNS, rows)


def rma(values, period):
    out = []
    prev = None
    alpha = 1.0 / period
    for value in values:
        x = finite_float(value)
        if x is None:
            out.append(prev)
            continue
        if prev is None:
            prev = x
        else:
            prev = prev + alpha * (x - prev)
        out.append(prev)
    return out


def default_market_state(market):
    return {
        "market": market,
        "position_status": "FLAT",
        "trade_id": None,
        "entry_time": None,
        "entry_price": None,
        "entry_close": None,
        "atr_at_entry": None,
        "risk_per_unit": None,
        "stop_loss": None,
        "take_profit": None,
        "bars_held": 0,
        "max_holding_bars": MAX_HOLDING_BARS,
        "signal_time": None,
        "signal_details": {},
        "unrealized_R": 0.0,
        "mfe_R": 0.0,
        "mae_R": 0.0,
        "last_processed_bar": None,
    }


def load_state():
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    else:
        state = {}
    state.setdefault("version", 1)
    state.setdefault("strategy_name", "Swing Bullish BOS + strong ADX")
    state.setdefault("status", "Paper Trading Candidate")
    state.setdefault("created_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    state.setdefault("last_run_at", None)
    state.setdefault("last_data_time", None)
    state.setdefault("next_trade_seq", 1)
    state.setdefault("warnings", [])
    state.setdefault("consistency", {"mismatch_rate": 0.0, "mismatches": 0, "comparable_rows": 0})
    state.setdefault("markets", {})
    for market in MARKETS:
        base = default_market_state(market)
        base.update(state["markets"].get(market, {}))
        state["markets"][market] = base
    return state


def save_state(state):
    PAPER_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATE_PATH)


def fetch_bars(market, target_bars=FETCH_TARGET_BARS):
    symbol = f"{market}USDT"
    end_ms = int(time.time() * 1000)
    all_rows = []
    while len(all_rows) < target_bars:
        params = urllib.parse.urlencode({"symbol": symbol, "interval": "15m", "limit": 1000, "endTime": end_ms})
        url = f"https://api.binance.com/api/v3/klines?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "paper-trading-monitor/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data:
            break
        chunk = []
        now_ms = int(time.time() * 1000)
        for item in data:
            open_ms = int(item[0])
            if open_ms + BAR_MS > now_ms:
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


def compute_strategy(rows):
    n = len(rows)
    highs = [r["high"] for r in rows]
    lows = [r["low"] for r in rows]
    closes = [r["close"] for r in rows]
    tr = []
    plus_dm = []
    minus_dm = []
    for i in range(n):
        if i == 0:
            tr.append(highs[i] - lows[i])
            plus_dm.append(0.0)
            minus_dm.append(0.0)
            continue
        tr.append(max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])))
        up_move = highs[i] - highs[i - 1]
        down_move = lows[i - 1] - lows[i]
        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0.0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0.0)
    atr14 = rma(tr, ATR_PERIOD)
    plus_rma = rma(plus_dm, ATR_PERIOD)
    minus_rma = rma(minus_dm, ATR_PERIOD)
    dx = []
    for i in range(n):
        base = finite_float(atr14[i])
        if base is None or base <= 0:
            dx.append(None)
            continue
        plus_di = 100.0 * plus_rma[i] / base
        minus_di = 100.0 * minus_rma[i] / base
        denom = plus_di + minus_di
        dx.append(100.0 * abs(plus_di - minus_di) / denom if denom > 0 else None)
    adx14 = rma(dx, ATR_PERIOD)

    pivot_high = None
    pivot_low = None
    high_crossed = True
    low_crossed = True
    bias = 0
    out = []
    for i, bar in enumerate(rows):
        swing_bull_bos = False
        swing_bear_bos = False
        swing_bull_choch = False
        swing_bear_choch = False
        bos_level = None
        if i >= SWING_SIZE * 2:
            j = i - SWING_SIZE
            left = j - SWING_SIZE
            right = j + SWING_SIZE + 1
            if highs[j] == max(highs[left:right]):
                pivot_high = highs[j]
                high_crossed = False
            if lows[j] == min(lows[left:right]):
                pivot_low = lows[j]
                low_crossed = False
            if pivot_high is not None and not high_crossed and closes[i] > pivot_high:
                if bias == -1:
                    swing_bull_choch = True
                else:
                    swing_bull_bos = True
                bos_level = pivot_high
                high_crossed = True
                bias = 1
            if pivot_low is not None and not low_crossed and closes[i] < pivot_low:
                if bias == 1:
                    swing_bear_choch = True
                else:
                    swing_bear_bos = True
                bos_level = pivot_low
                low_crossed = True
                bias = -1
        atr_val = finite_float(atr14[i])
        adx_val = finite_float(adx14[i])
        signal_valid = bool(swing_bull_bos and atr_val is not None and atr_val > 0 and adx_val is not None and adx_val >= ADX_THRESHOLD)
        item = dict(bar)
        item.update({
            "atr14": atr_val,
            "adx": adx_val,
            "swing_bull_bos": swing_bull_bos,
            "swing_bear_bos": swing_bear_bos,
            "swing_bull_choch": swing_bull_choch,
            "swing_bear_choch": swing_bear_choch,
            "swing_high_level": pivot_high,
            "swing_low_level": pivot_low,
            "bos_level": bos_level,
            "signal_valid": signal_valid,
        })
        out.append(item)
    return out


def active(ms):
    return ms.get("position_status") == "OPEN"


def signal_skip_reason(row):
    if not row.get("swing_bull_bos"):
        return "no_signal"
    atr_val = finite_float(row.get("atr14"))
    adx_val = finite_float(row.get("adx"))
    if atr_val is None or atr_val <= 0 or adx_val is None:
        return "indicator_not_ready"
    if adx_val < ADX_THRESHOLD:
        return "adx_below_30"
    return ""


def make_signal_row(market, row, valid_signal, skip_reason, position_exists):
    stamp = row["time"].strftime("%Y%m%d%H%M")
    return {
        "signal_id": f"{market}_{stamp}",
        "market": market,
        "signal_time": ts_text(row["time"]),
        "close": row["close"],
        "atr14": row.get("atr14"),
        "adx": row.get("adx"),
        "swing_high_level": row.get("swing_high_level"),
        "swing_low_level": row.get("swing_low_level"),
        "bos_direction": "bullish" if row.get("swing_bull_bos") else "",
        "signal_valid": bool(valid_signal),
        "skip_reason": skip_reason,
        "position_exists": bool(position_exists),
    }


def open_position(state, market, row):
    seq = int(state.get("next_trade_seq", 1))
    trade_id = f"PT-{seq:06d}-{market}"
    state["next_trade_seq"] = seq + 1
    entry_close = float(row["close"])
    atr_value = float(row["atr14"])
    risk_per_unit = SL_ATR * atr_value
    stop_loss = entry_close - risk_per_unit
    take_profit = entry_close + TP_R * risk_per_unit
    entry_price = entry_close * (1.0 + SLIPPAGE_RATE)
    state["markets"][market].update({
        "position_status": "OPEN",
        "trade_id": trade_id,
        "entry_time": ts_text(row["time"]),
        "entry_price": entry_price,
        "entry_close": entry_close,
        "atr_at_entry": atr_value,
        "risk_per_unit": risk_per_unit,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "bars_held": 0,
        "max_holding_bars": MAX_HOLDING_BARS,
        "signal_time": ts_text(row["time"]),
        "signal_details": {
            "adx_at_signal": row.get("adx"),
            "bos_level": row.get("bos_level"),
            "swing_high_level": row.get("swing_high_level"),
            "swing_low_level": row.get("swing_low_level"),
        },
        "unrealized_R": 0.0,
        "mfe_R": 0.0,
        "mae_R": 0.0,
    })
    upsert_trade({
        "trade_id": trade_id, "market": market, "direction": "LONG", "signal_time": ts_text(row["time"]),
        "entry_time": ts_text(row["time"]), "entry_price": entry_price, "atr_at_entry": atr_value,
        "stop_loss": stop_loss, "take_profit": take_profit, "exit_time": "", "exit_price": "",
        "exit_reason": "", "gross_R": "", "cost_R": "", "net_R": "", "bars_held": 0,
        "adx_at_signal": row.get("adx"), "bos_level": row.get("bos_level"), "mfe_R": 0.0,
        "mae_R": 0.0, "status": "OPEN",
    })
    return trade_id


def close_position(state, market, row, raw_exit_price, exit_price, exit_reason):
    ms = state["markets"][market]
    trade_id = str(ms["trade_id"])
    entry_price = float(ms["entry_price"])
    risk_per_unit = float(ms["risk_per_unit"])
    fees = FEE_RATE * entry_price + FEE_RATE * exit_price
    gross_r = (exit_price - entry_price) / risk_per_unit
    cost_r = fees / risk_per_unit
    net_r = gross_r - cost_r
    trade_row = {
        "trade_id": trade_id, "market": market, "direction": "LONG", "signal_time": ms.get("signal_time", ""),
        "entry_time": ms.get("entry_time", ""), "entry_price": entry_price, "atr_at_entry": ms.get("atr_at_entry"),
        "stop_loss": ms.get("stop_loss"), "take_profit": ms.get("take_profit"), "exit_time": ts_text(row["time"]),
        "exit_price": exit_price, "exit_reason": exit_reason, "gross_R": gross_r, "cost_R": cost_r,
        "net_R": net_r, "bars_held": int(ms.get("bars_held", 0)),
        "adx_at_signal": ms.get("signal_details", {}).get("adx_at_signal"),
        "bos_level": ms.get("signal_details", {}).get("bos_level"), "mfe_R": ms.get("mfe_R", 0.0),
        "mae_R": ms.get("mae_R", 0.0), "status": "CLOSED",
    }
    upsert_trade(trade_row)
    last_processed = ms.get("last_processed_bar")
    state["markets"][market] = default_market_state(market)
    state["markets"][market]["last_processed_bar"] = last_processed
    return trade_id


def update_open_position(state, market, row):
    ms = state["markets"][market]
    if not active(ms):
        return None
    entry_time = parse_time(ms.get("entry_time"))
    if entry_time and row["time"] <= entry_time:
        return None
    entry_close = float(ms["entry_close"])
    risk = float(ms["risk_per_unit"])
    stop_loss = float(ms["stop_loss"])
    take_profit = float(ms["take_profit"])
    high = float(row["high"])
    low = float(row["low"])
    close = float(row["close"])
    ms["bars_held"] = int(ms.get("bars_held", 0)) + 1
    ms["mfe_R"] = max(float(ms.get("mfe_R", 0.0)), max(0.0, (high - entry_close) / risk))
    ms["mae_R"] = max(float(ms.get("mae_R", 0.0)), max(0.0, (entry_close - low) / risk))
    ms["unrealized_R"] = (close * (1.0 - SLIPPAGE_RATE) - float(ms["entry_price"])) / risk
    if low <= stop_loss:
        return close_position(state, market, row, stop_loss, stop_loss * (1.0 - SLIPPAGE_RATE), "SL")
    if high >= take_profit:
        return close_position(state, market, row, take_profit, take_profit * (1.0 - SLIPPAGE_RATE), "TP")
    if int(ms["bars_held"]) >= MAX_HOLDING_BARS:
        return close_position(state, market, row, close, close * (1.0 - SLIPPAGE_RATE), "TIME")
    return None


def process_market(state, market, strategy):
    if not strategy:
        return [], [], [], None
    ms = state["markets"][market]
    if not ms.get("last_processed_bar"):
        idx = max(0, len(strategy) - 2)
        ms["last_processed_bar"] = ts_text(strategy[idx]["time"])
    last_processed = parse_time(ms.get("last_processed_bar"))
    process_rows = [row for row in strategy if last_processed is None or row["time"] > last_processed]
    new_signals = []
    new_entries = []
    closed = []
    latest = None
    for row in process_rows:
        position_at_start = active(state["markets"][market])
        closed_id = update_open_position(state, market, row)
        if closed_id:
            closed.append(closed_id)
        position_blocks_signal = position_at_start or bool(closed_id)
        valid_signal = bool(row.get("signal_valid"))
        skip_reason = signal_skip_reason(row)
        if valid_signal and position_blocks_signal:
            skip_reason = "position_exists"
        if row.get("swing_bull_bos"):
            sig = make_signal_row(market, row, valid_signal, skip_reason, position_blocks_signal)
            if append_unique(SIGNALS_PATH, SIGNAL_COLUMNS, sig, "signal_id") and valid_signal:
                new_signals.append(sig["signal_id"])
        if valid_signal and not position_blocks_signal:
            new_entries.append(open_position(state, market, row))
        state["markets"][market]["last_processed_bar"] = ts_text(row["time"])
        latest = row["time"]
    return new_signals, new_entries, closed, latest


def closed_trades():
    rows = []
    for row in read_table(TRADES_PATH, TRADE_COLUMNS):
        if str(row.get("status", "")).upper() != "CLOSED":
            continue
        net = finite_float(row.get("net_R"))
        if net is None:
            continue
        row["net_R"] = net
        row["exit_dt"] = parse_time(row.get("exit_time"))
        rows.append(row)
    return rows


def profit_factor(values):
    wins = sum(v for v in values if v > 0)
    losses = -sum(v for v in values if v < 0)
    return None if losses <= 0 else wins / losses


def drawdown(values):
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    current_dd = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        current_dd = peak - equity
        max_dd = max(max_dd, current_dd)
    return max_dd, current_dd


def consecutive_losses(values):
    best = 0
    cur = 0
    for value in values:
        if value < 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def evaluate_warnings(trades, report_date, mismatch_rate):
    warnings = []
    net = [float(t["net_R"]) for t in trades]
    if len(net) >= 20 and sum(net[-20:]) < -10.0:
        warnings.append("Last 20 trades net_R below -10R")
    if len(net) >= 60 and sum(net[-60:]) / 60.0 < 0.0:
        warnings.append("Last 60 trades avg_R below 0")
    if len(net) >= 60:
        pf60 = profit_factor(net[-60:])
        if pf60 is not None and pf60 < 1.0:
            warnings.append("Last 60 trades PF below 1.0")
    if consecutive_losses(net) >= 12:
        warnings.append("Consecutive losses reached 12 or more")
    _, current_dd = drawdown(net)
    if current_dd >= 20.0:
        warnings.append("Current drawdown reached 20R or more")
    month_start = datetime(report_date.year, report_date.month, 1)
    m = month_start.month - 2
    y = month_start.year
    while m <= 0:
        m += 12
        y -= 1
    three_month_start = datetime(y, m, 1)
    month_after = month_start + timedelta(days=32)
    three_month_net = sum(float(t["net_R"]) for t in trades if t.get("exit_dt") and three_month_start <= t["exit_dt"] < month_after)
    if trades and three_month_net < 0:
        warnings.append("Recent 3 calendar months cumulative net_R below 0")
    for market in ["BTC", "ADA", "LTC"]:
        vals = [float(t["net_R"]) for t in trades if t.get("market") == market]
        if len(vals) >= 30 and sum(vals[-30:]) / 30.0 < 0.0:
            warnings.append(f"{market} last 30 trades avg_R below 0")
    if mismatch_rate > 0.01:
        warnings.append(f"Backtest/realtime mismatch_rate above 1%: {mismatch_rate:.2%}")
    return warnings


def consistency_check(strategies):
    logs = read_table(SIGNALS_PATH, SIGNAL_COLUMNS)
    if not logs:
        write_table(MISMATCH_PATH, MISMATCH_COLUMNS, [])
        return {"mismatch_rate": 0.0, "mismatches": 0, "comparable_rows": 0}
    times = [parse_time(row.get("signal_time")) for row in logs]
    times = [t for t in times if t]
    if not times:
        write_table(MISMATCH_PATH, MISMATCH_COLUMNS, [])
        return {"mismatch_rate": 0.0, "mismatches": 0, "comparable_rows": 0}
    start = max(times) - timedelta(days=90)
    rows = []
    for market in MARKETS:
        strategy = strategies.get(market, [])
        by_time = {ts_text(row["time"]): row for row in strategy}
        valid_times = [row["time"] for row in strategy if row.get("signal_valid")]
        for log in logs:
            if log.get("market") != market:
                continue
            ts = parse_time(log.get("signal_time"))
            if not ts or ts < start:
                continue
            key = ts_text(ts)
            research = by_time.get(key)
            if research is None:
                nearest_offset = ""
                if valid_times:
                    nearest = min(valid_times, key=lambda x: abs((x - ts).total_seconds()))
                    nearest_offset = int(round((nearest - ts).total_seconds() / (BAR_MINUTES * 60)))
                rows.append({"market": market, "signal_time": key, "paper_signal_valid": log.get("signal_valid"), "research_signal_valid": "", "signal_time_offset_bars": nearest_offset, "pivot_repaint_suspect": "", "indicator_mismatch": True, "mismatch": True, "mismatch_reason": "paper_signal_time_not_in_research_frame"})
                continue
            reasons = []
            paper_valid = as_bool(log.get("signal_valid"))
            research_valid = bool(research.get("signal_valid"))
            if paper_valid != research_valid:
                reasons.append("signal_valid_mismatch")
            paper_atr = finite_float(log.get("atr14"))
            paper_adx = finite_float(log.get("adx"))
            research_atr = finite_float(research.get("atr14"))
            research_adx = finite_float(research.get("adx"))
            indicator_mismatch = False
            if paper_atr is not None and research_atr is not None and abs(paper_atr - research_atr) > max(1e-10, abs(research_atr) * 1e-9):
                indicator_mismatch = True
                reasons.append("atr_mismatch")
            if paper_adx is not None and research_adx is not None and abs(paper_adx - research_adx) > max(1e-10, abs(research_adx) * 1e-9):
                indicator_mismatch = True
                reasons.append("adx_mismatch")
            repaint = False
            if paper_valid or research_valid:
                prefix = [r for r in strategy if r["time"] <= ts]
                if prefix:
                    prefix_valid = compute_strategy(prefix)[-1].get("signal_valid")
                    if bool(prefix_valid) != research_valid:
                        repaint = True
                        reasons.append("confirmed_pivot_repaint_suspect")
            rows.append({
                "market": market, "signal_time": key, "paper_signal_valid": paper_valid,
                "research_signal_valid": research_valid, "paper_atr14": paper_atr, "research_atr14": research_atr,
                "paper_adx": paper_adx, "research_adx": research_adx,
                "paper_bos_level": finite_float(log.get("swing_high_level")), "research_bos_level": finite_float(research.get("bos_level")),
                "signal_time_offset_bars": 0, "pivot_repaint_suspect": repaint,
                "indicator_mismatch": indicator_mismatch, "mismatch": bool(reasons), "mismatch_reason": ";".join(reasons),
            })
    write_table(MISMATCH_PATH, MISMATCH_COLUMNS, rows)
    comparable = len(rows)
    mismatches = sum(1 for row in rows if as_bool(row.get("mismatch")))
    return {"mismatch_rate": mismatches / comparable if comparable else 0.0, "mismatches": mismatches, "comparable_rows": comparable}


def markdown_table(rows, columns, max_rows=None):
    if not rows:
        return "_No rows._"
    view = rows[-max_rows:] if max_rows else rows
    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in view:
        cells = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                cells.append(f"{val:.4f}")
            else:
                cells.append(str(val))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def build_report(state, report_date, warnings):
    trades = closed_trades()
    all_trades = read_table(TRADES_PATH, TRADE_COLUMNS)
    signals = read_table(SIGNALS_PATH, SIGNAL_COLUMNS)
    date_start = datetime(report_date.year, report_date.month, report_date.day)
    date_end = date_start + timedelta(days=1)
    daily_closed = [t for t in trades if t.get("exit_dt") and date_start <= t["exit_dt"] < date_end]
    daily_entries = [t for t in all_trades if (parse_time(t.get("entry_time")) or datetime.min) >= date_start and (parse_time(t.get("entry_time")) or datetime.min) < date_end]
    daily_signals = [s for s in signals if (parse_time(s.get("signal_time")) or datetime.min) >= date_start and (parse_time(s.get("signal_time")) or datetime.min) < date_end and as_bool(s.get("signal_valid"))]
    net = [float(t["net_R"]) for t in trades]
    cumulative = sum(net)
    avg = cumulative / len(net) if net else None
    win_rate = sum(1 for v in net if v > 0) / len(net) if net else None
    pf = profit_factor(net)
    max_dd, current_dd = drawdown(net)
    by_market = []
    for market in MARKETS:
        vals = [float(t["net_R"]) for t in trades if t.get("market") == market]
        if vals:
            by_market.append({"market": market, "trades": len(vals), "net_R": sum(vals), "avg_R": sum(vals) / len(vals)})
    by_market.sort(key=lambda x: x["net_R"], reverse=True)
    positive_markets = sum(1 for row in by_market if row["net_R"] > 0)
    last60 = net[-60:]
    risk_rows = []
    for risk in [0.001, 0.0025, 0.005, 0.01]:
        risk_rows.append({
            "risk_per_trade": f"{risk:.2%}",
            "estimated_return_pct": f"{cumulative * risk:.2%}",
            "current_drawdown_pct": f"{current_dd * risk:.2%}",
            "historical_max_dd_pct_estimate": f"{HISTORICAL_MAX_DD_R * risk:.2%}",
        })
    open_positions = [m for m, s in state["markets"].items() if s.get("position_status") == "OPEN"]
    warning_text = "\n".join(f"- WARNING: {w}" for w in warnings) if warnings else "- No WARNING."
    last20 = [{k: t.get(k, "") for k in ["trade_id", "market", "entry_time", "exit_time", "exit_reason", "net_R", "mfe_R", "mae_R"]} for t in trades[-20:]]
    for row in last20:
        for key in ["net_R", "mfe_R", "mae_R"]:
            value = finite_float(row.get(key))
            row[key] = "" if value is None else round(value, 4)
    report = f"""# Paper Trading Daily Report

date: {report_date.date()}

strategy: Swing Bullish BOS + strong ADX

status: Paper Trading Candidate. Not verified live alpha. Not a production heavy-capital strategy.

## Summary

- open_positions: {len(open_positions)} ({', '.join(open_positions) if open_positions else 'none'})
- new_signals: {len(daily_signals)}
- new_entries: {len(daily_entries)}
- closed_trades: {len(daily_closed)}
- daily_net_R: {sum(float(t['net_R']) for t in daily_closed) if daily_closed else 0.0:.4f}
- cumulative_net_R: {cumulative:.4f}
- trades: {len(trades)}
- avg_R: {avg if avg is not None else 'NA'}
- win_rate: {win_rate if win_rate is not None else 'NA'}
- profit_factor: {pf if pf is not None else 'NA'}
- max_drawdown_R: {max_dd:.4f}
- current_drawdown_R: {current_dd:.4f}
- positive_markets: {positive_markets}
- last_60_trades_avg_R: {(sum(last60) / len(last60)) if last60 else 'NA'}
- last_60_trades_profit_factor: {profit_factor(last60) if last60 else 'NA'}
- mismatch_rate: {state.get('consistency', {}).get('mismatch_rate', 0.0):.4%}

## Warning Monitor

{warning_text}

If WARNING is triggered, pause new live-position recommendations and continue paper signal logging.

## Market Breakdown

{markdown_table(by_market, ['market', 'trades', 'net_R', 'avg_R'])}

## Last 20 Trades

{markdown_table(last20, ['trade_id', 'market', 'entry_time', 'exit_time', 'exit_reason', 'net_R', 'mfe_R', 'mae_R'])}

## Risk Mapping

{markdown_table(risk_rows, ['risk_per_trade', 'estimated_return_pct', 'current_drawdown_pct', 'historical_max_dd_pct_estimate'])}

Default recommendation: paper trading or small observation at 0.1% - 0.25% risk per trade. 0.5% is not recommended. 1.0% is forbidden.

## Notes

- Signals are processed only after closed 15M candles.
- Swing pivots use confirmed pivots.
- Fixed rules are unchanged: ADX >= 30, SL = 3 ATR, TP = 3R, entry = close[t].
- Passing trade-rule validation is not the same as passing walk-forward.
- Passing walk-forward is not the same as safe heavy live trading.
- Effective paper trading is not the same as live alpha.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main():
    ensure_files()
    state = load_state()
    all_new_signals = []
    all_new_entries = []
    all_closed = []
    strategies = {}
    latest_processed = None
    for market in MARKETS:
        try:
            bars = fetch_bars(market)
            strategy = compute_strategy(bars)
            strategies[market] = strategy
            new_signals, new_entries, closed_ids, latest = process_market(state, market, strategy)
            all_new_signals.extend(new_signals)
            all_new_entries.extend(new_entries)
            all_closed.extend(closed_ids)
            if latest:
                latest_processed = max(latest_processed, latest) if latest_processed else latest
        except Exception as exc:
            state.setdefault("fetch_errors", {})[market] = str(exc)
            print(f"fetch/process error for {market}: {exc}")
    consistency = consistency_check(strategies)
    state["consistency"] = consistency
    report_date = latest_processed or datetime.utcnow()
    warnings = evaluate_warnings(closed_trades(), report_date, float(consistency.get("mismatch_rate", 0.0)))
    state["warnings"] = warnings
    state["last_run_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state["last_data_time"] = ts_text(latest_processed) if latest_processed else state.get("last_data_time")
    save_state(state)
    build_report(state, report_date, warnings)
    cumulative = sum(float(t["net_R"]) for t in closed_trades())
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
