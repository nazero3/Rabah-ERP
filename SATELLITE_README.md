# Installation Guide - Toshiba Satellite A505

## System Specifications
- **Operating System:** Windows 7 Ultimate (32-bit)
- **Processor:** Intel Core 2 Duo T6500 @ 2.10GHz
- **Memory (RAM):** 4 GB (2.87 GB usable)
- **System Type:** 32-bit (X86-based PC)

---

## Method 1: Using .exe File (Recommended)

### Steps:

1. **Get the Rabah_ERP.exe file**
   - You should have the `Rabah_ERP.exe` file from the computer where the application was built
   - Copy the file to the laptop

2. **Copy required files**
   - Copy `Rabah_ERP.exe` to any folder you want (e.g., `C:\Rabah_ERP\` or `D:\Rabah_ERP\`)
   - If you have a `format.docx` or `template.docx` file, copy it to the same folder as the `.exe` file

3. **Run the application**
   - Double-click `Rabah_ERP.exe`
   - **Note:** The first launch may take longer (30-60 seconds) as files are being extracted
   - The `inventory.db` file will be created automatically in the same folder

4. **If you see an error message "Windows cannot verify the publisher"**
   - Click "More info"
   - Click "Run anyway"
   - This is normal because the file is not digitally signed

---

## Method 2: Install Python and Run Code

### Requirements:
- Python 3.7 or 3.8 (Important: Must be 32-bit to match Windows 7 32-bit)
- Internet connection for download

### Detailed Steps:

#### 1. Download Python 3.8 (32-bit)

**⚠️ Very Important:** You must download the 32-bit version because your system is 32-bit

1. Open your browser and go to:
   ```
   https://www.python.org/downloads/release/python-3810/
   ```
   Or search for "Python 3.8.10 Windows 32-bit"

2. Look for the download link:
   - **Windows x86 executable installer** (This is the file you need)
   - File size: approximately 25-30 MB

3. Download the file (e.g., `python-3.8.10.exe`)

#### 2. Install Python

1. **Run the installer** (you may need administrator privileges)
2. **In the installation screen:**
   - ✅ **Make sure to check "Add Python 3.8 to PATH"** (Very important!)
   - Choose "Install Now" or "Customize installation"
   - If you choose "Customize installation":
     - In "Optional Features": Select everything
     - In "Advanced Options": Make sure to check "Add Python to environment variables"

3. Wait for installation to complete (5-10 minutes)

4. **Verify the installation:**
   - Open "Command Prompt" (cmd)
   - Type: `py --version`
   - You should see: `Python 3.8.10` or similar version number

#### 3. Copy Application Files

1. **Create a new folder** (e.g., `C:\Rabah_ERP\` or `D:\Rabah_ERP\`)

2. **Copy these files to the folder:**
   - `main.py`
   - `database.py`
   - `price_list_window.py`
   - `logo.png` (if available)
   - `logo.ico` (if available)
   - `format.docx` or `template.docx` (if available)
   - `run.bat` (optional - for quick launch)

#### 4. Install Required Libraries

1. Open "Command Prompt" (cmd)
   - Press `Win + R`
   - Type: `cmd`
   - Press Enter

2. **Navigate to the application folder:**
   ```
   cd C:\Rabah_ERP
   ```
   (Replace `C:\Rabah_ERP` with your actual folder path)

3. **Install required libraries:**
   ```
   py -m pip install python-docx
   ```
   
   Wait for installation to complete (1-2 minutes)

#### 5. Run the Application

**Method 1 - Using run.bat:**
- Double-click `run.bat`

**Method 2 - From Command Prompt:**
1. Open Command Prompt
2. Navigate to the application folder:
   ```
   cd C:\Rabah_ERP
   ```
3. Run the application:
   ```
   py main.py
   ```

---

## Troubleshooting

### Problem 1: "Python is not recognized"
**Solution:**
1. Reinstall Python with "Add Python to PATH" checked
2. Or use `py` instead of `python` in commands

### Problem 2: "pip is not recognized"
**Solution:**
Use:
```
py -m pip install python-docx
```
Instead of:
```
pip install python-docx
```

### Problem 3: Application is slow to start
**Solution:**
- This is normal on older Windows 7 systems
- Wait 30-60 seconds on first launch
- The application will run faster afterwards

### Problem 4: Error message "tkinter not found"
**Solution:**
1. Reinstall Python
2. In the installation screen, choose "Customize installation"
3. Make sure to check "tcl/tk and IDLE" in "Optional Features"

### Problem 5: "ModuleNotFoundError: No module named 'docx'"
**Solution:**
Run this command in Command Prompt:
```
py -m pip install python-docx
```

### Problem 6: Application doesn't open (nothing appears)
**Solution:**
1. Open Command Prompt
2. Navigate to the application folder
3. Run: `py main.py`
4. Read any error messages that appear

---

## Important Notes

### ✅ What works well:
- Windows 7 Ultimate is fully compatible
- 4 GB RAM is sufficient for the application
- Core 2 Duo processor is adequate

### ⚠️ Warnings:
- **Do not use Python 3.9 or newer** - May not work well on Windows 7
- **Use Python 3.7 or 3.8 only**
- **Make sure to install the 32-bit version** of Python
- If you have antivirus software, the application may need to be added as an exception

### 💾 Disk Space Required:
- Python: approximately 100-150 MB
- Application: approximately 5-10 MB
- Database: increases with usage (usually less than 10 MB)

### 🔄 Updates:
- If you want to update the application:
  1. Save the `inventory.db` file (contains your data)
  2. Delete old files
  3. Copy new files
  4. Place `inventory.db` in the same folder

---

## Support

If you encounter any problems:
1. Make sure you followed the steps carefully
2. Check error messages in Command Prompt
3. Verify Python 3.8 (32-bit) is installed correctly

---

## Quick Summary

**For quick use (recommended):**
1. Copy `Rabah_ERP.exe` to the computer
2. Double-click to run it
3. Done!

**For full installation:**
1. Install Python 3.8 (32-bit) with "Add to PATH" checked
2. Copy application files
3. Run: `py -m pip install python-docx`
4. Run: `py main.py`

---

**Last Updated:** 2025-01-29


