import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
from database import InventoryDB
from price_list_window import PriceListWindow

# Helper function to get resource path (works both as script and as PyInstaller exe)
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



class FanInventoryApp:
    def __init__(self, root):
        self.root = root
        # Load window icon (if available) - works both as script and as PyInstaller exe
        # Note: For Windows taskbar icon, we use iconbitmap with .ico file
        # For window title bar icon, we use iconphoto with PNG/GIF
        try:
            # Try to set .ico file for taskbar icon (Windows)
            icon_ico_path = None
            if os.path.exists('logo.ico'):
                icon_ico_path = 'logo.ico'
            else:
                try:
                    icon_ico_path = resource_path('logo.ico')
                except:
                    pass
            
            if icon_ico_path and os.path.exists(icon_ico_path):
                self.root.iconbitmap(icon_ico_path)  # Sets taskbar and window icon on Windows
            
            # Also try PNG for window icon (cross-platform, fallback)
            icon_png_path = None
            if os.path.exists('logo.png'):
                icon_png_path = 'logo.png'
            else:
                try:
                    icon_png_path = resource_path('logo.png')
                except:
                    pass
            
            if icon_png_path and os.path.exists(icon_png_path):
                icon_image = tk.PhotoImage(file=icon_png_path)
                self.root.iconphoto(False, icon_image)  # Set window icon
        except Exception:
            # Icon file not found or failed to load - continue without icon
            pass
        self.root.title("رباح للتهوية")
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
        self.title_label = ttk.Label(main_frame, text="ادارة المخزون", 
                               font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        # Product type selection
        product_frame = ttk.LabelFrame(main_frame, text="نوع المنتج", padding="5")
        product_frame.grid(row=1, column=0, columnspan=3, pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.product_type_var = tk.StringVar(value="fans")
        ttk.Radiobutton(product_frame, text="مراوح", variable=self.product_type_var, 
                       value="fans", command=self.switch_product_type).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(product_frame, text="صاج", variable=self.product_type_var, 
                       value="sheet_metal", command=self.switch_product_type).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(product_frame, text="فلكسيبل", variable=self.product_type_var, 
                       value="flexible", command=self.switch_product_type).pack(side=tk.LEFT, padx=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.N), padx=(0, 10))
        
        self.add_btn = ttk.Button(buttons_frame, text="إضافة", command=self.add_item, 
                  width=20)
        self.add_btn.pack(pady=5, fill=tk.X)
        
        self.edit_btn = ttk.Button(buttons_frame, text="تعديل", command=self.edit_item, 
                  width=20)
        self.edit_btn.pack(pady=5, fill=tk.X)
        
        self.delete_btn = ttk.Button(buttons_frame, text="حذف", command=self.delete_item, 
                  width=20)
        self.delete_btn.pack(pady=5, fill=tk.X)
        
        self.view_datasheet_btn = ttk.Button(buttons_frame, text="عرض الكتالوج", 
                  command=self.view_datasheet, width=20)
        # Initially hide - will be shown only for fans
        # self.view_datasheet_btn.pack(pady=5, fill=tk.X)
        
        ttk.Button(buttons_frame, text="تحديث", command=self.refresh_table, 
                  width=20).pack(pady=5, fill=tk.X)
        ttk.Button(buttons_frame, text="إنشاء عرض سعر", 
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
        self.toggle_search_btn = ttk.Button(search_container, text="🔍 إظهار البحث", 
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
        
        # Bind double-click event to view datasheet (for fans)
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
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
        
        # Reverse column order for RTL display
        if self.current_product_type == "fans":
            columns = ("Quantity", "Retail", "Wholesale", "Airflow", "Name")
            headings = ("كمية", "مفرق", "جملة", "غزارة", "نوع")
            widths = (100, 120, 120, 150, 200)
        elif self.current_product_type == "sheet_metal":
            columns = ("Extra", "Cost", "Measurement", "Dimensions", "Thickness")
            headings = ("عزل و ارموفلكس", "اجور", "القياس", "ابعاد الصندوق", "سماكة الصاج")
            widths = (150, 100, 100, 120, 120)
        else:  # flexible
            columns = ("Meter", "Collection", "Diameter")
            headings = ("متر", "ربطة", "قطر")
            widths = (100, 150, 120)
        
        # Configure columns with RTL alignment
        self.tree['columns'] = columns
        for i, (col, heading, width) in enumerate(zip(columns, headings, widths)):
            self.tree.heading(col, text=heading, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=width, anchor=tk.E)  # Right alignment for RTL
    
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
        
        # Update button labels (Arabic)
        labels = {
            "fans": ("إضافة مروحة", "تعديل مروحة", "حذف مروحة"),
            "sheet_metal": ("إضافة صاج", "تعديل صاج", "حذف صاج"),
            "flexible": ("إضافة فلكسيبل", "تعديل فلكسيبل", "حذف فلكسيبل")
        }
        self.add_btn.config(text=labels[self.current_product_type][0])
        self.edit_btn.config(text=labels[self.current_product_type][1])
        self.delete_btn.config(text=labels[self.current_product_type][2])
        
        # Show/hide view datasheet button (only for fans)
        if self.current_product_type == "fans":
            self.view_datasheet_btn.pack(pady=5, fill=tk.X)
        else:
            self.view_datasheet_btn.pack_forget()
        
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
        
        # Insert into treeview based on product type (RTL order - reversed)
        # Use iid to store the item ID for edit/delete operations
        for item in items:
            if self.current_product_type == "fans":
                self.tree.insert("", tk.END, iid=str(item['id']), values=(
                    item['quantity'],
                    f"${item['price_retail']:.2f}",
                    f"${item['price_wholesale']:.2f}",
                    item.get('airflow') or "",
                    item['name']
                ))
            elif self.current_product_type == "sheet_metal":
                self.tree.insert("", tk.END, iid=str(item['id']), values=(
                    item.get('extra') or "",
                    f"${item.get('cost', 0):.2f}",
                    item.get('measurement') or "",
                    item.get('dimensions') or "",
                    item.get('thickness') or ""
                ))
            else:  # flexible
                self.tree.insert("", tk.END, iid=str(item['id']), values=(
                    f"${item.get('meter', 0):.2f}",
                    item.get('collection') or "",
                    item.get('diameter') or ""
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
                "نوع": "name",
                "غزارة": "airflow",
                "جملة": "price",
                "مفرق": "price",
                "كمية": "quantity"
            }
        elif self.current_product_type == "sheet_metal":
            column_map = {
                "سماكة الصاج": "thickness",
                "ابعاد الصندوق": "thickness",  # Fallback to thickness for sorting
                "القياس": "thickness",  # Fallback to thickness for sorting
                "اجور": "price",
                "عزل و ارموفلكس": "thickness"  # Fallback to thickness for sorting
            }
        else:  # flexible
            column_map = {
                "قطر": "diameter",
                "ربطة": "diameter",  # Fallback to diameter for sorting
                "متر": "price"
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
            messagebox.showinfo("معلومات", "ميزة عرض السعر متاحة حالياً للمراوح فقط.")
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
                    msg = "تمت إضافة المروحة بنجاح!"
                elif self.current_product_type == "sheet_metal":
                    self.db.add_sheet_metal(**dialog.result)
                    msg = "تمت إضافة الصاج بنجاح!"
                else:  # flexible
                    self.db.add_flexible(**dialog.result)
                    msg = "تمت إضافة الفلكسيبل بنجاح!"
                
                # Clear search to show all items including the new one
                self.search_var.set("")
                self.refresh_table()
                messagebox.showinfo("نجح", msg)
            except Exception as e:
                messagebox.showerror("خطأ", f"فشلت إضافة العنصر: {str(e)}")
    
    def edit_item(self):
        """Open dialog to edit selected item"""
        selection = self.tree.selection()
        if not selection:
            product_name = {"fans": "مروحة", "sheet_metal": "صاج", "flexible": "فلكسيبل"}
            messagebox.showwarning("لا يوجد تحديد", f"يرجى تحديد {product_name[self.current_product_type]} للتعديل.")
            return
        
        # Get item ID from the treeview item identifier (iid)
        item_id = int(selection[0])
        
        # Get item data
        if self.current_product_type == "fans":
            item_data = self.db.get_fan_by_id(item_id)
            if not item_data:
                messagebox.showerror("خطأ", "لم يتم العثور على العنصر.")
                return
            dialog = FanDialog(self.root, "Edit Fan", item_data)
        elif self.current_product_type == "sheet_metal":
            item_data = self.db.get_sheet_metal_by_id(item_id)
            if not item_data:
                messagebox.showerror("خطأ", "لم يتم العثور على العنصر.")
                return
            dialog = SheetMetalDialog(self.root, "Edit Sheet Metal", item_data)
        else:  # flexible
            item_data = self.db.get_flexible_by_id(item_id)
            if not item_data:
                messagebox.showerror("خطأ", "لم يتم العثور على العنصر.")
                return
            dialog = FlexibleDialog(self.root, "Edit Flexible", item_data)
        
        # Wait for dialog to close
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            try:
                if self.current_product_type == "fans":
                    self.db.update_fan(item_id, **dialog.result)
                    msg = "تم تحديث المروحة بنجاح!"
                elif self.current_product_type == "sheet_metal":
                    # Remove quantity if present (for backward compatibility)
                    result = {k: v for k, v in dialog.result.items() if k != 'quantity'}
                    self.db.update_sheet_metal(item_id, **result)
                    msg = "تم تحديث الصاج بنجاح!"
                else:  # flexible
                    self.db.update_flexible(item_id, **dialog.result)
                    msg = "تم تحديث الفلكسيبل بنجاح!"
                
                self.refresh_table()
                messagebox.showinfo("نجح", msg)
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل تحديث العنصر: {str(e)}")
    
    def on_item_double_click(self, event):
        """Handle double-click on treeview item"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Only handle double-click for fans
        if self.current_product_type != "fans":
            return
        
        # Get item ID from the treeview item identifier (iid)
        item_id = int(selection[0])
        
        # Get fan data
        item_data = self.db.get_fan_by_id(item_id)
        if not item_data:
            return
        
        # View datasheet
        self._open_catalog_file(item_data)
    
    def view_datasheet(self):
        """View the catalog/datasheet for selected fan"""
        if self.current_product_type != "fans":
            return
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("لا يوجد تحديد", "يرجى تحديد مروحة لعرض الكتالوج.")
            return
        
        # Get item ID from the treeview item identifier (iid)
        item_id = int(selection[0])
        
        # Get fan data
        item_data = self.db.get_fan_by_id(item_id)
        if not item_data:
            messagebox.showerror("خطأ", "لم يتم العثور على العنصر.")
            return
        
        self._open_catalog_file(item_data)
    
    def _open_catalog_file(self, item_data):
        """Open catalog file for a fan item"""
        catalog_path = item_data.get('catalog_file_path')
        if not catalog_path:
            messagebox.showinfo("لا يوجد كتالوج", "لا يوجد ملف كتالوج مرتبط بهذه المروحة.\n\nيرجى تعديل المروحة واختيار ملف الكتالوج.")
            return
        
        # Check if file exists
        import os
        if not os.path.exists(catalog_path):
            messagebox.showerror("ملف غير موجود", 
                f"ملف الكتالوج غير موجود:\n{catalog_path}\n\nيرجى التحقق من مسار الملف في تفاصيل المروحة.")
            return
        
        # Open the file using the default system application
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(catalog_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', catalog_path])
            else:  # Linux
                subprocess.run(['xdg-open', catalog_path])
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل فتح ملف الكتالوج:\n{str(e)}")
    
    def delete_item(self):
        """Delete selected item"""
        selection = self.tree.selection()
        if not selection:
            product_name = {"fans": "مروحة", "sheet_metal": "صاج", "flexible": "فلكسيبل"}
            messagebox.showwarning("لا يوجد تحديد", f"يرجى تحديد {product_name[self.current_product_type]} للحذف.")
            return
        
        # Get item ID from the treeview item identifier (iid)
        item_id = int(selection[0])
        item = self.tree.item(selection[0])
        # In RTL order, name is last column
        if self.current_product_type == "fans":
            item_name = item['values'][4]  # Name is last in RTL
        elif self.current_product_type == "sheet_metal":
            item_name = item['values'][4]  # Thickness is last in RTL
        else:  # flexible
            item_name = item['values'][2]  # Diameter is last in RTL
        
        if messagebox.askyesno("تأكيد الحذف", 
                              f"هل أنت متأكد أنك تريد حذف '{item_name}'؟"):
            try:
                if self.current_product_type == "fans":
                    self.db.delete_fan(item_id)
                elif self.current_product_type == "sheet_metal":
                    self.db.delete_sheet_metal(item_id)
                else:  # flexible
                    self.db.delete_flexible(item_id)
                
                self.refresh_table()
                messagebox.showinfo("نجح", "تم حذف العنصر بنجاح!")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل حذف العنصر: {str(e)}")
    
    def toggle_search(self):
        """Toggle search bar visibility"""
        if self.search_visible:
            # Hide search bar
            self.search_frame.grid_remove()
            self.toggle_search_btn.config(text="🔍 إظهار البحث")
            self.search_visible = False
            # Clear search when hiding
            self.search_var.set("")
            self.refresh_table()
        else:
            # Show search bar
            self.search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
            self.toggle_search_btn.config(text="✖ إخفاء البحث")
            self.search_visible = True
            # Focus on search entry
            self.search_entry.focus()
    


class FanDialog:
    def __init__(self, parent, title, fan_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        # Translate title to Arabic
        title_ar = "إضافة مروحة" if "Add" in title else "تعديل مروحة"
        self.dialog.title(title_ar)
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Form frame with RTL layout
        form_frame = ttk.Frame(self.dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        form_frame.columnconfigure(0, weight=1)  # Entry column
        form_frame.columnconfigure(1, weight=0)  # Label column
        
        # Helper function to bind keyboard shortcuts to entry widgets
        def bind_shortcuts(widget):
            widget.bind('<Control-v>', lambda e: widget.event_generate('<<Paste>>'))
            widget.bind('<Control-c>', lambda e: widget.event_generate('<<Copy>>'))
            widget.bind('<Control-x>', lambda e: widget.event_generate('<<Cut>>'))
            widget.bind('<Control-a>', lambda e: widget.select_range(0, tk.END))
        
        # RTL Layout: Entry on left (column 0), Label on right (column 1)
        # Name
        self.name_var = tk.StringVar(value=fan_data['name'] if fan_data else "")
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(name_entry)
        ttk.Label(form_frame, text=":نوع *").grid(row=0, column=1, sticky=tk.E, pady=5)
        
        # Description
        self.description_var = tk.StringVar(value=fan_data.get('description', '') if fan_data else "")
        description_entry = ttk.Entry(form_frame, textvariable=self.description_var, width=30)
        description_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(description_entry)
        ttk.Label(form_frame, text=":الوصف").grid(row=1, column=1, sticky=tk.E, pady=5)
        
        # Airflow
        self.airflow_var = tk.StringVar(value=fan_data['airflow'] if fan_data and fan_data.get('airflow') else "")
        airflow_entry = ttk.Entry(form_frame, textvariable=self.airflow_var, width=30)
        airflow_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(airflow_entry)
        ttk.Label(form_frame, text=":غزارة").grid(row=2, column=1, sticky=tk.E, pady=5)
        
        # Wholesale Price
        self.wholesale_var = tk.StringVar(value=str(fan_data['price_wholesale']) if fan_data else "")
        wholesale_entry = ttk.Entry(form_frame, textvariable=self.wholesale_var, width=30)
        wholesale_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(wholesale_entry)
        ttk.Label(form_frame, text=":سعر الجملة *").grid(row=3, column=1, sticky=tk.E, pady=5)
        
        # Retail Price
        self.retail_var = tk.StringVar(value=str(fan_data['price_retail']) if fan_data else "")
        retail_entry = ttk.Entry(form_frame, textvariable=self.retail_var, width=30)
        retail_entry.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(retail_entry)
        ttk.Label(form_frame, text=":سعر المفرق *").grid(row=4, column=1, sticky=tk.E, pady=5)
        
        # Quantity
        self.quantity_var = tk.StringVar(value=str(fan_data['quantity']) if fan_data else "0")
        quantity_entry = ttk.Entry(form_frame, textvariable=self.quantity_var, width=30)
        quantity_entry.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(quantity_entry)
        ttk.Label(form_frame, text=":الكمية *").grid(row=5, column=1, sticky=tk.E, pady=5)
        
        # Catalog File Path (RTL layout)
        catalog_frame = ttk.Frame(form_frame)
        catalog_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        catalog_frame.columnconfigure(0, weight=1)
        
        self.catalog_path_var = tk.StringVar(value=fan_data.get('catalog_file_path', '') if fan_data else "")
        catalog_entry = ttk.Entry(catalog_frame, textvariable=self.catalog_path_var, width=25)
        catalog_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(5, 0))
        bind_shortcuts(catalog_entry)
        
        def browse_catalog_file():
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="اختر ملف الكتالوج",
                filetypes=[
                    ("All supported", "*.pdf;*.jpg;*.jpeg;*.png;*.docx"),
                    ("PDF files", "*.pdf"),
                    ("Image files", "*.jpg;*.jpeg;*.png"),
                    ("Word files", "*.docx"),
                    ("All files", "*.*")
                ],
                parent=self.dialog
            )
            if filename:
                self.catalog_path_var.set(filename)
        
        ttk.Button(catalog_frame, text="تصفح", command=browse_catalog_file, width=10).grid(row=0, column=1)
        ttk.Label(form_frame, text=":ملف الكتالوج").grid(row=6, column=1, sticky=tk.E, pady=5)
        
        # Buttons (RTL: Cancel on right, Save on left)
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="إلغاء", command=self.cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="حفظ", command=self.save).pack(side=tk.RIGHT, padx=5)
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def save(self):
        """Validate and save form data"""
        name = self.name_var.get().strip()
        description = self.description_var.get().strip() or None
        airflow = self.airflow_var.get().strip() or None
        wholesale = self.wholesale_var.get().strip()
        retail = self.retail_var.get().strip()
        quantity = self.quantity_var.get().strip()
        catalog_path = self.catalog_path_var.get().strip() or None
        
        # Validation (Arabic messages)
        if not name:
            messagebox.showerror("خطأ في التحقق", "النوع مطلوب.")
            return
        
        try:
            price_wholesale = float(wholesale)
            if price_wholesale < 0:
                raise ValueError("السعر لا يمكن أن يكون سالباً")
        except ValueError:
            messagebox.showerror("خطأ في التحقق", "سعر الجملة غير صحيح.")
            return
        
        try:
            price_retail = float(retail)
            if price_retail < 0:
                raise ValueError("السعر لا يمكن أن يكون سالباً")
        except ValueError:
            messagebox.showerror("خطأ في التحقق", "سعر المفرق غير صحيح.")
            return
        
        try:
            qty = int(quantity)
            if qty < 0:
                raise ValueError("الكمية لا يمكن أن تكون سالبة")
        except ValueError:
            messagebox.showerror("خطأ في التحقق", "الكمية غير صحيحة.")
            return
        
        catalog_path = self.catalog_path_var.get().strip() or None
        
        self.result = {
            'name': name,
            'description': description,
            'airflow': airflow,
            'price_wholesale': price_wholesale,
            'price_retail': price_retail,
            'quantity': qty,
            'catalog_file_path': catalog_path
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


class SheetMetalDialog:
    def __init__(self, parent, title, item_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        # Translate title to Arabic
        title_ar = "إضافة صاج" if "Add" in title else "تعديل صاج"
        self.dialog.title(title_ar)
        self.dialog.geometry("450x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Form frame with RTL layout
        form_frame = ttk.Frame(self.dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        form_frame.columnconfigure(0, weight=1)  # Entry column
        form_frame.columnconfigure(1, weight=0)  # Label column
        
        # Helper function to bind keyboard shortcuts to entry widgets
        def bind_shortcuts(widget):
            widget.bind('<Control-v>', lambda e: widget.event_generate('<<Paste>>'))
            widget.bind('<Control-c>', lambda e: widget.event_generate('<<Copy>>'))
            widget.bind('<Control-x>', lambda e: widget.event_generate('<<Cut>>'))
            widget.bind('<Control-a>', lambda e: widget.select_range(0, tk.END))
        
        # RTL Layout: Entry on left (column 0), Label on right (column 1)
        # Thickness
        self.thickness_var = tk.StringVar(value=item_data.get('thickness', '') if item_data else "")
        thickness_entry = ttk.Entry(form_frame, textvariable=self.thickness_var, width=30)
        thickness_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(thickness_entry)
        ttk.Label(form_frame, text=":سماكة الصاج").grid(row=0, column=1, sticky=tk.E, pady=5)
        
        # Dimensions
        self.dimensions_var = tk.StringVar(value=item_data.get('dimensions', '') if item_data else "")
        dimensions_entry = ttk.Entry(form_frame, textvariable=self.dimensions_var, width=30)
        dimensions_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(dimensions_entry)
        ttk.Label(form_frame, text=":ابعاد الصندوق").grid(row=1, column=1, sticky=tk.E, pady=5)
        
        # Measurement
        self.measurement_var = tk.StringVar(value=item_data.get('measurement', '') if item_data else "")
        measurement_entry = ttk.Entry(form_frame, textvariable=self.measurement_var, width=30)
        measurement_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(measurement_entry)
        ttk.Label(form_frame, text=":القياس").grid(row=2, column=1, sticky=tk.E, pady=5)
        
        # Cost
        self.cost_var = tk.StringVar(value=str(item_data.get('cost', '')) if item_data else "")
        cost_entry = ttk.Entry(form_frame, textvariable=self.cost_var, width=30)
        cost_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(cost_entry)
        ttk.Label(form_frame, text=":اجور *").grid(row=3, column=1, sticky=tk.E, pady=5)
        
        # Extra
        self.extra_var = tk.StringVar(value=item_data.get('extra', '') if item_data else "")
        extra_entry = ttk.Entry(form_frame, textvariable=self.extra_var, width=30)
        extra_entry.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(extra_entry)
        ttk.Label(form_frame, text=":عزل و ارموفلكس").grid(row=4, column=1, sticky=tk.E, pady=5)
        
        # Buttons (RTL: Cancel on right, Save on left)
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="إلغاء", command=self.cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="حفظ", command=self.save).pack(side=tk.RIGHT, padx=5)
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def save(self):
        """Validate and save form data"""
        thickness = self.thickness_var.get().strip() or None
        dimensions = self.dimensions_var.get().strip() or None
        measurement = self.measurement_var.get().strip() or None
        cost = self.cost_var.get().strip()
        extra = self.extra_var.get().strip() or None
        
        # Validation (Arabic messages)
        try:
            cost_value = float(cost)
            if cost_value < 0:
                raise ValueError("الأجور لا يمكن أن تكون سالبة")
        except ValueError:
            messagebox.showerror("خطأ في التحقق", "الأجور غير صحيحة.")
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
        # Translate title to Arabic
        title_ar = "إضافة فلكسيبل" if "Add" in title else "تعديل فلكسيبل"
        self.dialog.title(title_ar)
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Form frame with RTL layout
        form_frame = ttk.Frame(self.dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        form_frame.columnconfigure(0, weight=1)  # Entry column
        form_frame.columnconfigure(1, weight=0)  # Label column
        
        # Helper function to bind keyboard shortcuts to entry widgets
        def bind_shortcuts(widget):
            widget.bind('<Control-v>', lambda e: widget.event_generate('<<Paste>>'))
            widget.bind('<Control-c>', lambda e: widget.event_generate('<<Copy>>'))
            widget.bind('<Control-x>', lambda e: widget.event_generate('<<Cut>>'))
            widget.bind('<Control-a>', lambda e: widget.select_range(0, tk.END))
        
        # RTL Layout: Entry on left (column 0), Label on right (column 1)
        # Description
        self.description_var = tk.StringVar(value=item_data.get('description', '') if item_data else "")
        description_entry = ttk.Entry(form_frame, textvariable=self.description_var, width=30)
        description_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(description_entry)
        ttk.Label(form_frame, text=":الوصف").grid(row=0, column=1, sticky=tk.E, pady=5)
        
        # Diameter
        self.diameter_var = tk.StringVar(value=item_data.get('diameter', '') if item_data else "")
        diameter_entry = ttk.Entry(form_frame, textvariable=self.diameter_var, width=30)
        diameter_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(diameter_entry)
        ttk.Label(form_frame, text=":قطر").grid(row=1, column=1, sticky=tk.E, pady=5)
        
        # Collection
        self.collection_var = tk.StringVar(value=item_data.get('collection', '') if item_data else "")
        collection_entry = ttk.Entry(form_frame, textvariable=self.collection_var, width=30)
        collection_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(collection_entry)
        ttk.Label(form_frame, text=":ربطة").grid(row=2, column=1, sticky=tk.E, pady=5)
        
        # Meter
        self.meter_var = tk.StringVar(value=str(item_data.get('meter', '')) if item_data else "")
        meter_entry = ttk.Entry(form_frame, textvariable=self.meter_var, width=30)
        meter_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        bind_shortcuts(meter_entry)
        ttk.Label(form_frame, text=":متر *").grid(row=3, column=1, sticky=tk.E, pady=5)
        
        # Buttons (RTL: Cancel on right, Save on left)
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="إلغاء", command=self.cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="حفظ", command=self.save).pack(side=tk.RIGHT, padx=5)
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def save(self):
        """Validate and save form data"""
        description = self.description_var.get().strip() or None
        diameter = self.diameter_var.get().strip() or None
        collection = self.collection_var.get().strip() or None
        meter = self.meter_var.get().strip()
        
        # Validation (Arabic messages)
        try:
            meter_value = float(meter)
            if meter_value < 0:
                raise ValueError("المتر لا يمكن أن يكون سالباً")
        except ValueError:
            messagebox.showerror("خطأ في التحقق", "قيمة المتر غير صحيحة.")
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

