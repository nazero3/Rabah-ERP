@echo off
REM Advanced build script with data files inclusion
REM This version includes template files and creates a folder structure

echo ========================================
echo Building Rabah ERP Executable (Advanced)
echo ========================================
echo.

REM Check if PyInstaller is installed
py -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    py -m pip install pyinstaller
    echo.
)

REM Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Rabah_ERP.spec del /q Rabah_ERP.spec

echo Building executable...
echo.

REM Check if template files exist
set DATA_FILES=
if exist template.docx set DATA_FILES=--add-data="template.docx;."
if exist format.docx (
    if defined DATA_FILES (
        set DATA_FILES=%DATA_FILES% --add-data="format.docx;."
    ) else (
        set DATA_FILES=--add-data="format.docx;."
    )
)

REM Check which icon file exists (prefer .ico, fallback to .png)
if exist logo.ico (
    set ICON_FILE=logo.ico
    echo Using logo.ico for executable icon
) else if exist logo.png (
    set ICON_FILE=logo.png
    echo Using logo.png for executable icon (consider converting to .ico for better results)
) else (
    echo WARNING: No icon file found! The executable will use the default Python icon.
    set ICON_FILE=
)
echo.

REM Build the executable with icon and data files
if defined ICON_FILE (
    py -m PyInstaller ^
        --name="Rabah_ERP" ^
        --onefile ^
        --windowed ^
        --icon="%ICON_FILE%" ^
        --add-data="database.py;." ^
        --add-data="price_list_window.py;." ^
        --add-data="logo.png;." ^
        --add-data="logo.ico;." ^
        %DATA_FILES% ^
        --hidden-import=tkinter ^
        --hidden-import=sqlite3 ^
        --hidden-import=docx ^
        --hidden-import=docx.shared ^
        --hidden-import=docx.oxml.ns ^
        --hidden-import=docx.oxml ^
        --collect-all docx ^
        main.py
) else (
    py -m PyInstaller ^
        --name="Rabah_ERP" ^
        --onefile ^
        --windowed ^
        --add-data="database.py;." ^
        --add-data="price_list_window.py;." ^
        --add-data="logo.png;." ^
        --add-data="logo.ico;." ^
        %DATA_FILES% ^
        --hidden-import=tkinter ^
        --hidden-import=sqlite3 ^
        --hidden-import=docx ^
        --hidden-import=docx.shared ^
        --hidden-import=docx.oxml.ns ^
        --hidden-import=docx.oxml ^
        --collect-all docx ^
        main.py
)

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
echo IMPORTANT NOTES:
echo - Copy template.docx (or format.docx) to the same folder as the .exe
echo - The database file (inventory.db) will be created automatically
echo - If the taskbar icon still shows incorrectly, try:
echo   1. Delete the .exe and rebuild
echo   2. Clear Windows icon cache: Delete the IconCache.db file in:
echo      %%localappdata%%\Microsoft\Windows\Explorer\
echo   3. Restart Windows Explorer or reboot
echo.
pause

