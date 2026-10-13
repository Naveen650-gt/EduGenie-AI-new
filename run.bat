@echo off
echo ========================================================
echo  Starting EduGenie - AI Powered Learning Assistant
echo ========================================================
echo.

py -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
