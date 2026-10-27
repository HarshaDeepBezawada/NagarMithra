@echo off
title NagarMithra — Streamlit Executive Dashboard
echo ========================================================
echo   NagarMithra Streamlit Dashboard — GHMC Hyderabad
echo   Starting Streamlit Dashboard on Port 8501...
echo   Open your browser to: http://localhost:8501
echo ========================================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
streamlit run app.py
pause
