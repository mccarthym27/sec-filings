@echo off
setlocal
rem Double-click this file, or run:  get_filings.bat AAPL
rem Works from any folder. Sets itself up the first time it runs.

cd /d "%~dp0"

rem 1. First run only: create the Python environment and install packages.
if not exist ".venv\Scripts\python.exe" (
    echo Setting up for the first time...
    python -m venv .venv || goto :nopython
    ".venv\Scripts\python" -m pip install -q -r requirements.txt || goto :fail
)

rem 2. The SEC requires your name and email. Asked once, then remembered.
if not defined SEC_USER_AGENT (
    if exist ".sec_user_agent" (
        set /p SEC_USER_AGENT=<".sec_user_agent"
    ) else (
        set /p SEC_USER_AGENT=Your name and email for the SEC, e.g. Jane Doe jane@email.com:
    )
)
if not exist ".sec_user_agent" (
    >".sec_user_agent" echo %SEC_USER_AGENT%
)

rem 3. Ticker from the command line, or ask for it.
set "TICKER=%~1"
if "%TICKER%"=="" set /p TICKER=Ticker (e.g. AAPL):

".venv\Scripts\python" get_filings.py %TICKER% || goto :fail
echo.
echo Your files are in: %~dp0filings\%TICKER%
start "" "%~dp0filings"
goto :end

:nopython
echo.
echo Python was not found. Install it from https://www.python.org/downloads/
echo (tick "Add python.exe to PATH" during install), then try again.
goto :end

:fail
echo.
echo Something went wrong - see the message above.

:end
if "%~1"=="" pause
