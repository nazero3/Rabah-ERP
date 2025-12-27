# Building Executable (.exe) from Python Script

This guide explains how to convert the Rabah ERP application into a standalone Windows executable (.exe) file.

## Prerequisites

1. **Python installed** (version 3.7 or higher)
2. **All dependencies installed**: Run `pip install -r requirements.txt`
3. **PyInstaller**: Will be installed automatically by the build script, or install manually:
   ```bash
   pip install pyinstaller
   ```

## Quick Build (Recommended)

1. **Double-click `build_exe.bat`** in the project folder
2. Wait for the build process to complete (this may take a few minutes)
3. Your executable will be in the `dist` folder: `dist\Rabah_ERP.exe`

## Manual Build (Advanced)

If you prefer to build manually or customize the build:

```bash
pip install pyinstaller
pyinstaller --name="Rabah_ERP" --onefile --windowed --icon=logo.png --add-data="database.py;." --add-data="price_list_window.py;." main.py
```

## Icon Setup

- **Current icon file**: `logo.png`
- The build script automatically uses `logo.png` as the .exe icon
- **To use a different icon**: Replace `logo.png` or use an `.ico` file and update the `--icon` parameter

### Converting PNG to ICO (Optional)

If you want to use a `.ico` file instead of `.png`:

1. Use an online converter like [convertio.co](https://convertio.co/png-ico/)
2. Save as `logo.ico` in the project folder
3. Update `build_exe.bat` to use `--icon=logo.ico` instead of `--icon=logo.png`

## Distribution

### Files to Include with the Executable

When distributing your application, include:

1. **Rabah_ERP.exe** (from `dist` folder)
2. **template.docx** or **format.docx** (if you use template-based export)
   - Place in the same folder as the .exe
3. **logo.png** (optional, only if referenced in code)

### Files Created Automatically

- **inventory.db** - Created automatically when the app first runs
- Other data files are created as needed

## Build Script Options

### `build_exe.bat` (Simple)
- Creates a single .exe file
- Includes necessary Python modules
- Basic configuration

### `build_exe_advanced.bat` (Advanced)
- Includes template files if they exist
- More comprehensive module inclusion
- Better for production builds

## Troubleshooting

### "PyInstaller not found"
- The script will try to install it automatically
- Or install manually: `pip install pyinstaller`

### "Module not found" errors
- Add missing modules to `--hidden-import` in the build script
- Or use `--collect-all <module_name>` to include all submodules

### Large file size
- The .exe includes Python interpreter and all dependencies
- Expect 20-50 MB file size (normal for PyInstaller onefile)
- Use `--onedir` instead of `--onefile` for smaller size (but multiple files)

### Icon not showing
- Ensure `logo.png` exists in the project folder
- Try converting to `.ico` format
- Rebuild after changing the icon file

### Template file not found after building
- Copy `template.docx` or `format.docx` to the same folder as the .exe
- Or modify the build script to include it with `--add-data`

## Notes

- The executable is a standalone file - users don't need Python installed
- First run may be slower as files are extracted to a temporary location
- Antivirus software may flag the .exe (false positive) - this is normal for PyInstaller executables
- The executable works on the same Windows version where it was built (or compatible versions)
