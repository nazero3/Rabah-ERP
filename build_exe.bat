@echo off
REM Build script to create executable from main.py
REM This script uses PyInstaller to bundle the application into an .exe file

echo ========================================
echo Building Rabah ERP Executable
echo ========================================
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    echo.
)

REM Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist main.spec del /q main.spec

echo Building executable...
echo.

REM Build the executable with icon
python -m PyInstaller ^
    --name="Rabah_ERP" ^
    --onefile ^
    --windowed ^
    --icon=logo.png ^
    --add-data="database.py;." ^
    --add-data="price_list_window.py;." ^
    --add-data="logo.png;." ^
    --hidden-import=tkinter ^
    --hidden-import=sqlite3 ^
    --hidden-import=docx ^
    --hidden-import=docx.shared ^
    --hidden-import=docx.oxml.ns ^
    --hidden-import=docx.oxml ^
    --collect-all docx ^
    main.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo The executable is located in: dist\Rabah_ERP.exe
echo.
echo Note: The database file (inventory.db) will be created automatically 
echo       in the same directory as the executable when you first run it.
echo.
pause
