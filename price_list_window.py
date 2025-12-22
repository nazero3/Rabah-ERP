import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import List, Dict

class PriceListWindow:
    def __init__(self, parent, db):
        self.db = db
        self.selected_fans = []  # List of dicts: {'fan': fan_data, 'quantity': int}
        
        self.window = tk.Toplevel(parent)
        self.window.title("Create Price List / Inquiry")
        self.window.geometry("1200x700")
        self.window.transient(parent)
        
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Price List / Inquiry Generator", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Left panel - Search and available fans
        left_frame = ttk.LabelFrame(main_frame, text="Available Fans", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Available fans treeview
        available_tree_frame = ttk.Frame(left_frame)
        available_tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        available_tree_frame.columnconfigure(0, weight=1)
        available_tree_frame.rowconfigure(0, weight=1)
        
        scrollbar_avail_y = ttk.Scrollbar(available_tree_frame, orient=tk.VERTICAL)
        scrollbar_avail_x = ttk.Scrollbar(available_tree_frame, orient=tk.HORIZONTAL)
        
        self.available_tree = ttk.Treeview(available_tree_frame,
                                           columns=("ID", "Name", "Airflow", "Wholesale", "Retail", "Qty"),
                                           show="headings",
                                           yscrollcommand=scrollbar_avail_y.set,
                                           xscrollcommand=scrollbar_avail_x.set,
                                           height=15)
        
        scrollbar_avail_y.config(command=self.available_tree.yview)
        scrollbar_avail_x.config(command=self.available_tree.xview)
        
        # Configure available tree columns
        self.available_tree.heading("ID", text="ID")
        self.available_tree.heading("Name", text="Name")
        self.available_tree.heading("Airflow", text="Airflow")
        self.available_tree.heading("Wholesale", text="Wholesale")
        self.available_tree.heading("Retail", text="Retail")
        self.available_tree.heading("Qty", text="Qty")
        
        self.available_tree.column("ID", width=40, anchor=tk.CENTER)
        self.available_tree.column("Name", width=150, anchor=tk.CENTER)
        self.available_tree.column("Airflow", width=100, anchor=tk.CENTER)
        self.available_tree.column("Wholesale", width=80, anchor=tk.CENTER)
        self.available_tree.column("Retail", width=80, anchor=tk.CENTER)
        self.available_tree.column("Qty", width=60, anchor=tk.CENTER)
        
        self.available_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_avail_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_avail_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Add button
        ttk.Button(left_frame, text="Add to Price List →", 
                  command=self.add_to_price_list).grid(row=2, column=0, pady=10)
        
        # Right panel - Price list
        right_frame = ttk.LabelFrame(main_frame, text="Price List / Inquiry", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Info label (price type is now per-item)
        info_frame = ttk.Frame(right_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(info_frame, text="Double-click Price Type or Quantity to edit", 
                 font=("Arial", 9)).pack()
        
        # Price list treeview
        price_list_tree_frame = ttk.Frame(right_frame)
        price_list_tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        price_list_tree_frame.columnconfigure(0, weight=1)
        price_list_tree_frame.rowconfigure(0, weight=1)
        
        scrollbar_list_y = ttk.Scrollbar(price_list_tree_frame, orient=tk.VERTICAL)
        scrollbar_list_x = ttk.Scrollbar(price_list_tree_frame, orient=tk.HORIZONTAL)
        
        self.price_list_tree = ttk.Treeview(price_list_tree_frame,
                                            columns=("Name", "Airflow", "PriceType", "Price", "Qty", "Total"),
                                            show="headings",
                                            yscrollcommand=scrollbar_list_y.set,
                                            xscrollcommand=scrollbar_list_x.set,
                                            height=15)
        
        scrollbar_list_y.config(command=self.price_list_tree.yview)
        scrollbar_list_x.config(command=self.price_list_tree.xview)
        
        # Configure price list tree columns
        self.price_list_tree.heading("Name", text="Name")
        self.price_list_tree.heading("Airflow", text="Airflow")
        self.price_list_tree.heading("PriceType", text="Price Type")
        self.price_list_tree.heading("Price", text="Unit Price")
        self.price_list_tree.heading("Qty", text="Quantity")
        self.price_list_tree.heading("Total", text="Total")
        
        self.price_list_tree.column("Name", width=180, anchor=tk.CENTER)
        self.price_list_tree.column("Airflow", width=130, anchor=tk.CENTER)
        self.price_list_tree.column("PriceType", width=90, anchor=tk.CENTER)
        self.price_list_tree.column("Price", width=90, anchor=tk.CENTER)
        self.price_list_tree.column("Qty", width=70, anchor=tk.CENTER)
        self.price_list_tree.column("Total", width=90, anchor=tk.CENTER)
        
        # Bind double-click to edit quantity or price type
        self.price_list_tree.bind('<Double-1>', self.on_item_double_click)
        
        self.price_list_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_list_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_list_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Buttons frame
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(buttons_frame, text="Remove Selected", 
                  command=self.remove_from_price_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Clear All", 
                  command=self.clear_price_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Export to Word", 
                  command=self.export_to_word).pack(side=tk.LEFT, padx=5)
        
        # Load initial data
        self.refresh_available_fans()
    
    def refresh_available_fans(self):
        """Refresh the available fans list"""
        # Clear existing items
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)
        
        # Get all fans
        search_term = self.search_var.get().strip()
        if search_term:
            fans = self.db.search_fans(search_term)
        else:
            fans = self.db.get_all_fans()
        
        # Insert into treeview
        for fan in fans:
            self.available_tree.insert("", tk.END, values=(
                fan['id'],
                fan['name'],
                fan['airflow'] or "",
                f"${fan['price_wholesale']:.2f}",
                f"${fan['price_retail']:.2f}",
                fan['quantity']
            ))
    
    def on_search_change(self, *args):
        """Handle search input changes"""
        self.refresh_available_fans()
    
    def add_to_price_list(self):
        """Add selected fan to price list"""
        selection = self.available_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a fan to add.")
            return
        
        item = self.available_tree.item(selection[0])
        fan_id = item['values'][0]
        
        # Check if already in price list
        if any(item_data['fan']['id'] == fan_id for item_data in self.selected_fans):
            messagebox.showinfo("Already Added", "This fan is already in the price list.")
            return
        
        # Get fan data
        fan = self.db.get_fan_by_id(fan_id)
        if fan:
            # Ask user to select price type for this item
            price_type = self.select_price_type_dialog(fan['name'])
            if price_type is None:
                return  # User cancelled
            
            # Add with default quantity of 1 and selected price type
            self.selected_fans.append({
                'fan': fan, 
                'quantity': 1,
                'price_type': price_type
            })
            self.update_price_list()
    
    def remove_from_price_list(self):
        """Remove selected fan from price list"""
        selection = self.price_list_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a fan to remove.")
            return
        
        item = self.price_list_tree.item(selection[0])
        fan_name = item['values'][0]
        
        # Remove from selected fans
        self.selected_fans = [f for f in self.selected_fans if f['fan']['name'] != fan_name]
        self.update_price_list()
    
    def select_price_type_dialog(self, fan_name):
        """Dialog to select price type for an item"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Select Price Type")
        dialog.geometry("300x150")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        result = {'price_type': None}
        
        ttk.Label(dialog, text=f"Select price type for:\n{fan_name}", 
                 font=("Arial", 10)).pack(pady=10)
        
        price_type_var = tk.StringVar(value="retail")
        
        frame = ttk.Frame(dialog)
        frame.pack(pady=10)
        
        ttk.Radiobutton(frame, text="Retail", variable=price_type_var, 
                       value="retail").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(frame, text="Wholesale", variable=price_type_var, 
                       value="wholesale").pack(side=tk.LEFT, padx=10)
        
        def save():
            result['price_type'] = price_type_var.get()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="OK", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)
        
        self.window.wait_window(dialog)
        return result['price_type']
    
    def on_item_double_click(self, event):
        """Handle double-click on price list item"""
        selection = self.price_list_tree.selection()
        if not selection:
            return
        
        item = self.price_list_tree.item(selection[0])
        fan_name = item['values'][0]
        column = self.price_list_tree.identify_column(event.x)
        
        # Find the item in selected_fans
        for item_data in self.selected_fans:
            if item_data['fan']['name'] == fan_name:
                # Column indices: Name=#1, Airflow=#2, PriceType=#3, Price=#4, Qty=#5, Total=#6
                # Values array: Name=0, Airflow=1, PriceType=2, Price=3, Qty=4, Total=5
                if column == '#3':  # PriceType column
                    # Edit price type
                    new_price_type = self.select_price_type_dialog(fan_name)
                    if new_price_type is not None:
                        item_data['price_type'] = new_price_type
                        self.update_price_list()
                elif column == '#5':  # Quantity column
                    # Edit quantity
                    current_qty = item['values'][4]
                    new_qty = simpledialog.askinteger("Edit Quantity", 
                                                      f"Enter quantity for {fan_name}:",
                                                      initialvalue=current_qty,
                                                      minvalue=1,
                                                      parent=self.window)
                    if new_qty is not None:
                        item_data['quantity'] = new_qty
                        self.update_price_list()
                break
    
    def clear_price_list(self):
        """Clear all fans from price list"""
        if self.selected_fans and messagebox.askyesno("Confirm Clear", 
                                                      "Clear all items from price list?"):
            self.selected_fans = []
            self.update_price_list()
    
    def update_price_list(self):
        """Update the price list display"""
        # Clear existing items
        for item in self.price_list_tree.get_children():
            self.price_list_tree.delete(item)
        
        # Insert selected fans with their individual price types
        for item_data in self.selected_fans:
            fan = item_data['fan']
            qty = item_data['quantity']
            price_type = item_data.get('price_type', 'retail')  # Default to retail if not set
            price = fan['price_retail'] if price_type == 'retail' else fan['price_wholesale']
            total = price * qty
            price_type_label = "Retail" if price_type == 'retail' else "Wholesale"
            self.price_list_tree.insert("", tk.END, values=(
                fan['name'],
                fan['airflow'] or "",
                price_type_label,
                f"${price:.2f}",
                qty,
                f"${total:.2f}"
            ))
    
    def export_to_word(self):
        """Export price list to a Word document matching the company format"""
        if not self.selected_fans:
            messagebox.showwarning("Empty List", "Price list is empty.")
            return
        
        try:
            from docx import Document
            from docx.shared import Inches, Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.oxml.ns import qn
            from docx.oxml import OxmlElement
        except ImportError:
            messagebox.showerror("Error", 
                "python-docx library is required. Please install it using:\n"
                "pip install python-docx")
            return
        
        from tkinter import filedialog
        from datetime import datetime
        
        # Ensure window is active before showing dialogs
        self.window.update()
        self.window.lift()
        self.window.focus_force()
        
        # Get customer name (with parent window to ensure it stays on top)
        customer_name = simpledialog.askstring("Customer Name", 
                                               "Enter customer name (Arabic):",
                                               initialvalue="السيد نبيل حميدان المحترم",
                                               parent=self.window)
        if customer_name is None:
            return  # User cancelled
        
        # Ensure window is still active before next dialog
        self.window.update()
        self.window.lift()
        self.window.focus_force()
        
        # Get date (optional, defaults to today) - with parent window
        date_str = simpledialog.askstring("Date", 
                                         "Enter date (YYYY/MM/DD) or leave blank for today:",
                                         initialvalue=datetime.now().strftime("%Y/%m/%d"),
                                         parent=self.window)
        if date_str is None:
            return  # User cancelled
        if not date_str.strip():
            date_str = datetime.now().strftime("%Y/%m/%d")
        
        # Ensure window is raised before file dialog
        self.window.update()
        self.window.lift()
        self.window.focus_force()
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word documents", "*.docx"), ("All files", "*.*")],
            title="Save Price List",
            parent=self.window
        )
        
        if filename:
            try:
                # Create Word document
                doc = Document()
                
                # Set document-level RTL direction
                # This sets the default text direction for the entire document
                try:
                    settings = doc.settings
                    settings_element = settings._element
                    # Try to set document-level RTL (may not be directly supported)
                    # Instead, we'll set it on all paragraphs and the default style
                except:
                    pass
                
                # Set default paragraph style to RTL
                # This ensures all new paragraphs inherit RTL direction
                try:
                    styles = doc.styles
                    normal_style = styles['Normal']
                    style_element = normal_style._element
                    pPr = style_element.find(qn('w:pPr'))
                    if pPr is None:
                        pPr = OxmlElement('w:pPr')
                        style_element.append(pPr)
                    pPr.set(qn('w:bidi'), '1')
                except:
                    pass
                
                # Set document margins
                sections = doc.sections
                for section in sections:
                    section.top_margin = Inches(0.5)
                    section.bottom_margin = Inches(0.5)
                    section.left_margin = Inches(0.7)
                    section.right_margin = Inches(0.7)
                    
                    # Set section to RTL as well
                    sectPr = section._sectPr
                    pgSz = sectPr.find(qn('w:pgSz'))
                    if pgSz is not None:
                        # Set page layout direction
                        pass  # Page size doesn't need RTL
                    
                    # Set text direction on section
                    sectPr.set(qn('w:bidi'), '1')
                
                # Helper function to ensure paragraph has RTL
                def set_paragraph_rtl(para):
                    """Ensure a paragraph has RTL direction set"""
                    pPr = para._element.get_or_add_pPr()
                    pPr.set(qn('w:bidi'), '1')
                    return para
                
                # ===== HEADER SECTION =====
                # Create header table
                header_table = doc.add_table(rows=1, cols=3)
                header_table.style = 'Table Grid'
                header_table.autofit = False
                
                # Left cell - English company info
                left_cell = header_table.rows[0].cells[0]
                left_cell.width = Inches(3)
                left_para = left_cell.paragraphs[0]
                left_para.add_run("Technical Equipment").bold = True
                left_para.add_run().font.size = Pt(14)
                left_para = left_cell.add_paragraph("Industrial-Domestic")
                left_para = left_cell.add_paragraph("Ventilation")
                left_para = left_cell.add_paragraph()
                left_para.add_run("M. Nazir Rabah").bold = True
                left_para.add_run().font.size = Pt(12)
                left_para = left_cell.add_paragraph("& Sons")
                
                # Center cell - Logo placeholder (red lines would be added manually or via image)
                center_cell = header_table.rows[0].cells[1]
                center_cell.width = Inches(1.5)
                center_para = center_cell.paragraphs[0]
                center_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                center_para.add_run("S&P").bold = True
                center_para.add_run().font.size = Pt(10)
                center_para = center_cell.add_paragraph()
                center_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                center_para.add_run("CHAYSOL").font.size = Pt(8)
                center_para = center_cell.add_paragraph()
                center_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                center_para.add_run("emc").font.size = Pt(7)
                
                # Right cell - Arabic company info
                right_cell = header_table.rows[0].cells[2]
                right_cell.width = Inches(3)
                right_para = right_cell.paragraphs[0]
                right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                # Set RTL properly for Arabic
                pPr = right_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                right_run = right_para.add_run("التجهيزات التقنية")
                right_run.bold = True
                right_run.font.size = Pt(14)
                right_para = right_cell.add_paragraph()
                right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                pPr = right_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                right_para.add_run("توربينات تهوية")
                right_para = right_cell.add_paragraph()
                right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                pPr = right_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                right_para.add_run("منزلية. صناعية")
                right_para = right_cell.add_paragraph()
                right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                pPr = right_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                right_para.add_run("محمد نذير رباح").bold = True
                right_para.add_run().font.size = Pt(12)
                right_para = right_cell.add_paragraph()
                right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                pPr = right_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                right_para.add_run("وأولاده")
                
                # Add spacing
                doc.add_paragraph()
                
                # ===== TITLE SECTION =====
                title_para = doc.add_paragraph()
                title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                # Set RTL properly
                pPr = title_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                title_run = title_para.add_run("عرض سعر")
                title_run.bold = True
                title_run.font.size = Pt(18)
                
                # Salutation (right-aligned Arabic)
                salutation_para = doc.add_paragraph()
                salutation_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                pPr = salutation_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                salutation_para.add_run(customer_name)
                
                doc.add_paragraph()
                
                # ===== PRODUCT TABLE =====
                # Create main product table
                product_table = doc.add_table(rows=1, cols=4)
                product_table.style = 'Table Grid'
                
                # Set table direction to RTL for Arabic layout
                tbl = product_table._element
                tblPr = tbl.tblPr
                if tblPr is None:
                    tblPr = OxmlElement('w:tblPr')
                    tbl.insert(0, tblPr)
                # Set RTL visual order - this makes columns display right-to-left
                tblPr.set(qn('w:bidiVisual'), '1')
                # Also set the table to be right-to-left
                tblPr.set(qn('w:jc'), 'right')  # Right justification for RTL
                
                # Table headers - for RTL, we reverse the order so they display correctly
                # Visual order (right to left): النوع, الإفرادي, عدد, الإجمالي
                # Code order (for RTL table): الإجمالي, عدد, الإفرادي, النوع
                headers = ["الإجمالي", "عدد", "الإفرادي", "النوع"]
                header_cells = product_table.rows[0].cells
                
                # Set column widths - reversed for RTL: الإجمالي, عدد, الإفرادي, النوع
                widths = [Inches(1.2), Inches(0.8), Inches(1.2), Inches(4)]
                
                for i, header_text in enumerate(headers):
                    cell = header_cells[i]
                    cell.width = widths[i]
                    para = cell.paragraphs[0]
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    # Set RTL properly for Arabic headers
                    pPr = para._element.get_or_add_pPr()
                    pPr.set(qn('w:bidi'), '1')
                    run = para.add_run(header_text)
                    run.bold = True
                    run.font.size = Pt(11)
                
                # Add product rows
                grand_total = 0
                for item_data in self.selected_fans:
                    fan = item_data['fan']
                    qty = item_data['quantity']
                    # Use individual price type for each item
                    item_price_type = item_data.get('price_type', 'retail')
                    unit_price = fan['price_retail'] if item_price_type == 'retail' else fan['price_wholesale']
                    total_price = unit_price * qty
                    grand_total += total_price
                    
                    row_cells = product_table.add_row().cells
                    
                    # Column order in code (for RTL): الإجمالي, عدد, الإفرادي, النوع
                    # This displays as: النوع, الإفرادي, عدد, الإجمالي (right to left)
                    
                    # Column 0: الإجمالي (Total) - displays on left in RTL
                    total_cell = row_cells[0]
                    total_para = total_cell.paragraphs[0]
                    total_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    total_para.add_run(f"$ {total_price:.0f}")
                    
                    # Column 1: عدد (Quantity)
                    qty_cell = row_cells[1]
                    qty_para = qty_cell.paragraphs[0]
                    qty_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    qty_para.add_run(str(qty))
                    
                    # Column 2: الإفرادي (Unit Price)
                    price_cell = row_cells[2]
                    price_para = price_cell.paragraphs[0]
                    price_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    price_para.add_run(f"{unit_price:.0f}")
                    
                    # Column 3: النوع (Type/Description) - displays on right in RTL
                    type_cell = row_cells[3]
                    type_para = type_cell.paragraphs[0]
                    type_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    # Set RTL properly
                    pPr = type_para._element.get_or_add_pPr()
                    pPr.set(qn('w:bidi'), '1')
                    type_para.add_run(fan['name'])
                    if fan.get('airflow'):
                        type_para = type_cell.add_paragraph()
                        type_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                        pPr = type_para._element.get_or_add_pPr()
                        pPr.set(qn('w:bidi'), '1')
                        type_para.add_run(f"Airflow: {fan['airflow']}")
                
                doc.add_paragraph()
                
                # ===== FOOTER SECTION =====
                # Notes section
                notes_para = doc.add_paragraph()
                notes_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                pPr = notes_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                notes_run = notes_para.add_run("ملاحظات:")
                notes_run.bold = True
                notes_run.font.size = Pt(11)
                
                note1_para = doc.add_paragraph()
                note1_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                pPr = note1_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                note1_para.add_run("• المحرك الخارجي يتوفر لدينا نوع تشيكي يتم اختيار الاستطاعة المطلوبة على كتالوك التوربين حسب الغزارة والضغط")
                
                note2_para = doc.add_paragraph()
                note2_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                pPr = note2_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                note2_para.add_run("• التسليم أرض الشركة بدمشق")
                
                doc.add_paragraph()
                
                # Contact information
                contact_para = doc.add_paragraph()
                contact_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                contact_para.add_run("DAMASCUS. SYRIA. TEL: (0096311) 2122066-2141283 - FAX: 2122048 - P.O.BOX 32157")
                contact_para.runs[0].font.size = Pt(9)
                
                contact_arabic_para = doc.add_paragraph()
                contact_arabic_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                pPr = contact_arabic_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                contact_arabic_para.add_run("دمشق . برامكة . جانب الهجرة والجوازات - 21220662 / 2141283 - فاكس : 2122048 / ص . ب 32157 - س . ت 12661")
                contact_arabic_para.runs[0].font.size = Pt(9)
                
                # Date
                date_para = doc.add_paragraph()
                date_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                pPr = date_para._element.get_or_add_pPr()
                pPr.set(qn('w:bidi'), '1')
                date_para.add_run(f"مع تحياتنا {date_str}")
                
                # Ensure ALL paragraphs in the document have RTL set
                # This ensures the entire document is RTL by default
                for para in doc.paragraphs:
                    pPr = para._element.get_or_add_pPr()
                    # Set RTL - this makes the paragraph right-to-left
                    pPr.set(qn('w:bidi'), '1')
                
                # Also set RTL on all paragraphs in all tables
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for para in cell.paragraphs:
                                pPr = para._element.get_or_add_pPr()
                                # Set RTL for all table cell paragraphs
                                pPr.set(qn('w:bidi'), '1')
                
                # Save document
                doc.save(filename)
                
                messagebox.showinfo("Success", f"Price list exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
                import traceback
                traceback.print_exc()

