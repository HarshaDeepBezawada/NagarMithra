@echo off
title NagarMithra — Automated Test Suite
echo ========================================================
echo   Running NagarMithra Pytest Business Logic Suite...
echo ========================================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
pytest test_logic.py -v
echo ========================================================
echo   Test execution finished.
echo ========================================================
pause
