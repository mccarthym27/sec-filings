#!/usr/bin/env python3
"""
get_filings.py  -  type a ticker, get 5 years of SEC filings in a folder + zip.

Usage:
    python3 get_filings.py AAPL
    python3 get_filings.py            (it will ask you for the ticker)

What you get (in ./filings/<TICKER>/ and ./filings/<TICKER>.zip):
    10-K/                 annual reports (10-K, plus ARS glossy annual report if filed)
    10-Q/                 quarterly reports
    earnings_releases/    8-K earnings press releases (Item 2.02, exhibit 99.x)
    transcripts/          earnings call transcripts  (only if FMP_API_KEY is set - see below)

Earnings call transcripts are NOT filed with the SEC, so they are not free.
To include them, get a Financial Modeling Prep key (paid plan) and run:
    export FMP_API_KEY=your_key_here
"""
import json, os, re, sys, time, shutil, subprocess
from datetime import date
import requests

# SEC requires a User-Agent with your name + email. Put yours here.
USER_AGENT = os.environ.get("SEC_USER_AGENT", "Your Name your.email@example.com")
YEARS = 5
OUT_ROOT = "filings"

S = requests.Session()
S.headers.update({"User-Agent": USER_AGENT, "Accept-Encoding": "gzip, deflate"})


def get(url, **kw):
    for attempt in range(4):
        time.sleep(0.15)  # SEC limit is 10 requests/sec
        r = S.get(url, timeout=60, **kw)
        if r.status_code == 200:
            return r
        if r.status_code in (429, 503):
            time.sleep(2 * (attempt + 1))
            continue
        r.raise_for_status()
    r.raise_for_status()


def ticker_to_cik(ticker):
    data = get("https://www.sec.gov/files/company_tickers.json").json()
    for row in data.values():
        if row["ticker"].upper() == ticker.upper():
            return int(row["cik_str"]), row["title"]
    sys.exit(f"Ticker '{ticker}' not found on SEC EDGAR.")


def all_filings(cik):
    sub = get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json").json()
    tables = [sub["filings"]["recent"]]
    for f in sub["filings"].get("files", []):  # older filings live in extra pages
        tables.append(get(f"https://data.sec.gov/submissions/{f['name']}").json())
    rows = []
    for t in tables:
        for i in range(len(t["accessionNumber"])):
            rows.append({k: t[k][i] for k in
                         ("accessionNumber", "filingDate", "reportDate", "form",
                          "primaryDocument", "items")})
    return rows


def safe(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


def save(url, path):
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(get(url).content)
    print("  saved", path)


def main():
    ticker = (sys.argv[1] if len(sys.argv) > 1 else input("Ticker: ")).strip().upper()
    cik, name = ticker_to_cik(ticker)
    print(f"{ticker} -> {name} (CIK {cik})")

    today = date.today()
    cutoff = today.replace(year=today.year - YEARS).isoformat()
    out = os.path.join(OUT_ROOT, ticker)
    folders = {"10-K": "10-K", "10-K/A": "10-K", "ARS": "10-K",
               "10-Q": "10-Q", "10-Q/A": "10-Q",
               "20-F": "10-K", "40-F": "10-K"}  # foreign filers' annual reports

    for f in all_filings(cik):
        if f["filingDate"] < cutoff:
            continue
        form, acc = f["form"], f["accessionNumber"]
        base = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}"
        period = f["reportDate"] or f["filingDate"]

        if form in folders and f["primaryDocument"]:
            doc = f["primaryDocument"]
            fname = f"{ticker}_{safe(form)}_{period}{os.path.splitext(doc)[1] or '.htm'}"
            save(f"{base}/{doc}", os.path.join(out, folders[form], fname))

        elif form == "8-K" and "2.02" in (f["items"] or ""):
            # Earnings release: grab exhibit 99.x from the filing
            idx = get(f"{base}/index.json").json()["directory"]["item"]
            for item in idx:
                n = item["name"]
                if re.search(r"(ex|exhibit)[-_]?99", n, re.I) and n.lower().endswith((".htm", ".html", ".txt", ".pdf")):
                    save(f"{base}/{n}", os.path.join(out, "earnings_releases",
                                                     f"{ticker}_{f['filingDate']}_{safe(n)}"))

    fetch_transcripts(ticker, out, today.year)

    zip_path = shutil.make_archive(out, "zip", out)
    print(f"\nDone. Folder: {out}/   Zip: {zip_path}")
    # In Google Cloud Shell this pops a download in your browser
    if shutil.which("cloudshell"):
        subprocess.run(["cloudshell", "download", zip_path])


def fetch_transcripts(ticker, out, this_year):
    key = os.environ.get("FMP_API_KEY")
    if not key:
        print("\n(No FMP_API_KEY set - skipping earnings call transcripts.)")
        return
    print("\nFetching earnings call transcripts...")
    for year in range(this_year - YEARS, this_year + 1):
        for q in range(1, 5):
            r = S.get("https://financialmodelingprep.com/stable/earning-call-transcript",
                      params={"symbol": ticker, "year": year, "quarter": q, "apikey": key},
                      timeout=60)
            if r.status_code != 200:
                print(f"  {year} Q{q}: HTTP {r.status_code} {r.text[:120]}")
                continue
            data = r.json()
            if not data:
                continue
            t = data[0] if isinstance(data, list) else data
            path = os.path.join(out, "transcripts", f"{ticker}_{year}_Q{q}_transcript.txt")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(f"{ticker} {year} Q{q} earnings call - {t.get('date', '')}\n\n")
                fh.write(t.get("content", ""))
            print("  saved", path)


if __name__ == "__main__":
    main()
