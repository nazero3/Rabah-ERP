import sqlite3
import os
from typing import List, Dict, Optional

class InventoryDB:
    def __init__(self, db_path: str = "inventory.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with all product tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Fans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                airflow TEXT,
                price_wholesale REAL NOT NULL,
                price_retail REAL NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sheet Metal table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sheet_metal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thickness TEXT,
                dimensions TEXT,
                measurement TEXT,
                cost REAL NOT NULL,
                extra TEXT,
                quantity INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migrate existing sheet_metal table if it has name/description columns
        try:
            cursor.execute("PRAGMA table_info(sheet_metal)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'name' in columns or 'description' in columns:
                # Create new table without name and description
                cursor.execute('''
                    CREATE TABLE sheet_metal_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        thickness TEXT,
                        dimensions TEXT,
                        measurement TEXT,
                        cost REAL NOT NULL,
                        extra TEXT,
                        quantity INTEGER NOT NULL DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                # Copy data (excluding name and description)
                cursor.execute('''
                    INSERT INTO sheet_metal_new (id, thickness, dimensions, measurement, cost, extra, quantity, created_at, updated_at)
                    SELECT id, thickness, dimensions, measurement, cost, extra, quantity, created_at, updated_at
                    FROM sheet_metal
                ''')
                # Drop old table and rename new one
                cursor.execute('DROP TABLE sheet_metal')
                cursor.execute('ALTER TABLE sheet_metal_new RENAME TO sheet_metal')
        except sqlite3.OperationalError:
            pass  # Table might not exist yet or migration already done
        
        # Flexible table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flexible (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                diameter TEXT,
                collection TEXT,
                meter REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migrate existing flexible table if it has name/quantity columns
        try:
            cursor.execute("PRAGMA table_info(flexible)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'name' in columns or 'quantity' in columns:
                # Create new table without name and quantity
                cursor.execute('''
                    CREATE TABLE flexible_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT,
                        diameter TEXT,
                        collection TEXT,
                        meter REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                # Copy data (excluding name and quantity)
                cursor.execute('''
                    INSERT INTO flexible_new (id, description, diameter, collection, meter, created_at, updated_at)
                    SELECT id, description, diameter, collection, meter, created_at, updated_at
                    FROM flexible
                ''')
                # Drop old table and rename new one
                cursor.execute('DROP TABLE flexible')
                cursor.execute('ALTER TABLE flexible_new RENAME TO flexible')
        except sqlite3.OperationalError:
            pass  # Table might not exist yet or migration already done
        
        # Add description column to existing databases (migration)
        try:
            cursor.execute('ALTER TABLE fans ADD COLUMN description TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        
        
        conn.commit()
        conn.close()
    
    def add_fan(self, name: str, description: Optional[str], airflow: Optional[str], 
                price_wholesale: float, price_retail: float, quantity: int) -> int:
        """Add a new fan to inventory"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO fans (name, description, airflow, price_wholesale, price_retail, quantity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, airflow, price_wholesale, price_retail, quantity))
        
        fan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return fan_id
    
    def update_fan(self, fan_id: int, name: str, description: Optional[str], 
                   airflow: Optional[str], price_wholesale: float, price_retail: float, quantity: int):
        """Update an existing fan"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE fans 
            SET name = ?, description = ?, airflow = ?, price_wholesale = ?, price_retail = ?, 
                quantity = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (name, description, airflow, price_wholesale, price_retail, quantity, fan_id))
        
        conn.commit()
        conn.close()
    
    def delete_fan(self, fan_id: int):
        """Delete a fan from inventory"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM fans WHERE id = ?', (fan_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_fans(self) -> List[Dict]:
        """Get all fans from inventory"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM fans ORDER BY name')
        fans = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return fans
    
    def get_fan_by_id(self, fan_id: int) -> Optional[Dict]:
        """Get a specific fan by ID"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM fans WHERE id = ?', (fan_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def search_fans(self, search_term: str) -> List[Dict]:
        """Search fans by name, description, or airflow"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_pattern = f'%{search_term}%'
        cursor.execute('''
            SELECT * FROM fans 
            WHERE name LIKE ? OR description LIKE ? OR airflow LIKE ?
            ORDER BY name
        ''', (search_pattern, search_pattern, search_pattern))
        
        fans = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return fans
    
    def update_quantity(self, fan_id: int, quantity_change: int):
        """Update fan quantity (add or subtract)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT quantity FROM fans WHERE id = ?', (fan_id,))
        current_qty = cursor.fetchone()[0]
        new_qty = max(0, current_qty + quantity_change)
        
        cursor.execute('''
            UPDATE fans 
            SET quantity = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_qty, fan_id))
        
        conn.commit()
        conn.close()
    
    # ===== SHEET METAL METHODS =====
    
    def add_sheet_metal(self, thickness: Optional[str],
                        dimensions: Optional[str], measurement: Optional[str], cost: float,
                        extra: Optional[str]) -> int:
        """Add a new sheet metal to inventory"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sheet_metal (thickness, dimensions, measurement, cost, extra, quantity)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (thickness, dimensions, measurement, cost, extra))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id
    
    def update_sheet_metal(self, item_id: int, thickness: Optional[str], 
                          dimensions: Optional[str], measurement: Optional[str], 
                          cost: float, extra: Optional[str]):
        """Update an existing sheet metal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sheet_metal 
            SET thickness = ?, dimensions = ?, measurement = ?,
                cost = ?, extra = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (thickness, dimensions, measurement, cost, extra, item_id))
        
        conn.commit()
        conn.close()
    
    def delete_sheet_metal(self, item_id: int):
        """Delete a sheet metal from inventory"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sheet_metal WHERE id = ?', (item_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_sheet_metal(self) -> List[Dict]:
        """Get all sheet metal from inventory"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sheet_metal ORDER BY id')
        items = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return items
    
    def get_sheet_metal_by_id(self, item_id: int) -> Optional[Dict]:
        """Get a specific sheet metal by ID"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sheet_metal WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def search_sheet_metal(self, search_term: str) -> List[Dict]:
        """Search sheet metal by name, description, or other fields"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_pattern = f'%{search_term}%'
        cursor.execute('''
            SELECT * FROM sheet_metal 
            WHERE name LIKE ? OR description LIKE ? OR thickness LIKE ? 
               OR dimensions LIKE ? OR measurement LIKE ? OR extra LIKE ?
            ORDER BY name
        ''', (search_pattern, search_pattern, search_pattern, search_pattern, 
              search_pattern, search_pattern))
        
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    # ===== FLEXIBLE METHODS =====
    
    def add_flexible(self, description: Optional[str], diameter: Optional[str],
                    collection: Optional[str], meter: float) -> int:
        """Add a new flexible to inventory"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO flexible (description, diameter, collection, meter)
            VALUES (?, ?, ?, ?)
        ''', (description, diameter, collection, meter))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id
    
    def update_flexible(self, item_id: int, description: Optional[str],
                       diameter: Optional[str], collection: Optional[str], meter: float):
        """Update an existing flexible"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE flexible 
            SET description = ?, diameter = ?, collection = ?,
                meter = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (description, diameter, collection, meter, item_id))
        
        conn.commit()
        conn.close()
    
    def delete_flexible(self, item_id: int):
        """Delete a flexible from inventory"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM flexible WHERE id = ?', (item_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_flexible(self) -> List[Dict]:
        """Get all flexible from inventory"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM flexible ORDER BY id')
        items = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return items
    
    def get_flexible_by_id(self, item_id: int) -> Optional[Dict]:
        """Get a specific flexible by ID"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM flexible WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def search_flexible(self, search_term: str) -> List[Dict]:
        """Search flexible by description, diameter, or collection fields"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_pattern = f'%{search_term}%'
        cursor.execute('''
            SELECT * FROM flexible 
            WHERE description LIKE ? OR diameter LIKE ? OR collection LIKE ?
            ORDER BY id
        ''', (search_pattern, search_pattern, search_pattern))
        
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

