import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import InventoryDB
from price_list_window import PriceListWindow

class FanInventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("1000x700")
        
        self.db = InventoryDB()
        self.current_product_type = "fans"  # Current product type: fans, sheet_metal, flexible
        self.sort_column = "name"  # Default sort by name
        self.sort_reverse = False  # Default ascending
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Table is in row 2
        
        # Title
        self.title_label = ttk.Label(main_frame, text="Inventory Management System", 
                               font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        # Product type selection
        product_frame = ttk.LabelFrame(main_frame, text="Product Type", padding="5")
        product_frame.grid(row=1, column=0, columnspan=3, pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.product_type_var = tk.StringVar(value="fans")
        ttk.Radiobutton(product_frame, text="Fans", variable=self.product_type_var, 
                       value="fans", command=self.switch_product_type).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(product_frame, text="Sheet Metal", variable=self.product_type_var, 
                       value="sheet_metal", command=self.switch_product_type).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(product_frame, text="Flexible", variable=self.product_type_var, 
                       value="flexible", command=self.switch_product_type).pack(side=tk.LEFT, padx=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.N), padx=(0, 10))
        
        self.add_btn = ttk.Button(buttons_frame, text="Add", command=self.add_item, 
                  width=20)
        self.add_btn.pack(pady=5, fill=tk.X)
        
        self.edit_btn = ttk.Button(buttons_frame, text="Edit", command=self.edit_item, 
                  width=20)
        self.edit_btn.pack(pady=5, fill=tk.X)
        
        self.delete_btn = ttk.Button(buttons_frame, text="Delete", command=self.delete_item, 
                  width=20)
        self.delete_btn.pack(pady=5, fill=tk.X)
        
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh_table, 
                  width=20).pack(pady=5, fill=tk.X)
        ttk.Button(buttons_frame, text="Create Price List", 
                  command=self.open_price_list, width=20).pack(pady=5, fill=tk.X)
        
        # Sort controls
        self.sort_frame = ttk.LabelFrame(buttons_frame, text="Sort By", padding="5")
        self.sort_frame.pack(pady=10, fill=tk.X)
        self.update_sort_buttons()
        
        # Right side container for search and table
        right_container = ttk.Frame(main_frame)
        right_container.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_container.columnconfigure(0, weight=1)
        right_container.rowconfigure(1, weight=1)
        
        # Search frame container
        search_container = ttk.Frame(right_container)
        search_container.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        search_container.columnconfigure(0, weight=1)
        
        # Search frame (initially hidden)
        self.search_frame = ttk.Frame(search_container)
        self.search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Toggle button for search
        self.search_visible = False
        self.toggle_search_btn = ttk.Button(search_container, text="🔍 Show Search", 
                                           command=self.toggle_search, width=15)
        self.toggle_search_btn.grid(row=0, column=0, sticky=tk.E)
        
        # Table frame
        table_frame = ttk.Frame(right_container)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Create treeview (columns will be set dynamically)
        self.tree = ttk.Treeview(table_frame, 
                                 columns=("ID", "Name"),
                                 show="headings",
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Setup columns based on product type
        self.setup_table_columns()
        
        # Load initial data
        self.refresh_table()
    
    def update_sort_buttons(self):
        """Update sort buttons based on current product type"""
        # Clear existing buttons
        for widget in self.sort_frame.winfo_children():
            widget.destroy()
        
        # Common sort buttons
        ttk.Button(self.sort_frame, text="ID ↑", command=lambda: self.sort_table("id", True), 
                  width=15).pack(pady=2, fill=tk.X)
        ttk.Button(self.sort_frame, text="ID ↓", command=lambda: self.sort_table("id", False), 
                  width=15).pack(pady=2, fill=tk.X)
        
        # Name sort buttons (only for fans, not sheet_metal or flexible)
        if self.current_product_type == "fans":
            ttk.Button(self.sort_frame, text="Name ↑", command=lambda: self.sort_table("name", True), 
                      width=15).pack(pady=2, fill=tk.X)
            ttk.Button(self.sort_frame, text="Name ↓", command=lambda: self.sort_table("name", False), 
                      width=15).pack(pady=2, fill=tk.X)
        
        # Quantity sort buttons (only for fans)
        if self.current_product_type == "fans":
            ttk.Button(self.sort_frame, text="Qty ↑", command=lambda: self.sort_table("quantity", True), 
                      width=15).pack(pady=2, fill=tk.X)
            ttk.Button(self.sort_frame, text="Qty ↓", command=lambda: self.sort_table("quantity", False), 
                      width=15).pack(pady=2, fill=tk.X)
        
        # Product-specific sort buttons
        if self.current_product_type == "fans":
            ttk.Button(self.sort_frame, text="Price ↑", command=lambda: self.sort_table("price", True), 
                      width=15).pack(pady=2, fill=tk.X)
            ttk.Button(self.sort_frame, text="Price ↓", command=lambda: self.sort_table("price", False), 
                      width=15).pack(pady=2, fill=tk.X)
        elif self.current_product_type == "sheet_metal":
            ttk.Button(self.sort_frame, text="Cost ↑", command=lambda: self.sort_table("price", True), 
                      width=15).pack(pady=2, fill=tk.X)
            ttk.Button(self.sort_frame, text="Cost ↓", command=lambda: self.sort_table("price", False), 
                      width=15).pack(pady=2, fill=tk.X)
            ttk.Button(self.sort_frame, text="Thickness ↑", command=lambda: self.sort_table("thickness", True), 
                      width=15).pack(pady=2, fill=tk.X)
            ttk.Button(self.sort_frame, text="Thickness ↓", command=lambda: self.sort_table("thickness", False), 
                      width=15).pack(pady=2, fill=tk.X)
        else:  # flexible
            ttk.Button(self.sort_frame, text="Meter ↑", command=lambda: self.sort_table("price", True), 
                      width=15).pack(pady=2, fill=tk.X)
            ttk.Button(self.sort_frame, text="Meter ↓", command=lambda: self.sort_table("price", False), 
                      width=15).pack(pady=2, fill=tk.X)
            ttk.Button(self.sort_frame, text="Diameter ↑", command=lambda: self.sort_table("diameter", True), 
                      width=15).pack(pady=2, fill=tk.X)
            ttk.Button(self.sort_frame, text="Diameter ↓", command=lambda: self.sort_table("diameter", False), 
                      width=15).pack(pady=2, fill=tk.X)
    
    def setup_table_columns(self):
        """Setup table columns based on current product type"""
        # Clear existing columns
        for col in self.tree['columns']:
            self.tree.heading(col, text="")
            self.tree.column(col, width=0)
        
        if self.current_product_type == "fans":
            columns = ("ID", "Name", "Airflow", "Wholesale", "Retail", "Quantity")
            headings = ("ID", "Name", "Airflow", "Wholesale Price", "Retail Price", "Quantity")
            widths = (50, 200, 150, 120, 120, 100)
        elif self.current_product_type == "sheet_metal":
            columns = ("ID", "Thickness", "Dimensions", "Measurement", "Cost", "Extra")
            headings = ("ID", "Thickness", "Dimensions", "Measurement", "Cost", "Extra")
            widths = (50, 100, 120, 100, 100, 120)
        else:  # flexible
            columns = ("ID", "Diameter", "Collection", "Meter")
            headings = ("ID", "Diameter", "Collection", "Meter")
            widths = (50, 120, 150, 100)
        
        # Configure columns
        self.tree['columns'] = columns
        for i, (col, heading, width) in enumerate(zip(columns, headings, widths)):
            self.tree.heading(col, text=heading, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=width, anchor=tk.CENTER)
    
    def switch_product_type(self):
        """Switch between product types"""
        self.current_product_type = self.product_type_var.get()
        
        # Update title
        titles = {
            "fans": "Fans Inventory",
            "sheet_metal": "Sheet Metal Inventory",
            "flexible": "Flexible Inventory"
        }
        self.title_label.config(text=f"Inventory Management - {titles[self.current_product_type]}")
        
        # Update button labels
        labels = {
            "fans": ("Add Fan", "Edit Fan", "Delete Fan"),
            "sheet_metal": ("Add Sheet Metal", "Edit Sheet Metal", "Delete Sheet Metal"),
            "flexible": ("Add Flexible", "Edit Flexible", "Delete Flexible")
        }
        self.add_btn.config(text=labels[self.current_product_type][0])
        self.edit_btn.config(text=labels[self.current_product_type][1])
        self.delete_btn.config(text=labels[self.current_product_type][2])
        
        # Update table columns
        self.setup_table_columns()
        
        # Update sort buttons
        self.update_sort_buttons()
        
        # Refresh table with new product type
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh the table with current inventory"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get items based on current product type and search
        search_term = self.search_var.get().strip()
        
        if self.current_product_type == "fans":
            if search_term:
                items = self.db.search_fans(search_term)
            else:
                items = self.db.get_all_fans()
        elif self.current_product_type == "sheet_metal":
            if search_term:
                items = self.db.search_sheet_metal(search_term)
            else:
                items = self.db.get_all_sheet_metal()
        else:  # flexible
            if search_term:
                items = self.db.search_flexible(search_term)
            else:
                items = self.db.get_all_flexible()
        
        # Apply sorting
        items = self.apply_sorting(items)
        
        # Insert into treeview based on product type
        for item in items:
            if self.current_product_type == "fans":
                self.tree.insert("", tk.END, values=(
                    item['id'],
                    item['name'],
                    item.get('airflow') or "",
                    f"${item['price_wholesale']:.2f}",
                    f"${item['price_retail']:.2f}",
                    item['quantity']
                ))
            elif self.current_product_type == "sheet_metal":
                self.tree.insert("", tk.END, values=(
                    item['id'],
                    item.get('thickness') or "",
                    item.get('dimensions') or "",
                    item.get('measurement') or "",
                    f"${item.get('cost', 0):.2f}",
                    item.get('extra') or ""
                ))
            else:  # flexible
                self.tree.insert("", tk.END, values=(
                    item['id'],
                    item.get('diameter') or "",
                    item.get('collection') or "",
                    f"${item.get('meter', 0):.2f}"
                ))
    
    def apply_sorting(self, items):
        """Apply current sort settings to items list"""
        if self.sort_column == "id":
            items.sort(key=lambda x: x['id'], reverse=self.sort_reverse)
        elif self.sort_column == "name":
            # Name sorting only works for fans, not sheet_metal or flexible
            if self.current_product_type == "fans":
                items.sort(key=lambda x: x.get('name', '').lower(), reverse=self.sort_reverse)
            else:
                # For sheet_metal and flexible, sort by id instead if name is requested
                items.sort(key=lambda x: x['id'], reverse=self.sort_reverse)
        elif self.sort_column == "price":
            # Sort by price (retail for fans, cost for sheet_metal, meter for flexible)
            if self.current_product_type == "fans":
                items.sort(key=lambda x: x.get('price_retail', 0), reverse=self.sort_reverse)
            elif self.current_product_type == "sheet_metal":
                items.sort(key=lambda x: x.get('cost', 0), reverse=self.sort_reverse)
            else:  # flexible
                items.sort(key=lambda x: x.get('meter', 0), reverse=self.sort_reverse)
        elif self.sort_column == "quantity":
            # Quantity sorting only works for fans
            if self.current_product_type == "fans":
                items.sort(key=lambda x: x['quantity'], reverse=self.sort_reverse)
            else:
                # For sheet_metal and flexible, sort by id instead if quantity is requested
                items.sort(key=lambda x: x['id'], reverse=self.sort_reverse)
        elif self.sort_column == "airflow":
            items.sort(key=lambda x: (x.get('airflow') or '').lower(), reverse=self.sort_reverse)
        elif self.sort_column == "thickness":
            items.sort(key=lambda x: (x.get('thickness') or '').lower(), reverse=self.sort_reverse)
        elif self.sort_column == "diameter":
            items.sort(key=lambda x: (x.get('diameter') or '').lower(), reverse=self.sort_reverse)
        return items
    
    def sort_by_column(self, column_name):
        """Sort table by clicking column header"""
        # Map column names to sort keys based on product type
        if self.current_product_type == "fans":
            column_map = {
                "ID": "id",
                "Name": "name",
                "Airflow": "airflow",
                "Wholesale": "price",
                "Retail": "price",
                "Quantity": "quantity"
            }
        elif self.current_product_type == "sheet_metal":
            column_map = {
                "ID": "id",
                "Thickness": "thickness",
                "Dimensions": "thickness",  # Fallback to thickness for sorting
                "Measurement": "thickness",  # Fallback to thickness for sorting
                "Cost": "price",
                "Extra": "thickness"  # Fallback to thickness for sorting
            }
        else:  # flexible
            column_map = {
                "ID": "id",
                "Diameter": "diameter",
                "Collection": "diameter",  # Fallback to diameter for sorting
                "Meter": "price"
            }
        
        sort_key = column_map.get(column_name, "name")
        
        # Toggle reverse if clicking same column
        if self.sort_column == sort_key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = sort_key
            self.sort_reverse = False
        
        self.refresh_table()
    
    def sort_table(self, sort_by, ascending=True):
        """Sort table by specified column"""
        self.sort_column = sort_by
        self.sort_reverse = not ascending
        self.refresh_table()
    
    def open_price_list(self):
        """Open price list/inquiry window"""
        # For now, price list only works with fans
        # Can be extended later for other product types
        if self.current_product_type != "fans":
            messagebox.showinfo("Info", "Price list feature is currently available only for Fans.")
            return
        PriceListWindow(self.root, self.db)
    
    def on_search_change(self, *args):
        """Handle search input changes"""
        # Just refresh the table, which handles search
        self.refresh_table()
    
    def add_item(self):
        """Open dialog to add a new item based on product type"""
        if self.current_product_type == "fans":
            dialog = FanDialog(self.root, "Add Fan")
        elif self.current_product_type == "sheet_metal":
            dialog = SheetMetalDialog(self.root, "Add Sheet Metal")
        else:  # flexible
            dialog = FlexibleDialog(self.root, "Add Flexible")
        
        # Wait for dialog to close
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            try:
                if self.current_product_type == "fans":
                    self.db.add_fan(**dialog.result)
                    msg = "Fan added successfully!"
                elif self.current_product_type == "sheet_metal":
                    self.db.add_sheet_metal(**dialog.result)
                    msg = "Sheet Metal added successfully!"
                else:  # flexible
                    self.db.add_flexible(**dialog.result)
                    msg = "Flexible added successfully!"
                
                # Clear search to show all items including the new one
                self.search_var.set("")
                self.refresh_table()
                messagebox.showinfo("Success", msg)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add item: {str(e)}")
    
    def edit_item(self):
        """Open dialog to edit selected item"""
        selection = self.tree.selection()
        if not selection:
            product_name = {"fans": "fan", "sheet_metal": "sheet metal", "flexible": "flexible"}
            messagebox.showwarning("No Selection", f"Please select a {product_name[self.current_product_type]} to edit.")
            return
        
        item = self.tree.item(selection[0])
        item_id = item['values'][0]
        
        # Get item data
        if self.current_product_type == "fans":
            item_data = self.db.get_fan_by_id(item_id)
            if not item_data:
                messagebox.showerror("Error", "Item not found.")
                return
            dialog = FanDialog(self.root, "Edit Fan", item_data)
        elif self.current_product_type == "sheet_metal":
            item_data = self.db.get_sheet_metal_by_id(item_id)
            if not item_data:
                messagebox.showerror("Error", "Item not found.")
                return
            dialog = SheetMetalDialog(self.root, "Edit Sheet Metal", item_data)
        else:  # flexible
            item_data = self.db.get_flexible_by_id(item_id)
            if not item_data:
                messagebox.showerror("Error", "Item not found.")
                return
            dialog = FlexibleDialog(self.root, "Edit Flexible", item_data)
        
        # Wait for dialog to close
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            try:
                if self.current_product_type == "fans":
                    self.db.update_fan(item_id, **dialog.result)
                    msg = "Fan updated successfully!"
                elif self.current_product_type == "sheet_metal":
                    # Remove quantity if present (for backward compatibility)
                    result = {k: v for k, v in dialog.result.items() if k != 'quantity'}
                    self.db.update_sheet_metal(item_id, **result)
                    msg = "Sheet Metal updated successfully!"
                else:  # flexible
                    self.db.update_flexible(item_id, **dialog.result)
                    msg = "Flexible updated successfully!"
                
                self.refresh_table()
                messagebox.showinfo("Success", msg)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update item: {str(e)}")
    
    def delete_item(self):
        """Delete selected item"""
        selection = self.tree.selection()
        if not selection:
            product_name = {"fans": "fan", "sheet_metal": "sheet metal", "flexible": "flexible"}
            messagebox.showwarning("No Selection", f"Please select a {product_name[self.current_product_type]} to delete.")
            return
        
        item = self.tree.item(selection[0])
        item_id = item['values'][0]
        item_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete '{item_name}'?"):
            try:
                if self.current_product_type == "fans":
                    self.db.delete_fan(item_id)
                elif self.current_product_type == "sheet_metal":
                    self.db.delete_sheet_metal(item_id)
                else:  # flexible
                    self.db.delete_flexible(item_id)
                
                self.refresh_table()
                messagebox.showinfo("Success", "Item deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
    
    def toggle_search(self):
        """Toggle search bar visibility"""
        if self.search_visible:
            # Hide search bar
            self.search_frame.grid_remove()
            self.toggle_search_btn.config(text="🔍 Show Search")
            self.search_visible = False
            # Clear search when hiding
            self.search_var.set("")
            self.refresh_table()
        else:
            # Show search bar
            self.search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
            self.toggle_search_btn.config(text="✖ Hide Search")
            self.search_visible = True
            # Focus on search entry
            self.search_entry.focus()
    


class FanDialog:
    def __init__(self, parent, title, fan_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x380")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = ttk.Frame(self.dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Helper function to bind keyboard shortcuts to entry widgets
        def bind_shortcuts(widget):
            widget.bind('<Control-v>', lambda e: widget.event_generate('<<Paste>>'))
            widget.bind('<Control-c>', lambda e: widget.event_generate('<<Copy>>'))
            widget.bind('<Control-x>', lambda e: widget.event_generate('<<Cut>>'))
            widget.bind('<Control-a>', lambda e: widget.select_range(0, tk.END))
        
        # Name
        ttk.Label(form_frame, text="Name *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=fan_data['name'] if fan_data else "")
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=0, column=1, pady=5)
        bind_shortcuts(name_entry)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.description_var = tk.StringVar(value=fan_data.get('description', '') if fan_data else "")
        description_entry = ttk.Entry(form_frame, textvariable=self.description_var, width=30)
        description_entry.grid(row=1, column=1, pady=5)
        bind_shortcuts(description_entry)
        
        # Airflow
        ttk.Label(form_frame, text="Airflow:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.airflow_var = tk.StringVar(value=fan_data['airflow'] if fan_data and fan_data.get('airflow') else "")
        airflow_entry = ttk.Entry(form_frame, textvariable=self.airflow_var, width=30)
        airflow_entry.grid(row=2, column=1, pady=5)
        bind_shortcuts(airflow_entry)
        
        # Wholesale Price
        ttk.Label(form_frame, text="Wholesale Price *:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.wholesale_var = tk.StringVar(value=str(fan_data['price_wholesale']) if fan_data else "")
        wholesale_entry = ttk.Entry(form_frame, textvariable=self.wholesale_var, width=30)
        wholesale_entry.grid(row=3, column=1, pady=5)
        bind_shortcuts(wholesale_entry)
        
        # Retail Price
        ttk.Label(form_frame, text="Retail Price *:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.retail_var = tk.StringVar(value=str(fan_data['price_retail']) if fan_data else "")
        retail_entry = ttk.Entry(form_frame, textvariable=self.retail_var, width=30)
        retail_entry.grid(row=4, column=1, pady=5)
        bind_shortcuts(retail_entry)
        
        # Quantity
        ttk.Label(form_frame, text="Quantity *:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar(value=str(fan_data['quantity']) if fan_data else "0")
        quantity_entry = ttk.Entry(form_frame, textvariable=self.quantity_var, width=30)
        quantity_entry.grid(row=5, column=1, pady=5)
        bind_shortcuts(quantity_entry)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def save(self):
        """Validate and save form data"""
        name = self.name_var.get().strip()
        description = self.description_var.get().strip() or None
        airflow = self.airflow_var.get().strip() or None
        wholesale = self.wholesale_var.get().strip()
        retail = self.retail_var.get().strip()
        quantity = self.quantity_var.get().strip()
        
        # Validation
        if not name:
            messagebox.showerror("Validation Error", "Name is required.")
            return
        
        try:
            price_wholesale = float(wholesale)
            if price_wholesale < 0:
                raise ValueError("Price cannot be negative")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid wholesale price.")
            return
        
        try:
            price_retail = float(retail)
            if price_retail < 0:
                raise ValueError("Price cannot be negative")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid retail price.")
            return
        
        try:
            qty = int(quantity)
            if qty < 0:
                raise ValueError("Quantity cannot be negative")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid quantity.")
            return
        
        self.result = {
            'name': name,
            'description': description,
            'airflow': airflow,
            'price_wholesale': price_wholesale,
            'price_retail': price_retail,
            'quantity': qty
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


class SheetMetalDialog:
    def __init__(self, parent, title, item_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = ttk.Frame(self.dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Helper function to bind keyboard shortcuts to entry widgets
        def bind_shortcuts(widget):
            widget.bind('<Control-v>', lambda e: widget.event_generate('<<Paste>>'))
            widget.bind('<Control-c>', lambda e: widget.event_generate('<<Copy>>'))
            widget.bind('<Control-x>', lambda e: widget.event_generate('<<Cut>>'))
            widget.bind('<Control-a>', lambda e: widget.select_range(0, tk.END))
        
        # Thickness
        ttk.Label(form_frame, text="Thickness:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.thickness_var = tk.StringVar(value=item_data.get('thickness', '') if item_data else "")
        thickness_entry = ttk.Entry(form_frame, textvariable=self.thickness_var, width=30)
        thickness_entry.grid(row=0, column=1, pady=5)
        bind_shortcuts(thickness_entry)
        
        # Dimensions
        ttk.Label(form_frame, text="Dimensions:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dimensions_var = tk.StringVar(value=item_data.get('dimensions', '') if item_data else "")
        dimensions_entry = ttk.Entry(form_frame, textvariable=self.dimensions_var, width=30)
        dimensions_entry.grid(row=1, column=1, pady=5)
        bind_shortcuts(dimensions_entry)
        
        # Measurement
        ttk.Label(form_frame, text="Measurement:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.measurement_var = tk.StringVar(value=item_data.get('measurement', '') if item_data else "")
        measurement_entry = ttk.Entry(form_frame, textvariable=self.measurement_var, width=30)
        measurement_entry.grid(row=2, column=1, pady=5)
        bind_shortcuts(measurement_entry)
        
        # Cost
        ttk.Label(form_frame, text="Cost *:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.cost_var = tk.StringVar(value=str(item_data.get('cost', '')) if item_data else "")
        cost_entry = ttk.Entry(form_frame, textvariable=self.cost_var, width=30)
        cost_entry.grid(row=3, column=1, pady=5)
        bind_shortcuts(cost_entry)
        
        # Extra
        ttk.Label(form_frame, text="Extra:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.extra_var = tk.StringVar(value=item_data.get('extra', '') if item_data else "")
        extra_entry = ttk.Entry(form_frame, textvariable=self.extra_var, width=30)
        extra_entry.grid(row=4, column=1, pady=5)
        bind_shortcuts(extra_entry)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def save(self):
        """Validate and save form data"""
        thickness = self.thickness_var.get().strip() or None
        dimensions = self.dimensions_var.get().strip() or None
        measurement = self.measurement_var.get().strip() or None
        cost = self.cost_var.get().strip()
        extra = self.extra_var.get().strip() or None
        
        # Validation
        try:
            cost_value = float(cost)
            if cost_value < 0:
                raise ValueError("Cost cannot be negative")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid cost.")
            return
        
        self.result = {
            'thickness': thickness,
            'dimensions': dimensions,
            'measurement': measurement,
            'cost': cost_value,
            'extra': extra
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


class FlexibleDialog:
    def __init__(self, parent, title, item_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = ttk.Frame(self.dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Helper function to bind keyboard shortcuts to entry widgets
        def bind_shortcuts(widget):
            widget.bind('<Control-v>', lambda e: widget.event_generate('<<Paste>>'))
            widget.bind('<Control-c>', lambda e: widget.event_generate('<<Copy>>'))
            widget.bind('<Control-x>', lambda e: widget.event_generate('<<Cut>>'))
            widget.bind('<Control-a>', lambda e: widget.select_range(0, tk.END))
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.description_var = tk.StringVar(value=item_data.get('description', '') if item_data else "")
        description_entry = ttk.Entry(form_frame, textvariable=self.description_var, width=30)
        description_entry.grid(row=0, column=1, pady=5)
        bind_shortcuts(description_entry)
        
        # Diameter
        ttk.Label(form_frame, text="Diameter:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.diameter_var = tk.StringVar(value=item_data.get('diameter', '') if item_data else "")
        diameter_entry = ttk.Entry(form_frame, textvariable=self.diameter_var, width=30)
        diameter_entry.grid(row=1, column=1, pady=5)
        bind_shortcuts(diameter_entry)
        
        # Collection
        ttk.Label(form_frame, text="Collection:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.collection_var = tk.StringVar(value=item_data.get('collection', '') if item_data else "")
        collection_entry = ttk.Entry(form_frame, textvariable=self.collection_var, width=30)
        collection_entry.grid(row=2, column=1, pady=5)
        bind_shortcuts(collection_entry)
        
        # Meter
        ttk.Label(form_frame, text="Meter *:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.meter_var = tk.StringVar(value=str(item_data.get('meter', '')) if item_data else "")
        meter_entry = ttk.Entry(form_frame, textvariable=self.meter_var, width=30)
        meter_entry.grid(row=3, column=1, pady=5)
        bind_shortcuts(meter_entry)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def save(self):
        """Validate and save form data"""
        description = self.description_var.get().strip() or None
        diameter = self.diameter_var.get().strip() or None
        collection = self.collection_var.get().strip() or None
        meter = self.meter_var.get().strip()
        
        # Validation
        try:
            meter_value = float(meter)
            if meter_value < 0:
                raise ValueError("Meter cannot be negative")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid meter value.")
            return
        
        self.result = {
            'description': description,
            'diameter': diameter,
            'collection': collection,
            'meter': meter_value
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FanInventoryApp(root)
    root.mainloop()

