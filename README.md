# SEC Filings Fetcher

Type a stock ticker (NYSE or Nasdaq) and get the last 5 years of that company's SEC filings, pulled straight from **SEC EDGAR**, in one folder and one zip file.

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com//sec-filings&show=terminal)

## What you get

| Folder | Contents |
|---|---|
| `10-K/` | Annual reports (10-K, plus the ARS shareholder report if filed) |
| `10-Q/` | Quarterly reports |
| `earnings_releases/` | Quarterly earnings press releases (8-K, Item 2.02) |
| `transcripts/` | Earnings call transcripts *(optional, see below)* |

## How to use it (Google Cloud Shell, free)

1. Click **Open in Cloud Shell** above and sign in with any Google account.
2. In the terminal, tell the SEC who you are (they require a name and email):
   ```bash
   export SEC_USER_AGENT="Your Name your@email.com"
   ```
3. Run it with a ticker:
   ```bash
   python3 get_filings.py AAPL
   ```
4. When it finishes, your browser downloads `AAPL.zip`. The unzipped files are also in `filings/AAPL/`.

## Running it on your own computer

```bash
pip install -r requirements.txt
export SEC_USER_AGENT="Your Name your@email.com"
python3 get_filings.py AAPL
```

## Earnings call transcripts (optional)

Companies don't file transcripts with the SEC, so EDGAR doesn't have them. To include them, get a [Financial Modeling Prep](https://financialmodelingprep.com) API key (transcripts need a paid plan) and run this before the script:

```bash
export FMP_API_KEY=your_key_here
```

## Notes

- All filings come from SEC EDGAR (sec.gov). The script stays under the SEC's limit of 10 requests per second.
- Foreign companies that file 20-F or 40-F annual reports instead of 10-Ks get those in the `10-K/` folder.
