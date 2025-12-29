// Main Application Logic
class App {
    constructor() {
        this.currentProductType = 'fans';
        this.selectedItemId = null;
        this.sortColumn = 'id';
        this.sortReverse = false;
        this.searchQuery = '';
        this.selectedFans = []; // For price list
        
        this.init();
    }

    init() {
        // Product type change
        document.querySelectorAll('input[name="productType"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentProductType = e.target.value;
                this.selectedItemId = null;
                this.updateSortButtons();
                this.refreshTable();
            });
        });

        // Button events
        document.getElementById('addBtn').addEventListener('click', () => this.showAddDialog());
        document.getElementById('editBtn').addEventListener('click', () => this.showEditDialog());
        document.getElementById('deleteBtn').addEventListener('click', () => this.deleteItem());
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshTable());
        document.getElementById('priceListBtn').addEventListener('click', () => {
            if (this.currentProductType === 'fans') {
                this.showPriceListWindow();
            } else {
                alert('Price list is currently available only for Fans.');
            }
        });
        document.getElementById('viewDatasheetBtn').addEventListener('click', () => this.viewDatasheet());

        // Search
        document.getElementById('toggleSearchBtn').addEventListener('click', () => this.toggleSearch());
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.searchQuery = e.target.value;
            this.refreshTable();
        });

        // Table row click
        document.getElementById('tableBody').addEventListener('click', (e) => {
            const row = e.target.closest('tr');
            if (row) {
                document.querySelectorAll('#tableBody tr').forEach(r => r.classList.remove('selected'));
                row.classList.add('selected');
                this.selectedItemId = parseInt(row.dataset.id);
            }
        });

        // Modal close
        document.querySelector('.close').addEventListener('click', () => this.closeModal());

        // Initial setup
        this.updateSortButtons();
        this.refreshTable();
    }

    updateSortButtons() {
        const container = document.getElementById('sortButtons');
        container.innerHTML = '';

        const columns = this.getColumnsForProductType();
        columns.forEach(col => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-secondary';
            btn.textContent = col.label;
            btn.addEventListener('click', () => this.sortBy(col.key));
            container.appendChild(btn);
        });
    }

    getColumnsForProductType() {
        if (this.currentProductType === 'fans') {
            return [
                { key: 'id', label: 'ID' },
                { key: 'name', label: 'نوع / Name' },
                { key: 'airflow', label: 'غزارة / Airflow' },
                { key: 'price_wholesale', label: 'جملة / Wholesale' },
                { key: 'price_retail', label: 'مفرق / Retail' },
                { key: 'quantity', label: 'كمية / Quantity' }
            ];
        } else if (this.currentProductType === 'sheet_metal') {
            return [
                { key: 'id', label: 'ID' },
                { key: 'thickness', label: 'سماكة الصاج' },
                { key: 'dimensions', label: 'ابعاد الصندوق' },
                { key: 'measurement', label: 'القياس' },
                { key: 'cost', label: 'اجور' },
                { key: 'extra', label: 'عزل و ارموفلكس' }
            ];
        } else { // flexible
            return [
                { key: 'id', label: 'ID' },
                { key: 'diameter', label: 'قطر' },
                { key: 'collection', label: 'ربطة' },
                { key: 'meter', label: 'متر' }
            ];
        }
    }

    sortBy(column) {
        if (this.sortColumn === column) {
            this.sortReverse = !this.sortReverse;
        } else {
            this.sortColumn = column;
            this.sortReverse = false;
        }
        this.refreshTable();
    }

    toggleSearch() {
        const container = document.getElementById('searchContainer');
        const btn = document.getElementById('toggleSearchBtn');
        
        if (container.classList.contains('hidden')) {
            container.classList.remove('hidden');
            btn.textContent = '✖ إخفاء البحث / Hide Search';
        } else {
            container.classList.add('hidden');
            btn.textContent = '🔍 إظهار البحث / Show Search';
            document.getElementById('searchInput').value = '';
            this.searchQuery = '';
            this.refreshTable();
        }
    }

    refreshTable() {
        let items = [];
        
        // Get items based on product type
        if (this.currentProductType === 'fans') {
            items = this.searchQuery ? db.searchFans(this.searchQuery) : db.getAll('fans');
        } else if (this.currentProductType === 'sheet_metal') {
            items = this.searchQuery ? db.searchSheetMetal(this.searchQuery) : db.getAll('sheet_metal');
        } else {
            items = this.searchQuery ? db.searchFlexible(this.searchQuery) : db.getAll('flexible');
        }

        // Sort items
        items.sort((a, b) => {
            let aVal = a[this.sortColumn] || '';
            let bVal = b[this.sortColumn] || '';
            
            if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }
            
            if (this.sortReverse) {
                return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
            } else {
                return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
            }
        });

        // Update table
        this.updateTable(items);
    }

    updateTable(items) {
        const thead = document.getElementById('tableHead');
        const tbody = document.getElementById('tableBody');
        
        thead.innerHTML = '';
        tbody.innerHTML = '';

        const columns = this.getColumnsForProductType();
        
        // Create header
        const headerRow = document.createElement('tr');
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col.label;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);

        // Create rows
        items.forEach(item => {
            const row = document.createElement('tr');
            row.dataset.id = item.id;
            
            columns.forEach(col => {
                const td = document.createElement('td');
                const value = item[col.key];
                td.textContent = value !== null && value !== undefined ? value : '';
                row.appendChild(td);
            });
            
            tbody.appendChild(row);
        });
    }

    showAddDialog() {
        document.getElementById('modalTitle').textContent = 'إضافة عنصر / Add Item';
        this.showItemForm();
    }

    showEditDialog() {
        if (!this.selectedItemId) {
            alert('يرجى تحديد عنصر للتعديل / Please select an item to edit');
            return;
        }

        document.getElementById('modalTitle').textContent = 'تعديل عنصر / Edit Item';
        this.showItemForm(this.selectedItemId);
    }

    showItemForm(itemId = null) {
        const form = document.getElementById('itemForm');
        form.innerHTML = '';

        let itemData = null;
        if (itemId) {
            if (this.currentProductType === 'fans') {
                itemData = db.getFanById(itemId);
            } else if (this.currentProductType === 'sheet_metal') {
                itemData = db.getSheetMetalById(itemId);
            } else {
                itemData = db.getFlexibleById(itemId);
            }
        }

        const fields = this.getFieldsForProductType();
        
        fields.forEach(field => {
            const group = document.createElement('div');
            group.className = 'form-group';
            
            const label = document.createElement('label');
            label.textContent = field.label + (field.required ? ' *' : '');
            label.setAttribute('for', field.name);
            
            let input;
            if (field.type === 'select') {
                input = document.createElement('select');
                field.options.forEach(opt => {
                    const option = document.createElement('option');
                    option.value = opt.value;
                    option.textContent = opt.label;
                    input.appendChild(option);
                });
            } else {
                input = document.createElement('input');
                input.type = field.type || 'text';
            }
            
            input.id = field.name;
            input.name = field.name;
            input.required = field.required || false;
            
            if (itemData && itemData[field.name] !== null && itemData[field.name] !== undefined) {
                input.value = itemData[field.name];
            } else if (field.default !== undefined) {
                input.value = field.default;
            }

            group.appendChild(label);
            group.appendChild(input);
            form.appendChild(group);
        });

        form.onsubmit = (e) => {
            e.preventDefault();
            this.saveItem(itemId);
        };

        document.getElementById('itemModal').classList.remove('hidden');
    }

    getFieldsForProductType() {
        if (this.currentProductType === 'fans') {
            return [
                { name: 'name', label: 'نوع / Name', required: true },
                { name: 'description', label: 'الوصف / Description' },
                { name: 'airflow', label: 'غزارة / Airflow' },
                { name: 'price_wholesale', label: 'سعر الجملة / Wholesale Price', type: 'number', step: '0.01', required: true },
                { name: 'price_retail', label: 'سعر المفرق / Retail Price', type: 'number', step: '0.01', required: true },
                { name: 'quantity', label: 'الكمية / Quantity', type: 'number', default: '0', required: true },
                { name: 'catalog_file_path', label: 'ملف الكتالوج / Catalog File Path' }
            ];
        } else if (this.currentProductType === 'sheet_metal') {
            return [
                { name: 'thickness', label: 'سماكة الصاج / Thickness' },
                { name: 'dimensions', label: 'ابعاد الصندوق / Dimensions' },
                { name: 'measurement', label: 'القياس / Measurement' },
                { name: 'cost', label: 'اجور / Cost', type: 'number', step: '0.01', required: true },
                { name: 'extra', label: 'عزل و ارموفلكس / Extra' }
            ];
        } else { // flexible
            return [
                { name: 'description', label: 'الوصف / Description' },
                { name: 'diameter', label: 'قطر / Diameter' },
                { name: 'collection', label: 'ربطة / Collection' },
                { name: 'meter', label: 'متر / Meter', type: 'number', step: '0.01', required: true }
            ];
        }
    }

    saveItem(itemId) {
        const form = document.getElementById('itemForm');
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        try {
            if (itemId) {
                // Update
                if (this.currentProductType === 'fans') {
                    db.updateFan(itemId, data);
                } else if (this.currentProductType === 'sheet_metal') {
                    db.updateSheetMetal(itemId, data);
                } else {
                    db.updateFlexible(itemId, data);
                }
                alert('تم التحديث بنجاح / Updated successfully');
            } else {
                // Add
                if (this.currentProductType === 'fans') {
                    db.addFan(data);
                } else if (this.currentProductType === 'sheet_metal') {
                    db.addSheetMetal(data);
                } else {
                    db.addFlexible(data);
                }
                alert('تمت الإضافة بنجاح / Added successfully');
            }
            
            this.closeModal();
            this.refreshTable();
        } catch (error) {
            alert('خطأ: ' + error.message);
        }
    }

    deleteItem() {
        if (!this.selectedItemId) {
            alert('يرجى تحديد عنصر للحذف / Please select an item to delete');
            return;
        }

        if (!confirm('هل أنت متأكد من الحذف؟ / Are you sure you want to delete?')) {
            return;
        }

        try {
            if (this.currentProductType === 'fans') {
                db.deleteFan(this.selectedItemId);
            } else if (this.currentProductType === 'sheet_metal') {
                db.deleteSheetMetal(this.selectedItemId);
            } else {
                db.deleteFlexible(this.selectedItemId);
            }
            
            this.selectedItemId = null;
            this.refreshTable();
            alert('تم الحذف بنجاح / Deleted successfully');
        } catch (error) {
            alert('خطأ: ' + error.message);
        }
    }

    closeModal() {
        document.getElementById('itemModal').classList.add('hidden');
        this.selectedItemId = null;
    }

    viewDatasheet() {
        if (this.currentProductType !== 'fans' || !this.selectedItemId) {
            alert('يرجى تحديد مروحة لعرض الكتالوج / Please select a fan to view catalog');
            return;
        }

        const fan = db.getFanById(this.selectedItemId);
        if (!fan || !fan.catalog_file_path) {
            alert('لا يوجد ملف كتالوج مرتبط بهذه المروحة / No catalog file linked to this fan');
            return;
        }

        // In web version, we can open the file if it's a URL, or show a message
        if (fan.catalog_file_path.startsWith('http')) {
            window.open(fan.catalog_file_path, '_blank');
        } else {
            alert('ملف الكتالوج: ' + fan.catalog_file_path + '\nيرجى فتح الملف يدوياً / Please open the file manually');
        }
    }

    showPriceListWindow() {
        // This would open a price list window
        // For now, show a simple implementation
        alert('Price list feature - to be implemented with Word export');
        // TODO: Implement full price list window
    }
}

// Initialize app when page loads
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('mainPage') && !document.getElementById('mainPage').classList.contains('hidden')) {
        new App();
    }
});

// Re-initialize app when main page is shown
const originalShowMainPage = authManager.showMainPage.bind(authManager);
authManager.showMainPage = function() {
    originalShowMainPage();
    setTimeout(() => {
        if (!window.app) {
            window.app = new App();
        }
    }, 100);
};

