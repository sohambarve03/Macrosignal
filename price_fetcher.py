# ══════════════════════════════════════════════════════════════
# data_pipeline/price_fetcher.py
#
# 📖 WHAT THIS FILE DOES:
#   Downloads historical price data for our 8 ETFs using yfinance.
#   yfinance = Yahoo Finance wrapper — completely free.
#   Calculates weekly returns so we can train our ML model.
#
# 📖 KEY CONCEPT — WHY WEEKLY RETURNS?
#   We don't care about exact prices (e.g. XLE = $89.50).
#   We care about direction and magnitude (XLE went UP 5% this week).
#   Geopolitical events take ~1 week to fully price in.
# ══════════════════════════════════════════════════════════════

import yfinance as yf
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ETFS, DATA_PROCESSED, YEARS_OF_HISTORY


def download_etf_prices(tickers=None, years=None):
    """
    Download historical weekly price data for all ETFs.

    Args:
        tickers (list): ETF symbols. Defaults to config.ETFS
        years   (int):  Years of history. Defaults to config.YEARS_OF_HISTORY

    Returns:
        pd.DataFrame: Weekly returns for each ETF
    """
    if tickers is None:
        tickers = ETFS
    if years is None:
        years = YEARS_OF_HISTORY

    from datetime import datetime, timedelta
    end_date   = datetime.today()
    start_date = end_date - timedelta(days=years * 365)

    print(f"📥 Downloading {len(tickers)} ETFs from {start_date.date()} to {end_date.date()}...")

    # Download all tickers at once (yfinance supports batch download)
    raw_data = yf.download(
        tickers   = tickers,
        start     = start_date,
        end       = end_date,
        interval  = "1wk",        # weekly data
        auto_adjust = True,       # adjusts for stock splits, dividends
        progress  = False
    )

    # Extract just the closing prices
    # raw_data has multi-level columns like ("Close", "XLE"), ("Close", "GLD")
    if len(tickers) > 1:
        prices = raw_data["Close"]
    else:
        prices = raw_data[["Close"]].rename(columns={"Close": tickers[0]})

    print(f"✅ Downloaded {len(prices)} weeks of data")
    print(f"   Date range: {prices.index[0].date()} → {prices.index[-1].date()}")
    print(f"   ETFs: {list(prices.columns)}\n")

    return prices


def calculate_weekly_returns(prices_df):
    """
    Convert prices to percentage returns.

    Instead of: XLE = [$89.50, $92.10, $88.30, ...]
    We get:     XLE = [NaN, +2.91%, -4.13%, ...]

    Why? Because relative change is what matters, not absolute price.
    """
    # pct_change() = (current - previous) / previous * 100
    returns = prices_df.pct_change() * 100
    returns = returns.dropna()    # remove first row (it's NaN — no previous price)
    returns = returns.round(4)
    return returns


def save_price_data(prices_df, returns_df):
    """Save price and returns data to CSV files."""
    os.makedirs(DATA_PROCESSED, exist_ok=True)

    prices_path  = os.path.join(DATA_PROCESSED, "etf_prices.csv")
    returns_path = os.path.join(DATA_PROCESSED, "etf_returns.csv")

    prices_df.to_csv(prices_path)
    returns_df.to_csv(returns_path)

    print(f"💾 Saved prices  → {prices_path}")
    print(f"💾 Saved returns → {returns_path}")


def load_returns():
    """Load the saved returns data."""
    path = os.path.join(DATA_PROCESSED, "etf_returns.csv")
    if not os.path.exists(path):
        print("⚠️  No returns data found. Run price_fetcher.py first.")
        return None
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df


def show_summary_stats(returns_df):
    """Print summary statistics — good to understand your data."""
    print("\n📊 ETF Weekly Returns Summary")
    print("=" * 50)
    print(f"{'ETF':<8} {'Avg Return':>12} {'Volatility':>12} {'Best Week':>12} {'Worst Week':>12}")
    print("-" * 50)

    for col in returns_df.columns:
        avg   = returns_df[col].mean()
        std   = returns_df[col].std()
        best  = returns_df[col].max()
        worst = returns_df[col].min()
        print(f"{col:<8} {avg:>+11.2f}% {std:>11.2f}% {best:>+11.2f}% {worst:>+11.2f}%")


# ── TEST / RUN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("💹 GeoFinance Price Fetcher\n")

    # Download prices
    prices = download_etf_prices()

    # Calculate returns
    returns = calculate_weekly_returns(prices)

    # Save to files
    save_price_data(prices, returns)

    # Show stats
    show_summary_stats(returns)

    print(f"\n✅ Price data ready! {len(returns)} weeks of returns for {len(returns.columns)} ETFs")
