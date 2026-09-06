# Paper Trading Daily Report

date: 2026-09-06

strategy: Swing Bullish BOS + strong ADX

status: Paper Trading Candidate. Not verified live alpha. Not a production heavy-capital strategy.

## Summary

- open_positions: 1 (AVAX)
- new_signals: 0
- new_entries: 0
- closed_trades: 0
- daily_net_R: 0.0000
- cumulative_net_R: -7.3743
- trades: 30
- avg_R: -0.24581156935667872
- win_rate: 0.26666666666666666
- profit_factor: 0.6995455675333445
- max_drawdown_R: 18.2582
- current_drawdown_R: 8.0226
- positive_markets: 4
- last_60_trades_avg_R: -0.24581156935667872
- last_60_trades_profit_factor: 0.6995455675333445
- mismatch_rate: 0.0000%

## Warning Monitor

- WARNING: Consecutive losses reached 12 or more
- WARNING: Recent 3 calendar months cumulative net_R below 0

If WARNING is triggered, pause new live-position recommendations and continue paper signal logging.

## Market Breakdown

| market | trades | net_R | avg_R |
| --- | --- | --- | --- |
| XRP | 1 | 2.9444 | 2.9444 |
| LINK | 3 | 1.2771 | 0.4257 |
| SOL | 2 | 1.1712 | 0.5856 |
| ADA | 5 | 0.3024 | 0.0605 |
| LTC | 5 | -0.3356 | -0.0671 |
| AVAX | 1 | -1.1345 | -1.1345 |
| DOGE | 3 | -3.3489 | -1.1163 |
| ETH | 3 | -3.4949 | -1.1650 |
| BTC | 7 | -4.7555 | -0.6794 |

## Last 20 Trades

| trade_id | market | entry_time | exit_time | exit_reason | net_R | mfe_R | mae_R |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PT-000011-DOGE | DOGE | 2026-07-21 08:00:00 | 2026-07-21 17:45:00 | SL | -1.1680 | 0.1861 | 1.1020 |
| PT-000012-LTC | LTC | 2026-07-21 08:30:00 | 2026-07-21 10:45:00 | SL | -1.1814 | 0.1431 | 1.0256 |
| PT-000013-ADA | ADA | 2026-07-22 15:45:00 | 2026-07-22 19:00:00 | SL | -1.0862 | 0.8863 | 1.2530 |
| PT-000014-ADA | ADA | 2026-07-30 14:30:00 | 2026-07-31 06:30:00 | TIME | -0.5683 | 1.7613 | 0.7592 |
| PT-000015-BTC | BTC | 2026-08-02 21:30:00 | 2026-08-02 22:30:00 | SL | -1.3687 | 0.3347 | 1.1866 |
| PT-000016-ADA | ADA | 2026-08-03 13:45:00 | 2026-08-03 14:30:00 | SL | -1.0634 | 0.2682 | 1.0730 |
| PT-000017-BTC | BTC | 2026-08-03 14:45:00 | 2026-08-04 06:45:00 | TIME | -0.5691 | 0.3943 | 0.9196 |
| PT-000018-BTC | BTC | 2026-08-07 11:15:00 | 2026-08-07 17:00:00 | SL | -1.3172 | 0.9350 | 1.1752 |
| PT-000019-BTC | BTC | 2026-08-09 13:30:00 | 2026-08-09 20:00:00 | SL | -1.7644 | 0.5882 | 1.2726 |
| PT-000020-BTC | BTC | 2026-08-19 14:00:00 | 2026-08-19 15:00:00 | TP | 2.7657 | 3.0850 | 0.1889 |
| PT-000021-ETH | ETH | 2026-08-07 12:00:00 | 2026-08-07 14:00:00 | SL | -1.2111 | 0.6280 | 1.5793 |
| PT-000022-SOL | SOL | 2026-08-09 14:45:00 | 2026-08-09 23:15:00 | SL | -1.2353 | 1.5711 | 1.2646 |
| PT-000023-SOL | SOL | 2026-08-27 08:15:00 | 2026-08-28 00:15:00 | TIME | 2.4065 | 2.8451 | 0.4734 |
| PT-000024-XRP | XRP | 2026-08-21 08:00:00 | 2026-08-21 23:15:00 | TP | 2.9444 | 3.2045 | 0.2098 |
| PT-000025-ADA | ADA | 2026-08-06 14:30:00 | 2026-08-07 06:30:00 | TIME | 0.0904 | 1.8415 | 0.6265 |
| PT-000026-LINK | LINK | 2026-08-08 10:15:00 | 2026-08-09 02:15:00 | TIME | -0.5057 | 1.4074 | 0.5370 |
| PT-000027-LINK | LINK | 2026-08-21 02:15:00 | 2026-08-21 07:15:00 | TP | 2.9223 | 3.0574 | 0.3062 |
| PT-000028-LTC | LTC | 2026-08-08 20:45:00 | 2026-08-09 12:45:00 | TIME | 0.2148 | 1.3493 | 0.9305 |
| PT-000029-LTC | LTC | 2026-09-05 02:45:00 | 2026-09-05 17:00:00 | TP | 2.8955 | 3.2019 | 0.0733 |
| PT-000031-DOGE | DOGE | 2026-09-05 17:45:00 | 2026-09-05 19:00:00 | SL | -1.0520 | 0.1857 | 1.0303 |

## Risk Mapping

| risk_per_trade | estimated_return_pct | current_drawdown_pct | historical_max_dd_pct_estimate |
| --- | --- | --- | --- |
| 0.10% | -0.74% | 0.80% | 3.99% |
| 0.25% | -1.84% | 2.01% | 9.97% |
| 0.50% | -3.69% | 4.01% | 19.94% |
| 1.00% | -7.37% | 8.02% | 39.88% |

Default recommendation: paper trading or small observation at 0.1% - 0.25% risk per trade. 0.5% is not recommended. 1.0% is forbidden.

## Notes

- Signals are processed only after closed 15M candles.
- Swing pivots use confirmed pivots.
- Fixed rules are unchanged: ADX >= 30, SL = 3 ATR, TP = 3R, entry = close[t].
- Passing trade-rule validation is not the same as passing walk-forward.
- Passing walk-forward is not the same as safe heavy live trading.
- Effective paper trading is not the same as live alpha.
