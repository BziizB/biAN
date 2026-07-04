# Paper Trading Daily Report

date: 2026-07-04

strategy: Swing Bullish BOS + strong ADX

status: Paper Trading Candidate. Not verified live alpha. Not a production heavy-capital strategy.

## Summary

- open_positions: 6 (BTC, ETH, DOGE, LINK, AVAX, LTC)
- new_signals: 7
- new_entries: 7
- closed_trades: 1
- daily_net_R: 2.9299
- cumulative_net_R: 2.9299
- trades: 1
- avg_R: 2.929937227333756
- win_rate: 1.0
- profit_factor: NA
- max_drawdown_R: 0.0000
- current_drawdown_R: 0.0000
- positive_markets: 1
- last_60_trades_avg_R: 2.929937227333756
- last_60_trades_profit_factor: None
- mismatch_rate: 0.0000%

## Warning Monitor

- No WARNING.

If WARNING is triggered, pause new live-position recommendations and continue paper signal logging.

## Market Breakdown

| market | trades | net_R | avg_R |
| --- | --- | --- | --- |
| ADA | 1 | 2.9299 | 2.9299 |

## Last 20 Trades

| trade_id | market | entry_time | exit_time | exit_reason | net_R | mfe_R | mae_R |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PT-000003-ADA | ADA | 2026-07-04 14:45:00 | 2026-07-04 16:15:00 | TP | 2.9299 | 3.1207 | 0.0000 |

## Risk Mapping

| risk_per_trade | estimated_return_pct | current_drawdown_pct | historical_max_dd_pct_estimate |
| --- | --- | --- | --- |
| 0.10% | 0.29% | 0.00% | 3.99% |
| 0.25% | 0.73% | 0.00% | 9.97% |
| 0.50% | 1.46% | 0.00% | 19.94% |
| 1.00% | 2.93% | 0.00% | 39.88% |

Default recommendation: paper trading or small observation at 0.1% - 0.25% risk per trade. 0.5% is not recommended. 1.0% is forbidden.

## Notes

- Signals are processed only after closed 15M candles.
- Swing pivots use confirmed pivots.
- Fixed rules are unchanged: ADX >= 30, SL = 3 ATR, TP = 3R, entry = close[t].
- Passing trade-rule validation is not the same as passing walk-forward.
- Passing walk-forward is not the same as safe heavy live trading.
- Effective paper trading is not the same as live alpha.
