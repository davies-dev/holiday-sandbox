@echo off
REM Script to run the Hand History Explorer with virtual environment

REM Change to the project directory
cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
python scripts\hh_explorer.py

REM Keep the window open if there's an error
pause 