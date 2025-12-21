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
        
        # Price list type selection
        type_frame = ttk.Frame(right_frame)
        type_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(type_frame, text="Price Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.price_type_var = tk.StringVar(value="retail")
        ttk.Radiobutton(type_frame, text="Retail", variable=self.price_type_var, 
                       value="retail", command=self.update_price_list).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Wholesale", variable=self.price_type_var, 
                       value="wholesale", command=self.update_price_list).pack(side=tk.LEFT, padx=5)
        
        # Price list treeview
        price_list_tree_frame = ttk.Frame(right_frame)
        price_list_tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        price_list_tree_frame.columnconfigure(0, weight=1)
        price_list_tree_frame.rowconfigure(0, weight=1)
        
        scrollbar_list_y = ttk.Scrollbar(price_list_tree_frame, orient=tk.VERTICAL)
        scrollbar_list_x = ttk.Scrollbar(price_list_tree_frame, orient=tk.HORIZONTAL)
        
        self.price_list_tree = ttk.Treeview(price_list_tree_frame,
                                            columns=("Name", "Airflow", "Price", "Qty", "Total"),
                                            show="headings",
                                            yscrollcommand=scrollbar_list_y.set,
                                            xscrollcommand=scrollbar_list_x.set,
                                            height=15)
        
        scrollbar_list_y.config(command=self.price_list_tree.yview)
        scrollbar_list_x.config(command=self.price_list_tree.xview)
        
        # Configure price list tree columns
        self.price_list_tree.heading("Name", text="Name")
        self.price_list_tree.heading("Airflow", text="Airflow")
        self.price_list_tree.heading("Price", text="Unit Price")
        self.price_list_tree.heading("Qty", text="Quantity")
        self.price_list_tree.heading("Total", text="Total")
        
        self.price_list_tree.column("Name", width=200, anchor=tk.CENTER)
        self.price_list_tree.column("Airflow", width=150, anchor=tk.CENTER)
        self.price_list_tree.column("Price", width=100, anchor=tk.CENTER)
        self.price_list_tree.column("Qty", width=80, anchor=tk.CENTER)
        self.price_list_tree.column("Total", width=100, anchor=tk.CENTER)
        
        # Bind double-click to edit quantity
        self.price_list_tree.bind('<Double-1>', self.edit_quantity)
        
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
            # Add with default quantity of 1
            self.selected_fans.append({'fan': fan, 'quantity': 1})
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
    
    def edit_quantity(self, event):
        """Edit quantity for selected item"""
        selection = self.price_list_tree.selection()
        if not selection:
            return
        
        item = self.price_list_tree.item(selection[0])
        fan_name = item['values'][0]
        current_qty = item['values'][3]
        
        # Find the item in selected_fans
        for item_data in self.selected_fans:
            if item_data['fan']['name'] == fan_name:
                # Ask for new quantity
                new_qty = simpledialog.askinteger("Edit Quantity", 
                                                  f"Enter quantity for {fan_name}:",
                                                  initialvalue=current_qty,
                                                  minvalue=1)
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
        
        # Get price type
        price_type = self.price_type_var.get()
        
        # Insert selected fans
        for item_data in self.selected_fans:
            fan = item_data['fan']
            qty = item_data['quantity']
            price = fan['price_retail'] if price_type == 'retail' else fan['price_wholesale']
            total = price * qty
            self.price_list_tree.insert("", tk.END, values=(
                fan['name'],
                fan['airflow'] or "",
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
        
        # Get customer name
        customer_name = simpledialog.askstring("Customer Name", 
                                               "Enter customer name (Arabic):",
                                               initialvalue="السيد نبيل حميدان المحترم")
        if customer_name is None:
            return  # User cancelled
        
        # Get date (optional, defaults to today)
        date_str = simpledialog.askstring("Date", 
                                         "Enter date (YYYY/MM/DD) or leave blank for today:",
                                         initialvalue=datetime.now().strftime("%Y/%m/%d"))
        if date_str is None:
            return  # User cancelled
        if not date_str.strip():
            date_str = datetime.now().strftime("%Y/%m/%d")
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word documents", "*.docx"), ("All files", "*.*")],
            title="Save Price List"
        )
        
        if filename:
            try:
                price_type = self.price_type_var.get()
                
                # Create Word document
                doc = Document()
                
                # Set document margins
                sections = doc.sections
                for section in sections:
                    section.top_margin = Inches(0.5)
                    section.bottom_margin = Inches(0.5)
                    section.left_margin = Inches(0.7)
                    section.right_margin = Inches(0.7)
                
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
                right_run = right_para.add_run("التجهيزات التقنية")
                right_run.bold = True
                right_run.font.size = Pt(14)
                # Set RTL for Arabic
                right_para._element.set(qn('w:rtl'), 'true')
                right_para = right_cell.add_paragraph()
                right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                right_para._element.set(qn('w:rtl'), 'true')
                right_para.add_run("توربينات تهوية")
                right_para = right_cell.add_paragraph()
                right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                right_para._element.set(qn('w:rtl'), 'true')
                right_para.add_run("منزلية. صناعية")
                right_para = right_cell.add_paragraph()
                right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                right_para._element.set(qn('w:rtl'), 'true')
                right_para.add_run("محمد نذير رباح").bold = True
                right_para.add_run().font.size = Pt(12)
                right_para = right_cell.add_paragraph()
                right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                right_para._element.set(qn('w:rtl'), 'true')
                right_para.add_run("وأولاده")
                
                # Add spacing
                doc.add_paragraph()
                
                # ===== TITLE SECTION =====
                title_para = doc.add_paragraph()
                title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                title_run = title_para.add_run("عرض سعر")
                title_run.bold = True
                title_run.font.size = Pt(18)
                title_para._element.set(qn('w:rtl'), 'true')
                
                # Salutation (right-aligned Arabic)
                salutation_para = doc.add_paragraph()
                salutation_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                salutation_para._element.set(qn('w:rtl'), 'true')
                salutation_para.add_run(customer_name)
                
                doc.add_paragraph()
                
                # ===== PRODUCT TABLE =====
                # Create main product table
                product_table = doc.add_table(rows=1, cols=4)
                product_table.style = 'Table Grid'
                
                # Table headers (order: النوع, الإفرادي, عدد, الإجمالي from left to right)
                # This will display correctly for Arabic RTL layout
                headers = ["النوع", "الإفرادي", "عدد", "الإجمالي"]
                header_cells = product_table.rows[0].cells
                
                # Set column widths: النوع (widest), الإفرادي, عدد, الإجمالي
                widths = [Inches(4), Inches(1.2), Inches(0.8), Inches(1.2)]
                
                for i, header_text in enumerate(headers):
                    cell = header_cells[i]
                    cell.width = widths[i]
                    para = cell.paragraphs[0]
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    para._element.set(qn('w:rtl'), 'true')
                    run = para.add_run(header_text)
                    run.bold = True
                    run.font.size = Pt(11)
                
                # Add product rows
                grand_total = 0
                for item_data in self.selected_fans:
                    fan = item_data['fan']
                    qty = item_data['quantity']
                    unit_price = fan['price_retail'] if price_type == 'retail' else fan['price_wholesale']
                    total_price = unit_price * qty
                    grand_total += total_price
                    
                    row_cells = product_table.add_row().cells
                    
                    # Column order: النوع, الإفرادي, عدد, الإجمالي
                    
                    # Column 0: النوع (Type/Description) - Product name and airflow
                    type_cell = row_cells[0]
                    type_para = type_cell.paragraphs[0]
                    type_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    type_para._element.set(qn('w:rtl'), 'true')
                    type_para.add_run(fan['name'])
                    if fan.get('airflow'):
                        type_para = type_cell.add_paragraph()
                        type_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                        type_para._element.set(qn('w:rtl'), 'true')
                        type_para.add_run(f"Airflow: {fan['airflow']}")
                    
                    # Column 1: الإفرادي (Unit Price)
                    price_cell = row_cells[1]
                    price_para = price_cell.paragraphs[0]
                    price_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    price_para.add_run(f"{unit_price:.0f}")
                    
                    # Column 2: عدد (Quantity)
                    qty_cell = row_cells[2]
                    qty_para = qty_cell.paragraphs[0]
                    qty_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    qty_para.add_run(str(qty))
                    
                    # Column 3: الإجمالي (Total)
                    total_cell = row_cells[3]
                    total_para = total_cell.paragraphs[0]
                    total_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    total_para.add_run(f"$ {total_price:.0f}")
                
                doc.add_paragraph()
                
                # ===== FOOTER SECTION =====
                # Notes section
                notes_para = doc.add_paragraph()
                notes_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                notes_para._element.set(qn('w:rtl'), 'true')
                notes_run = notes_para.add_run("ملاحظات:")
                notes_run.bold = True
                notes_run.font.size = Pt(11)
                
                note1_para = doc.add_paragraph()
                note1_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                note1_para._element.set(qn('w:rtl'), 'true')
                note1_para.add_run("• المحرك الخارجي يتوفر لدينا نوع تشيكي يتم اختيار الاستطاعة المطلوبة على كتالوك التوربين حسب الغزارة والضغط")
                
                note2_para = doc.add_paragraph()
                note2_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                note2_para._element.set(qn('w:rtl'), 'true')
                note2_para.add_run("• التسليم أرض الشركة بدمشق")
                
                doc.add_paragraph()
                
                # Contact information
                contact_para = doc.add_paragraph()
                contact_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                contact_para.add_run("DAMASCUS. SYRIA. TEL: (0096311) 2122066-2141283 - FAX: 2122048 - P.O.BOX 32157")
                contact_para.runs[0].font.size = Pt(9)
                
                contact_arabic_para = doc.add_paragraph()
                contact_arabic_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                contact_arabic_para._element.set(qn('w:rtl'), 'true')
                contact_arabic_para.add_run("دمشق . برامكة . جانب الهجرة والجوازات - 21220662 / 2141283 - فاكس : 2122048 / ص . ب 32157 - س . ت 12661")
                contact_arabic_para.runs[0].font.size = Pt(9)
                
                # Date
                date_para = doc.add_paragraph()
                date_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                date_para._element.set(qn('w:rtl'), 'true')
                date_para.add_run(f"مع تحياتنا {date_str}")
                
                # Save document
                doc.save(filename)
                
                messagebox.showinfo("Success", f"Price list exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
                import traceback
                traceback.print_exc()

