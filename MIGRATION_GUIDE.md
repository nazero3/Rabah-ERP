# Database Migration Guide: Desktop to Web

This guide explains how to transfer your data from the desktop version (SQLite) to the web version (localStorage).

## ⚠️ Important Notes

**DO NOT commit your database file to GitHub!**

- `inventory.db` contains your actual business data
- It should remain private and local
- Add it to `.gitignore` (already done)

## Migration Process

### Step 1: Export Data from Desktop Version

1. **Run the migration script:**
   ```bash
   cd C:\Users\nezir\Rabah_ERP
   py migrate_to_web.py
   ```

2. **This will create:**
   - `web_data_export.json` - Your data in JSON format
   - `web/import.html` - Import page for web version

### Step 2: Copy Files to Web Folder

1. **Copy the JSON file:**
   ```bash
   # Copy web_data_export.json to web folder
   copy web_data_export.json web\
   ```

2. **The import.html is already created in web folder**

### Step 3: Import to Web Version

#### Option A: Using Import Page (Recommended)

1. **Open the import page:**
   - Navigate to `web/import.html` in your browser
   - Or if deployed: `https://yourusername.github.io/repo/import.html`

2. **Import the data:**
   - Click "Choose File" and select `web_data_export.json`
   - Click "Import Data"
   - Wait for success message

3. **Go to main app:**
   - Click "Back to App"
   - Log in with your credentials
   - Your data should now be visible!

#### Option B: Using Browser Console (Advanced)

1. **Open your web app** (even if deployed)
2. **Open browser console** (F12)
3. **Paste this code** (replace with your actual data):

```javascript
// Read the JSON file first, then paste this:
const data = { /* paste your JSON data here */ };

// Import to localStorage
if (data.fans) {
    localStorage.setItem('fans_db', JSON.stringify(data.fans));
}
if (data.sheet_metal) {
    localStorage.setItem('sheet_metal_db', JSON.stringify(data.sheet_metal));
}
if (data.flexible) {
    localStorage.setItem('flexible_db', JSON.stringify(data.flexible));
}

console.log('Import complete!');
```

4. **Refresh the page** and your data will be there

## What Gets Migrated?

✅ **Migrated:**
- All fans (name, description, airflow, prices, quantity, catalog path)
- All sheet metal items
- All flexible items
- Product IDs (preserved)

❌ **Not Migrated:**
- User authentication (separate system)
- Timestamps (created_at, updated_at)
- Any custom fields not in the schema

## After Migration

### Verify Data

1. Log into web version
2. Check each product type (Fans, Sheet Metal, Flexible)
3. Verify item counts match
4. Check a few items to ensure data is correct

### Update Catalog File Paths

⚠️ **Important:** Catalog file paths from desktop won't work in web version!

- Desktop paths: `C:\Users\nezir\Rabah_ERP\rabah\file.pdf`
- Web needs: URLs or relative paths

**Options:**
1. Upload catalog files to a cloud service (Google Drive, Dropbox)
2. Get shareable links
3. Update catalog paths in web version to use URLs

## Troubleshooting

### "Database file not found"
- Make sure `inventory.db` is in the project root folder
- Check the file name is exactly `inventory.db`

### "Import failed" in web version
- Check browser console (F12) for errors
- Verify JSON file is valid (open in text editor)
- Make sure you're logged out before importing

### Data not showing after import
- Clear browser cache
- Check localStorage in browser console:
  ```javascript
  JSON.parse(localStorage.getItem('fans_db'))
  ```
- Verify data was imported correctly

### Missing some data
- Check if all tables exist in your database
- Run migration script again
- Check the export JSON file for completeness

## Keeping Data in Sync

### Option 1: Use One Version as Primary
- Choose desktop OR web as your main system
- Export/import when needed

### Option 2: Regular Exports
- Export from desktop regularly
- Import to web when needed
- Keep JSON files as backups

### Option 3: Manual Entry
- Enter new items in both versions
- Keep them synchronized manually

## Security Reminders

🔒 **Never commit these files:**
- `inventory.db` (your database)
- `web_data_export.json` (contains your data)
- Any file with actual business data

✅ **Safe to commit:**
- Code files (`.py`, `.js`, `.html`, `.css`)
- Documentation (`.md` files)
- Configuration files (without sensitive data)

## Quick Reference

```bash
# Export from desktop
py migrate_to_web.py

# Copy to web folder
copy web_data_export.json web\

# Then use import.html in browser
```

---

**Need Help?**
- Check that `inventory.db` exists in project root
- Verify Python can access sqlite3
- Check browser console for import errors

