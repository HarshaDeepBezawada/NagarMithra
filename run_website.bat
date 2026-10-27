@echo off
title NagarMithra — Civic Web Portal
echo ========================================================
echo   NagarMithra Civic Web Portal — GHMC Hyderabad
echo   Starting REST API and Web Portal on Port 5000...
echo   Open your browser to: http://localhost:5000
echo ========================================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
python server.py
pause
