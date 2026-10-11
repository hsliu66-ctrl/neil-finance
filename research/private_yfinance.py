#!/usr/bin/env python3
"""Personal-use Yahoo Finance research. Does not commit or publish downloaded prices."""
import argparse
import sys

def main():
    p=argparse.ArgumentParser(description="Private personal research only; do not redistribute Yahoo quotes.")
    p.add_argument("symbol",nargs="?",default="VT",help="Ticker, e.g. VT GLD XLV VOO")
    p.add_argument("--period",choices=["5d","1mo","3mo","6mo","1y","2y"],default="1mo")
    args=p.parse_args()
    if len(args.symbol)>16 or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.^-= " for c in args.symbol):
        p.error("Invalid symbol")
    import yfinance as yf
    ticker=yf.Ticker(args.symbol.strip())
    frame=ticker.history(period=args.period,auto_adjust=True)
    if frame is None or frame.empty:
        sys.exit("No accessible data; do not treat this as a price of zero.")
    print("Research only / Yahoo Finance personal-use terms apply. No file is uploaded.")
    print(frame[["Open","High","Low","Close","Volume"]].tail(12).round(3).to_string())
if __name__=="__main__":
    main()
