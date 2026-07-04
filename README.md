# biAN Paper Trading Monitor

This repository runs a fixed paper trading observation workflow for:

- Strategy: Swing Bullish BOS + strong ADX
- Direction: LONG only
- Markets: BTC, ETH, SOL, XRP, DOGE, ADA, LINK, AVAX, LTC
- Timeframe: Binance USDT 15M
- Status: paper trading observation only

Important: this is not a verified live alpha and is not a production strategy for heavy capital.

## Current Cloud Setup

GitHub Actions workflow:

- `.github/workflows/paper-trading-pages.yml`
- Runs on `workflow_dispatch`
- Scheduled every 15 minutes with cron `*/15 * * * *`
- Fetches closed Binance 15M candles through `paper_update_cloud.py`
- Updates `paper_trading/` files
- Builds a static dashboard from `monitor_frontend/`
- Deploys the dashboard with GitHub Pages Actions

Current expected dashboard URL:

```text
https://bziizb.github.io/biAN/
```

If the URL returns 404, open repository settings and set:

```text
Settings -> Pages -> Build and deployment -> Source -> GitHub Actions
```

Then open:

```text
Actions -> Paper Trading Pages -> Run workflow
```

Because this repository is private, GitHub Pages availability may depend on the GitHub account plan or private Pages settings. If the URL remains 404 after a successful workflow run, make the repository public or enable private GitHub Pages if your plan supports it.

## Output Files

The workflow writes:

```text
paper_trading/state.json
paper_trading/paper_trades.csv
paper_trading/paper_signals.csv
paper_trading/paper_daily_report.md
paper_trading/mismatch_report.csv
```

## Risk Note

Current strategy is in paper trading observation stage. Passing trade-rule validation is not the same as passing walk-forward. Passing walk-forward is not the same as safe heavy live trading. Effective paper trading is not the same as live alpha.
