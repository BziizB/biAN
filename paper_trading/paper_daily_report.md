# Paper Trading Daily Report

date: 2026-07-04

strategy: Swing Bullish BOS + strong ADX

status: Paper Trading Candidate. Not verified live alpha. Not a production heavy-capital strategy.

## Summary

- open_positions: 3 (BTC, ETH, LINK)
- new_signals: 7
- new_entries: 7
- closed_trades: 4
- daily_net_R: -0.4728
- cumulative_net_R: -0.4728
- trades: 4
- avg_R: -0.11819459862721782
- win_rate: 0.25
- profit_factor: 0.8610585053085177
- max_drawdown_R: 2.2739
- current_drawdown_R: 2.2739
- positive_markets: 1
- last_60_trades_avg_R: -0.11819459862721782
- last_60_trades_profit_factor: 0.8610585053085177
- mismatch_rate: 0.0000%

## Warning Monitor

- WARNING: Recent 3 calendar months cumulative net_R below 0

If WARNING is triggered, pause new live-position recommendations and continue paper signal logging.

## Market Breakdown

| market | trades | net_R | avg_R |
| --- | --- | --- | --- |
| ADA | 1 | 2.9299 | 2.9299 |
| DOGE | 1 | -1.1289 | -1.1289 |
| AVAX | 1 | -1.1345 | -1.1345 |
| LTC | 1 | -1.1393 | -1.1393 |

## Last 20 Trades

| trade_id | market | entry_time | exit_time | exit_reason | net_R | mfe_R | mae_R |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PT-000002-DOGE | DOGE | 2026-07-04 15:30:00 | 2026-07-04 23:00:00 | SL | -1.1289 | 0.6898 | 1.2252 |
| PT-000003-ADA | ADA | 2026-07-04 14:45:00 | 2026-07-04 16:15:00 | TP | 2.9299 | 3.1207 | 0.0000 |
| PT-000005-LTC | LTC | 2026-07-04 16:45:00 | 2026-07-04 23:00:00 | SL | -1.1393 | 0.6563 | 1.1967 |
| PT-000007-AVAX | AVAX | 2026-07-04 17:30:00 | 2026-07-04 23:00:00 | SL | -1.1345 | 0.8526 | 1.1288 |

## Risk Mapping

| risk_per_trade | estimated_return_pct | current_drawdown_pct | historical_max_dd_pct_estimate |
| --- | --- | --- | --- |
| 0.10% | -0.05% | 0.23% | 3.99% |
| 0.25% | -0.12% | 0.57% | 9.97% |
| 0.50% | -0.24% | 1.14% | 19.94% |
| 1.00% | -0.47% | 2.27% | 39.88% |

Default recommendation: paper trading or small observation at 0.1% - 0.25% risk per trade. 0.5% is not recommended. 1.0% is forbidden.

## Notes

- Signals are processed only after closed 15M candles.
- Swing pivots use confirmed pivots.
- Fixed rules are unchanged: ADX >= 30, SL = 3 ATR, TP = 3R, entry = close[t].
- Passing trade-rule validation is not the same as passing walk-forward.
- Passing walk-forward is not the same as safe heavy live trading.
- Effective paper trading is not the same as live alpha.
