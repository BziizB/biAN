# Paper Trading Daily Report

date: 2026-11-26

strategy: Swing Bullish BOS + strong ADX

status: Paper Trading Candidate. Not verified live alpha. Not a production heavy-capital strategy.

## Summary

- open_positions: 0 (none)
- new_signals: 0
- new_entries: 0
- closed_trades: 0
- daily_net_R: 0.0000
- cumulative_net_R: -10.1435
- trades: 46
- avg_R: -0.22051048316776747
- win_rate: 0.30434782608695654
- profit_factor: 0.7169827484388478
- max_drawdown_R: 18.2582
- current_drawdown_R: 10.7918
- positive_markets: 5
- last_60_trades_avg_R: -0.22051048316776747
- last_60_trades_profit_factor: 0.7169827484388478
- mismatch_rate: 0.0000%

## Warning Monitor

- WARNING: Consecutive losses reached 12 or more
- WARNING: Recent 3 calendar months cumulative net_R below 0

If WARNING is triggered, pause new live-position recommendations and continue paper signal logging.

## Market Breakdown

| market | trades | net_R | avg_R |
| --- | --- | --- | --- |
| XRP | 2 | 1.8312 | 0.9156 |
| AVAX | 4 | 1.6769 | 0.4192 |
| ADA | 5 | 0.3024 | 0.0605 |
| LINK | 4 | 0.1388 | 0.0347 |
| SOL | 3 | 0.0506 | 0.0169 |
| ETH | 5 | -2.8452 | -0.5690 |
| BTC | 11 | -3.2026 | -0.2911 |
| LTC | 8 | -3.6646 | -0.4581 |
| DOGE | 4 | -4.4310 | -1.1077 |

## Last 20 Trades

| trade_id | market | entry_time | exit_time | exit_reason | net_R | mfe_R | mae_R |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PT-000027-LINK | LINK | 2026-08-21 02:15:00 | 2026-08-21 07:15:00 | TP | 2.9223 | 3.0574 | 0.3062 |
| PT-000028-LTC | LTC | 2026-08-08 20:45:00 | 2026-08-09 12:45:00 | TIME | 0.2148 | 1.3493 | 0.9305 |
| PT-000029-LTC | LTC | 2026-09-05 02:45:00 | 2026-09-05 17:00:00 | TP | 2.8955 | 3.2019 | 0.0733 |
| PT-000030-AVAX | AVAX | 2026-09-05 17:00:00 | 2026-09-06 09:00:00 | TIME | 0.9734 | 2.3223 | 0.3254 |
| PT-000031-DOGE | DOGE | 2026-09-05 17:45:00 | 2026-09-05 19:00:00 | SL | -1.0520 | 0.1857 | 1.0303 |
| PT-000032-SOL | SOL | 2026-09-06 03:30:00 | 2026-09-06 07:00:00 | SL | -1.1206 | 0.2638 | 1.2619 |
| PT-000033-LTC | LTC | 2026-09-07 00:15:00 | 2026-09-07 01:00:00 | SL | -1.1040 | 0.3744 | 1.4743 |
| PT-000034-ETH | ETH | 2026-09-14 20:00:00 | 2026-09-14 23:00:00 | SL | -1.1204 | 1.4679 | 1.2008 |
| PT-000035-AVAX | AVAX | 2026-09-20 14:30:00 | 2026-09-21 06:30:00 | TIME | 0.3763 | 1.5868 | 0.1083 |
| PT-000036-ETH | ETH | 2026-09-21 00:00:00 | 2026-09-21 16:00:00 | TIME | 1.7702 | 2.2298 | 0.9039 |
| PT-000037-DOGE | DOGE | 2026-09-30 12:30:00 | 2026-09-30 14:15:00 | SL | -1.0821 | 0.4095 | 1.5318 |
| PT-000038-BTC | BTC | 2026-10-02 04:15:00 | 2026-10-02 05:30:00 | SL | -1.1736 | 0.1565 | 1.1240 |
| PT-000039-XRP | XRP | 2026-10-02 10:30:00 | 2026-10-02 14:30:00 | SL | -1.1133 | 0.4336 | 1.1301 |
| PT-000040-LTC | LTC | 2026-10-04 14:30:00 | 2026-10-04 21:15:00 | SL | -1.1325 | 1.0620 | 1.0620 |
| PT-000041-LINK | LINK | 2026-10-11 15:45:00 | 2026-10-11 21:15:00 | SL | -1.1382 | 0.8194 | 1.4373 |
| PT-000042-AVAX | AVAX | 2026-10-11 15:30:00 | 2026-10-12 07:30:00 | TIME | 1.4618 | 1.9522 | 0.0861 |
| PT-000043-BTC | BTC | 2026-10-19 00:30:00 | 2026-10-19 14:00:00 | SL | -1.2193 | 1.2253 | 1.1049 |
| PT-000044-LTC | LTC | 2026-10-20 14:00:00 | 2026-10-20 15:15:00 | SL | -1.0925 | 0.4429 | 1.0109 |
| PT-000045-BTC | BTC | 2026-10-21 09:00:00 | 2026-10-22 01:00:00 | TIME | 1.0570 | 2.3813 | 0.5075 |
| PT-000046-BTC | BTC | 2026-11-23 05:30:00 | 2026-11-23 14:15:00 | TP | 2.8888 | 3.1793 | 0.7132 |

## Risk Mapping

| risk_per_trade | estimated_return_pct | current_drawdown_pct | historical_max_dd_pct_estimate |
| --- | --- | --- | --- |
| 0.10% | -1.01% | 1.08% | 3.99% |
| 0.25% | -2.54% | 2.70% | 9.97% |
| 0.50% | -5.07% | 5.40% | 19.94% |
| 1.00% | -10.14% | 10.79% | 39.88% |

Default recommendation: paper trading or small observation at 0.1% - 0.25% risk per trade. 0.5% is not recommended. 1.0% is forbidden.

## Notes

- Signals are processed only after closed 15M candles.
- Swing pivots use confirmed pivots.
- Fixed rules are unchanged: ADX >= 30, SL = 3 ATR, TP = 3R, entry = close[t].
- Passing trade-rule validation is not the same as passing walk-forward.
- Passing walk-forward is not the same as safe heavy live trading.
- Effective paper trading is not the same as live alpha.
