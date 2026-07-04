# Paper Trading Daily Report

date: 2026-07-04

strategy: Swing Bullish BOS + strong ADX

status: Paper Trading Candidate. Not verified live alpha. Not a production heavy-capital strategy.

## Summary

- open_positions: 0 (none)
- new_signals: 0
- new_entries: 0
- closed_trades: 0
- daily_net_R: 0.0000
- cumulative_net_R: 0.0000
- trades: 0
- avg_R: NA
- win_rate: NA
- profit_factor: NA
- max_drawdown_R: 0.0000
- current_drawdown_R: 0.0000
- positive_markets: 0
- last_60_trades_avg_R: NA
- last_60_trades_profit_factor: NA
- mismatch_rate: 0.0000%

## Warning Monitor

- No WARNING.

If WARNING is triggered, pause new live-position recommendations and continue paper signal logging.

## Market Breakdown

_No rows._

## Last 20 Trades

_No rows._

## Risk Mapping

| risk_per_trade | estimated_return_pct | current_drawdown_pct | historical_max_dd_pct_estimate |
| --- | --- | --- | --- |
| 0.10% | 0.00% | 0.00% | 3.99% |
| 0.25% | 0.00% | 0.00% | 9.97% |
| 0.50% | 0.00% | 0.00% | 19.94% |
| 1.00% | 0.00% | 0.00% | 39.88% |

Default recommendation: paper trading or small observation at 0.1% - 0.25% risk per trade. 0.5% is not recommended. 1.0% is forbidden.

## Notes

- Signals are processed only after closed 15M candles.
- Swing pivots use confirmed pivots.
- Fixed rules are unchanged: ADX >= 30, SL = 3 ATR, TP = 3R, entry = close[t].
- Passing trade-rule validation is not the same as passing walk-forward.
- Passing walk-forward is not the same as safe heavy live trading.
- Effective paper trading is not the same as live alpha.
