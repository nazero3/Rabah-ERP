@echo off
echo Starting Fan Inventory Management System...
py main.py
if errorlevel 1 (
    echo.
    echo Error: Could not start the application.
    echo Make sure Python is installed and accessible via 'py' command.
    pause
)

