# SEC Filings Fetcher

Type a stock ticker (NYSE or Nasdaq) and get the last 5 years of that company's SEC filings, pulled straight from **SEC EDGAR**, in one folder and one zip file.

## Quick start (Windows)

1. **Double-click `get_filings.bat`** in the `sec-filings` folder.
2. The first time only, it sets itself up and asks for your **name and email**. The SEC requires these, and they're saved in a `.sec_user_agent` file so you aren't asked again.
3. Type a **ticker**, such as `AAPL`, and press Enter.
4. When it finishes, the `filings` folder opens. Your files are in `filings\AAPL\`, plus `filings\AAPL.zip`.

That's it. To get another company, double-click it again.

You can also run it from PowerShell, from any folder:

```powershell
& "$HOME\Documents\sec-filings\get_filings.bat" MSFT
```

> **Need Python?** If it says Python wasn't found, install it from [python.org](https://www.python.org/downloads/). Tick **"Add python.exe to PATH"** during install, then try again.

## What you get

| Folder | Contents |
|---|---|
| `10-K/` | Annual reports (10-K, plus the ARS shareholder report if filed) |
| `10-Q/` | Quarterly reports |
| `earnings_releases/` | Quarterly earnings press releases (8-K, Item 2.02) |
| `transcripts/` | Earnings call transcripts *(optional, see below)* |

## Troubleshooting

| Problem | Fix |
|---|---|
| `'.venv/Scripts/python' is not recognized` | You're in the wrong folder. Use `get_filings.bat` instead, or `cd $HOME\Documents\sec-filings` first. |
| `Ticker 'XYZ' not found` | Check the spelling. Only US-listed companies that file with the SEC work. |
| Want to change the saved name and email | Delete the `.sec_user_agent` file. You'll be asked again next time. |
| `CERTIFICATE_VERIFY_FAILED` | Run `.venv\Scripts\python -m pip install -r requirements.txt` from the `sec-filings` folder. |

## Mac, Linux, or Google Cloud Shell

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/mccarthym27/sec-filings&show=terminal)

```bash
pip install -r requirements.txt
export SEC_USER_AGENT="Your Name your@email.com"
python3 get_filings.py AAPL
```

In Cloud Shell, your browser downloads the zip automatically when it finishes.

## Earnings call transcripts (optional)

Companies don't file transcripts with the SEC, so EDGAR doesn't have them. To include them, get a [Financial Modeling Prep](https://financialmodelingprep.com) API key (transcripts need a paid plan) and set it before running:

```powershell
$env:FMP_API_KEY = "your_key_here"      # Windows PowerShell
```
```bash
export FMP_API_KEY=your_key_here        # Mac / Linux
```

## Notes

- All filings come from SEC EDGAR (sec.gov). The script stays under the SEC's limit of 10 requests per second.
- Foreign companies that file 20-F or 40-F annual reports instead of 10-Ks get those in the `10-K/` folder.
- Running the same ticker again only downloads new filings. Files you already have are skipped.
