@echo off
title NagarMithra — Mangalagiri Civic Platform
echo ========================================================
echo   NagarMithra — Mangalagiri Civic Issue Reporting Platform
echo   Starting Server and Opening Browser on Port 5000...
echo   URL: http://localhost:5000
echo ========================================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
start "" http://localhost:5000
python server.py
pause
