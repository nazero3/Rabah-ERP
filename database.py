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
        """Initialize database with fans table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
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

