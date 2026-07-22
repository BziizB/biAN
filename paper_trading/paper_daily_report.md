# Paper Trading Daily Report

date: 2026-07-22

strategy: Swing Bullish BOS + strong ADX

status: Paper Trading Candidate. Not verified live alpha. Not a production heavy-capital strategy.

## Summary

- open_positions: 0 (none)
- new_signals: 0
- new_entries: 0
- closed_trades: 0
- daily_net_R: 0.0000
- cumulative_net_R: -9.8725
- trades: 12
- avg_R: -0.8227100308881791
- win_rate: 0.08333333333333333
- profit_factor: 0.22885740529953588
- max_drawdown_R: 10.5208
- current_drawdown_R: 10.5208
- positive_markets: 1
- last_60_trades_avg_R: -0.8227100308881791
- last_60_trades_profit_factor: 0.22885740529953588
- mismatch_rate: 0.0000%

## Warning Monitor

- WARNING: Recent 3 calendar months cumulative net_R below 0
- WARNING: No closed Binance 15M data processed; paper state is stale

If WARNING is triggered, pause new live-position recommendations and continue paper signal logging.

## Market Breakdown

| market | trades | net_R | avg_R |
| --- | --- | --- | --- |
| ADA | 1 | 2.9299 | 2.9299 |
| AVAX | 1 | -1.1345 | -1.1345 |
| LINK | 1 | -1.1395 | -1.1395 |
| ETH | 2 | -2.2838 | -1.1419 |
| DOGE | 2 | -2.2969 | -1.1484 |
| BTC | 2 | -2.5017 | -1.2509 |
| LTC | 3 | -3.4460 | -1.1487 |

## Last 20 Trades

| trade_id | market | entry_time | exit_time | exit_reason | net_R | mfe_R | mae_R |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PT-000001-ETH | ETH | 2026-07-04 15:00:00 | 2026-07-05 01:15:00 | SL | -1.1528 | 1.2159 | 1.1342 |
| PT-000002-DOGE | DOGE | 2026-07-04 15:30:00 | 2026-07-04 23:00:00 | SL | -1.1289 | 0.6898 | 1.2252 |
| PT-000003-ADA | ADA | 2026-07-04 14:45:00 | 2026-07-04 16:15:00 | TP | 2.9299 | 3.1207 | 0.0000 |
| PT-000004-LINK | LINK | 2026-07-04 15:00:00 | 2026-07-05 00:30:00 | SL | -1.1395 | 1.3840 | 1.0679 |
| PT-000005-LTC | LTC | 2026-07-04 16:45:00 | 2026-07-04 23:00:00 | SL | -1.1393 | 0.6563 | 1.1967 |
| PT-000006-BTC | BTC | 2026-07-04 17:30:00 | 2026-07-05 01:30:00 | SL | -1.2710 | 0.7692 | 1.0112 |
| PT-000007-AVAX | AVAX | 2026-07-04 17:30:00 | 2026-07-04 23:00:00 | SL | -1.1345 | 0.8526 | 1.1288 |
| PT-000008-LTC | LTC | 2026-07-05 16:00:00 | 2026-07-05 16:15:00 | SL | -1.1253 | 0.0689 | 1.1538 |
| PT-000009-BTC | BTC | 2026-07-10 08:15:00 | 2026-07-10 14:30:00 | SL | -1.2307 | 0.8115 | 1.2111 |
| PT-000010-ETH | ETH | 2026-07-13 00:00:00 | 2026-07-13 00:30:00 | SL | -1.1310 | 0.1742 | 1.4768 |
| PT-000011-DOGE | DOGE | 2026-07-21 08:00:00 | 2026-07-21 17:45:00 | SL | -1.1680 | 0.1861 | 1.1020 |
| PT-000012-LTC | LTC | 2026-07-21 08:30:00 | 2026-07-21 10:45:00 | SL | -1.1814 | 0.1431 | 1.0256 |

## Risk Mapping

| risk_per_trade | estimated_return_pct | current_drawdown_pct | historical_max_dd_pct_estimate |
| --- | --- | --- | --- |
| 0.10% | -0.99% | 1.05% | 3.99% |
| 0.25% | -2.47% | 2.63% | 9.97% |
| 0.50% | -4.94% | 5.26% | 19.94% |
| 1.00% | -9.87% | 10.52% | 39.88% |

Default recommendation: paper trading or small observation at 0.1% - 0.25% risk per trade. 0.5% is not recommended. 1.0% is forbidden.

## Notes

- Signals are processed only after closed 15M candles.
- Swing pivots use confirmed pivots.
- Fixed rules are unchanged: ADX >= 30, SL = 3 ATR, TP = 3R, entry = close[t].
- Passing trade-rule validation is not the same as passing walk-forward.
- Passing walk-forward is not the same as safe heavy live trading.
- Effective paper trading is not the same as live alpha.
