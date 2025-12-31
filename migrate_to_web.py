"""
Migration Tool: Desktop Database to Web Format
Converts SQLite database (inventory.db) to JSON format for web version
"""

import sqlite3
import json
import os
from datetime import datetime

def export_database_to_json(db_path="inventory.db", output_file="web_data_export.json"):
    """
    Export all data from SQLite database to JSON format
    that can be imported into the web version
    """
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()
    
    data = {
        'fans': [],
        'sheet_metal': [],
        'flexible': [],
        'export_date': datetime.now().isoformat(),
        'version': '1.0'
    }
    
    try:
        def safe_get(row, key, default=None):
            """Safely get value from sqlite3.Row, handling missing columns"""
            try:
                return row[key]
            except (KeyError, IndexError):
                return default
        
        # Export Fans
        cursor.execute("SELECT * FROM fans")
        fans = cursor.fetchall()
        for fan in fans:
            data['fans'].append({
                'id': fan['id'],
                'name': fan['name'],
                'description': safe_get(fan, 'description'),
                'airflow': safe_get(fan, 'airflow'),
                'price_wholesale': fan['price_wholesale'],
                'price_retail': fan['price_retail'],
                'quantity': fan['quantity'],
                'catalog_file_path': safe_get(fan, 'catalog_file_path')
            })
        
        # Export Sheet Metal
        cursor.execute("SELECT * FROM sheet_metal")
        sheet_metal = cursor.fetchall()
        for item in sheet_metal:
            data['sheet_metal'].append({
                'id': item['id'],
                'thickness': safe_get(item, 'thickness'),
                'dimensions': safe_get(item, 'dimensions'),
                'measurement': safe_get(item, 'measurement'),
                'cost': item['cost'],
                'extra': safe_get(item, 'extra')
            })
        
        # Export Flexible
        cursor.execute("SELECT * FROM flexible")
        flexible = cursor.fetchall()
        for item in flexible:
            data['flexible'].append({
                'id': item['id'],
                'description': safe_get(item, 'description'),
                'diameter': safe_get(item, 'diameter'),
                'collection': safe_get(item, 'collection'),
                'meter': item['meter']
            })
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("Export successful!")
        print(f"   - Fans: {len(data['fans'])} items")
        print(f"   - Sheet Metal: {len(data['sheet_metal'])} items")
        print(f"   - Flexible: {len(data['flexible'])} items")
        print(f"   - Output file: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error exporting data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

def create_web_import_script(json_file="web_data_export.json"):
    """
    Create an HTML file with import functionality for the web version
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Import Data to Web Version</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            direction: rtl;
        }}
        .container {{
            background: #f5f5f5;
            padding: 30px;
            border-radius: 10px;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .info {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        button {{
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
            margin: 10px 0;
        }}
        button:hover {{
            background: #5568d3;
        }}
        #fileInput {{
            margin: 20px 0;
            padding: 10px;
            width: 100%;
        }}
        #result {{
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            display: none;
        }}
        .success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>استيراد البيانات / Import Data</h1>
        
        <div class="info">
            <strong>تعليمات / Instructions:</strong><br>
            1. تأكد من تسجيل الخروج من النسخة الويب أولاً<br>
            2. اختر ملف JSON المُصدّر<br>
            3. انقر على "استيراد البيانات"<br>
            4. بعد الاستيراد، سجل دخول مرة أخرى<br><br>
            
            <strong>English:</strong><br>
            1. Make sure you're logged out of the web version first<br>
            2. Select the exported JSON file<br>
            3. Click "Import Data"<br>
            4. After import, log in again
        </div>
        
        <input type="file" id="fileInput" accept=".json">
        <button onclick="importData()">استيراد البيانات / Import Data</button>
        <button onclick="window.location.href='index.html'">العودة للتطبيق / Back to App</button>
        
        <div id="result"></div>
    </div>
    
    <script>
        function importData() {{
            const fileInput = document.getElementById('fileInput');
            const resultDiv = document.getElementById('result');
            
            if (!fileInput.files.length) {{
                showResult('يرجى اختيار ملف / Please select a file', 'error');
                return;
            }}
            
            const file = fileInput.files[0];
            const reader = new FileReader();
            
            reader.onload = function(e) {{
                try {{
                    const data = JSON.parse(e.target.result);
                    
                    // Import to localStorage
                    if (data.fans) {{
                        localStorage.setItem('fans_db', JSON.stringify(data.fans));
                    }}
                    if (data.sheet_metal) {{
                        localStorage.setItem('sheet_metal_db', JSON.stringify(data.sheet_metal));
                    }}
                    if (data.flexible) {{
                        localStorage.setItem('flexible_db', JSON.stringify(data.flexible));
                    }}
                    
                    const total = (data.fans?.length || 0) + 
                                 (data.sheet_metal?.length || 0) + 
                                 (data.flexible?.length || 0);
                    
                    showResult(
                        `تم الاستيراد بنجاح! / Import successful!<br>` +
                        `- Fans: ${{data.fans?.length || 0}}<br>` +
                        `- Sheet Metal: ${{data.sheet_metal?.length || 0}}<br>` +
                        `- Flexible: ${{data.flexible?.length || 0}}<br>` +
                        `- Total: ${{total}} items`,
                        'success'
                    );
                }} catch (error) {{
                    showResult('خطأ في قراءة الملف / Error reading file: ' + error.message, 'error');
                }}
            }};
            
            reader.readAsText(file);
        }}
        
        function showResult(message, type) {{
            const resultDiv = document.getElementById('result');
            resultDiv.className = type;
            resultDiv.innerHTML = message;
            resultDiv.style.display = 'block';
        }}
    </script>
</body>
</html>
"""
    
    with open('web/import.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Import page created: web/import.html")

if __name__ == "__main__":
    print("=" * 50)
    print("Desktop to Web Database Migration Tool")
    print("=" * 50)
    print()
    
    # Export database
    success = export_database_to_json()
    
    if success:
        print()
        print("Creating web import page...")
        create_web_import_script()
        print()
        print("=" * 50)
        print("Next Steps:")
        print("=" * 50)
        print("1. Copy 'web_data_export.json' to your web folder")
        print("2. The import.html is already created in web folder")
        print("3. Open 'web/import.html' in your browser")
        print("4. Select the JSON file and import")
        print("5. Go back to index.html and log in")
        print("=" * 50)
    else:
        print("\nMigration failed. Please check the error above.")

