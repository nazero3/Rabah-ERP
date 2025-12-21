# Fan Inventory Management System

A desktop application for managing fan inventory with features for product management, search, and price list/inquiry generation.

## Features

- **Product Management**
  - Add new fans to inventory
  - Edit existing fan details
  - Delete fans from inventory
  - View all fans in a searchable table

- **Product Information**
  - Name (required)
  - Airflow (optional)
  - Wholesale Price (required)
  - Retail Price (required)
  - Quantity (required)

- **Price List / Inquiry Generator**
  - Search for fans by name or airflow
  - Add multiple fans to a price list
  - Switch between retail and wholesale pricing
  - Remove items from price list
  - Export price list to text file

## Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)
- sqlite3 (included with Python)
- python-docx (for Word export feature)

## Installation

1. Make sure Python is installed on your system:
   ```bash
   # On Windows, use the Python launcher:
   py --version
   
   # On Linux/Mac:
   python --version
   # or
   python3 --version
   ```

2. Clone or download this repository

3. Install required packages:
   ```bash
   pip install python-docx
   ```
   
   Or install from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

1. Open a terminal/command prompt in the project directory

2. Run the main application:
   ```bash
   # On Windows:
   py main.py
   
   # On Linux/Mac:
   python main.py
   # or
   python3 main.py
   ```
   
   **Windows Users:** You can also double-click `run.bat` to start the application.

### Managing Inventory

1. **Add a Fan**: Click "Add Fan" button, fill in the form, and click "Save"
2. **Edit a Fan**: Select a fan from the table, click "Edit Fan", modify the details, and click "Save"
3. **Delete a Fan**: Select a fan from the table, click "Delete Fan", and confirm
4. **Search**: Type in the search box to filter fans by name or airflow

### Creating Price Lists

1. Click "Create Price List" button
2. Search for fans in the left panel
3. Select a fan and click "Add to Price List →"
4. Choose between Retail or Wholesale pricing
5. Add multiple fans as needed
6. Click "Export to Word" to save the price list to a Word document (.docx file)

## Database

The application uses SQLite database (`inventory.db`) which is automatically created in the same directory as the application. The database stores all fan information persistently.

## File Structure

```
.
├── main.py                 # Main application window
├── database.py            # Database operations
├── price_list_window.py   # Price list/inquiry window
├── requirements.txt       # Dependencies (none required)
├── README.md             # This file
├── run.bat               # Windows launcher (double-click to run)
└── inventory.db          # SQLite database (created automatically)
```

## Notes

- The database file (`inventory.db`) will be created automatically on first run
- All prices are stored in the database and can be updated at any time
- Price lists can be exported as text files for sharing or printing
- The application runs entirely offline - no internet connection required

## Transferring to Another Computer

**Yes, you can copy the entire project folder to another laptop!**

### What to Copy:
Copy the entire project folder containing:
- `main.py`
- `database.py`
- `price_list_window.py`
- `run.bat` (Windows launcher)
- `inventory.db` (if you want to keep your existing data)
- `README.md` (optional)

### Requirements on the New Laptop:
1. **Python must be installed** (3.7 or higher)
   - Check with: `py --version` (Windows) or `python3 --version` (Linux/Mac)
   - If not installed, download from [python.org](https://www.python.org/downloads/)

2. **That's it!** No additional software needed.

### Important Notes:
- If you copy `inventory.db`, all your fan data will be transferred
- If you don't copy `inventory.db`, a new empty database will be created
- The program will work the same way on any Windows, Mac, or Linux computer with Python installed
- You can use a USB drive, cloud storage, or network share to transfer the files

## Troubleshooting

**If tkinter is not available:**
- On Linux: Install with `sudo apt-get install python3-tk` (Ubuntu/Debian) or `sudo yum install python3-tkinter` (CentOS/RHEL)
- On macOS: tkinter should be included with Python
- On Windows: tkinter is included with Python

**If Python command is not found on Windows:**
- Use `py` instead of `python` (Python launcher for Windows)
- Or double-click `run.bat` to start the application
- If `py` doesn't work, install Python from [python.org](https://www.python.org/downloads/) and make sure to check "Add Python to PATH" during installation

**If you get import errors:**
- Make sure all files (`main.py`, `database.py`, `price_list_window.py`) are in the same directory
- Ensure you're using Python 3.7 or higher

## License

This project is provided as-is for personal or commercial use.

