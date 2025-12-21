import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import InventoryDB
from price_list_window import PriceListWindow

class FanInventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fan Inventory Management System")
        self.root.geometry("1000x700")
        
        self.db = InventoryDB()
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Fan Inventory Management", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.N), padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Add Fan", command=self.add_fan, 
                  width=20).pack(pady=5, fill=tk.X)
        ttk.Button(buttons_frame, text="Edit Fan", command=self.edit_fan, 
                  width=20).pack(pady=5, fill=tk.X)
        ttk.Button(buttons_frame, text="Delete Fan", command=self.delete_fan, 
                  width=20).pack(pady=5, fill=tk.X)
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh_table, 
                  width=20).pack(pady=5, fill=tk.X)
        ttk.Button(buttons_frame, text="Create Price List", 
                  command=self.open_price_list, width=20).pack(pady=5, fill=tk.X)
        
        # Search frame container
        search_container = ttk.Frame(main_frame)
        search_container.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
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
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(table_frame, 
                                 columns=("ID", "Name", "Airflow", "Wholesale", "Retail", "Quantity"),
                                 show="headings",
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Airflow", text="Airflow")
        self.tree.heading("Wholesale", text="Wholesale Price")
        self.tree.heading("Retail", text="Retail Price")
        self.tree.heading("Quantity", text="Quantity")
        
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Name", width=200, anchor=tk.CENTER)
        self.tree.column("Airflow", width=150, anchor=tk.CENTER)
        self.tree.column("Wholesale", width=120, anchor=tk.CENTER)
        self.tree.column("Retail", width=120, anchor=tk.CENTER)
        self.tree.column("Quantity", width=100, anchor=tk.CENTER)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Load initial data
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh the table with current inventory"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get fans based on current search
        search_term = self.search_var.get().strip()
        if search_term:
            fans = self.db.search_fans(search_term)
        else:
            fans = self.db.get_all_fans()
        
        # Insert into treeview
        for fan in fans:
            self.tree.insert("", tk.END, values=(
                fan['id'],
                fan['name'],
                fan['airflow'] or "",
                f"${fan['price_wholesale']:.2f}",
                f"${fan['price_retail']:.2f}",
                fan['quantity']
            ))
    
    def on_search_change(self, *args):
        """Handle search input changes"""
        search_term = self.search_var.get().strip()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if search_term:
            fans = self.db.search_fans(search_term)
        else:
            fans = self.db.get_all_fans()
        
        # Insert filtered results
        for fan in fans:
            self.tree.insert("", tk.END, values=(
                fan['id'],
                fan['name'],
                fan['airflow'] or "",
                f"${fan['price_wholesale']:.2f}",
                f"${fan['price_retail']:.2f}",
                fan['quantity']
            ))
    
    def add_fan(self):
        """Open dialog to add a new fan"""
        dialog = FanDialog(self.root, "Add Fan")
        # Wait for dialog to close
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            try:
                self.db.add_fan(**dialog.result)
                # Clear search to show all fans including the new one
                self.search_var.set("")
                self.refresh_table()
                messagebox.showinfo("Success", "Fan added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add fan: {str(e)}")
    
    def edit_fan(self):
        """Open dialog to edit selected fan"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a fan to edit.")
            return
        
        item = self.tree.item(selection[0])
        fan_id = item['values'][0]
        
        fan = self.db.get_fan_by_id(fan_id)
        if not fan:
            messagebox.showerror("Error", "Fan not found.")
            return
        
        dialog = FanDialog(self.root, "Edit Fan", fan)
        # Wait for dialog to close
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            try:
                self.db.update_fan(fan_id, **dialog.result)
                self.refresh_table()
                messagebox.showinfo("Success", "Fan updated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update fan: {str(e)}")
    
    def delete_fan(self):
        """Delete selected fan"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a fan to delete.")
            return
        
        item = self.tree.item(selection[0])
        fan_id = item['values'][0]
        fan_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete '{fan_name}'?"):
            self.db.delete_fan(fan_id)
            self.refresh_table()
            messagebox.showinfo("Success", "Fan deleted successfully!")
    
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
    
    def open_price_list(self):
        """Open price list/inquiry window"""
        PriceListWindow(self.root, self.db)


class FanDialog:
    def __init__(self, parent, title, fan_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
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
        
        # Name
        ttk.Label(form_frame, text="Name *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=fan_data['name'] if fan_data else "")
        ttk.Entry(form_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        # Airflow
        ttk.Label(form_frame, text="Airflow:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.airflow_var = tk.StringVar(value=fan_data['airflow'] if fan_data and fan_data['airflow'] else "")
        ttk.Entry(form_frame, textvariable=self.airflow_var, width=30).grid(row=1, column=1, pady=5)
        
        # Wholesale Price
        ttk.Label(form_frame, text="Wholesale Price *:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.wholesale_var = tk.StringVar(value=str(fan_data['price_wholesale']) if fan_data else "")
        ttk.Entry(form_frame, textvariable=self.wholesale_var, width=30).grid(row=2, column=1, pady=5)
        
        # Retail Price
        ttk.Label(form_frame, text="Retail Price *:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.retail_var = tk.StringVar(value=str(fan_data['price_retail']) if fan_data else "")
        ttk.Entry(form_frame, textvariable=self.retail_var, width=30).grid(row=3, column=1, pady=5)
        
        # Quantity
        ttk.Label(form_frame, text="Quantity *:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar(value=str(fan_data['quantity']) if fan_data else "0")
        ttk.Entry(form_frame, textvariable=self.quantity_var, width=30).grid(row=4, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def save(self):
        """Validate and save form data"""
        name = self.name_var.get().strip()
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
            'airflow': airflow,
            'price_wholesale': price_wholesale,
            'price_retail': price_retail,
            'quantity': qty
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FanInventoryApp(root)
    root.mainloop()

