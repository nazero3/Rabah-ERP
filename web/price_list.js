// Price List Window Logic
class PriceListManager {
    constructor() {
        this.selectedFans = []; // Array of {fan: fanData, priceType: 'wholesale'|'retail', quantity: number}
        this.selectedAvailableId = null;
        this.selectedPriceListIndex = null;
        this.init();
    }

    init() {
        // Search in available fans
        document.getElementById('availableSearch').addEventListener('input', (e) => {
            this.refreshAvailableFans(e.target.value);
        });

        // Available table click
        document.getElementById('availableTableBody').addEventListener('click', (e) => {
            const row = e.target.closest('tr');
            if (row) {
                document.querySelectorAll('#availableTableBody tr').forEach(r => r.classList.remove('selected'));
                row.classList.add('selected');
                this.selectedAvailableId = parseInt(row.dataset.id);
            }
        });

        // Price list table click
        document.getElementById('priceListTableBody').addEventListener('click', (e) => {
            const row = e.target.closest('tr');
            if (row) {
                document.querySelectorAll('#priceListTableBody tr').forEach(r => r.classList.remove('selected'));
                row.classList.add('selected');
                this.selectedPriceListIndex = parseInt(row.dataset.index);
            }
        });

        // Double-click on price type or quantity to edit
        document.getElementById('priceListTableBody').addEventListener('dblclick', (e) => {
            const cell = e.target;
            const row = cell.closest('tr');
            if (!row) return;

            const index = parseInt(row.dataset.index);
            const item = this.selectedFans[index];
            if (!item) return;

            // Check if clicked on price type or quantity cell
            if (cell.classList.contains('price-type-cell')) {
                this.changePriceType(index);
            } else if (cell.classList.contains('quantity-cell')) {
                this.editQuantity(index);
            }
        });

        // Initial load
        this.refreshAvailableFans('');
        this.updatePriceList();
    }

    refreshAvailableFans(searchQuery = '') {
        const tbody = document.getElementById('availableTableBody');
        tbody.innerHTML = '';

        let fans = searchQuery ? db.searchFans(searchQuery) : db.getAll('fans');
        
        // Sort by name
        fans.sort((a, b) => {
            const aName = (a.name || '').toLowerCase();
            const bName = (b.name || '').toLowerCase();
            return aName.localeCompare(bName);
        });

        fans.forEach(fan => {
            const row = document.createElement('tr');
            row.dataset.id = fan.id;
            
            const cells = [
                fan.quantity || 0,
                fan.price_retail || 0,
                fan.price_wholesale || 0,
                fan.airflow || '',
                fan.name || ''
            ];

            cells.forEach(cellValue => {
                const td = document.createElement('td');
                td.textContent = cellValue;
                row.appendChild(td);
            });

            tbody.appendChild(row);
        });
    }

    addToPriceList() {
        if (!this.selectedAvailableId) {
            alert('يرجى تحديد مروحة من القائمة المتاحة / Please select a fan from available list');
            return;
        }

        const fan = db.getFanById(this.selectedAvailableId);
        if (!fan) {
            alert('لم يتم العثور على المروحة / Fan not found');
            return;
        }

        // Check if already in price list
        if (this.selectedFans.some(item => item.fan.id === fan.id)) {
            alert('هذه المروحة موجودة بالفعل في عرض السعر / This fan is already in the price list');
            return;
        }

        // Show dialog to select price type and quantity
        this.selectPriceTypeAndQuantity(fan);
    }

    selectPriceTypeAndQuantity(fan) {
        // Create a simple modal for price type and quantity selection
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 400px;">
                <h2>إضافة إلى عرض السعر / Add to Price List</h2>
                <div class="form-group">
                    <label>نوع السعر / Price Type:</label>
                    <select id="priceTypeSelect" style="width: 100%; padding: 10px; margin-top: 5px;">
                        <option value="wholesale">جملة / Wholesale (${fan.price_wholesale})</option>
                        <option value="retail">مفرق / Retail (${fan.price_retail})</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>الكمية / Quantity:</label>
                    <input type="number" id="quantityInput" value="1" min="1" max="${fan.quantity || 9999}" 
                           style="width: 100%; padding: 10px; margin-top: 5px;">
                    <small style="color: #666;">متاح / Available: ${fan.quantity || 0}</small>
                </div>
                <div class="modal-actions">
                    <button class="btn btn-primary" onclick="confirmAddToPriceList()">إضافة / Add</button>
                    <button class="btn btn-secondary" onclick="cancelAddToPriceList()">إلغاء / Cancel</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Store fan for the confirm function
        window._pendingFan = fan;
        window._pendingModal = modal;
    }

    changePriceType(index) {
        const item = this.selectedFans[index];
        if (!item) return;

        // Toggle price type
        item.priceType = item.priceType === 'wholesale' ? 'retail' : 'wholesale';
        this.updatePriceList();
        
        // Reselect the row
        setTimeout(() => {
            const rows = document.querySelectorAll('#priceListTableBody tr');
            if (rows[index]) {
                rows[index].classList.add('selected');
                this.selectedPriceListIndex = index;
            }
        }, 10);
    }

    editQuantity(index) {
        const item = this.selectedFans[index];
        if (!item) return;

        const newQty = prompt(
            'أدخل الكمية الجديدة / Enter new quantity:\n' +
            '(Available: ' + (item.fan.quantity || 0) + ')',
            item.quantity
        );

        if (newQty !== null && newQty !== '') {
            const qty = parseInt(newQty) || 1;
            if (qty > 0) {
                item.quantity = qty;
                this.updatePriceList();
                
                // Reselect the row
                setTimeout(() => {
                    const rows = document.querySelectorAll('#priceListTableBody tr');
                    if (rows[index]) {
                        rows[index].classList.add('selected');
                        this.selectedPriceListIndex = index;
                    }
                }, 10);
            }
        }
    }

    removeFromPriceList() {
        if (this.selectedPriceListIndex === null) {
            alert('يرجى تحديد عنصر للحذف / Please select an item to remove');
            return;
        }

        if (confirm('هل تريد حذف هذا العنصر من عرض السعر؟ / Remove this item from price list?')) {
            this.selectedFans.splice(this.selectedPriceListIndex, 1);
            this.selectedPriceListIndex = null;
            this.updatePriceList();
        }
    }

    moveUp() {
        if (this.selectedPriceListIndex === null || this.selectedPriceListIndex === 0) {
            return;
        }

        const temp = this.selectedFans[this.selectedPriceListIndex];
        this.selectedFans[this.selectedPriceListIndex] = this.selectedFans[this.selectedPriceListIndex - 1];
        this.selectedFans[this.selectedPriceListIndex - 1] = temp;
        this.selectedPriceListIndex--;
        this.updatePriceList();
    }

    moveDown() {
        if (this.selectedPriceListIndex === null || this.selectedPriceListIndex >= this.selectedFans.length - 1) {
            return;
        }

        const temp = this.selectedFans[this.selectedPriceListIndex];
        this.selectedFans[this.selectedPriceListIndex] = this.selectedFans[this.selectedPriceListIndex + 1];
        this.selectedFans[this.selectedPriceListIndex + 1] = temp;
        this.selectedPriceListIndex++;
        this.updatePriceList();
    }

    sortById() {
        this.selectedFans.sort((a, b) => a.fan.id - b.fan.id);
        this.updatePriceList();
        alert('تم الترتيب حسب ID / Sorted by ID');
    }

    updatePriceList() {
        const tbody = document.getElementById('priceListTableBody');
        tbody.innerHTML = '';

        if (this.selectedFans.length === 0) {
            const row = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = 7;
            td.textContent = 'لا توجد عناصر في عرض السعر / No items in price list';
            td.style.textAlign = 'center';
            td.style.padding = '20px';
            td.style.color = '#999';
            row.appendChild(td);
            tbody.appendChild(row);
            return;
        }

        this.selectedFans.forEach((item, index) => {
            const row = document.createElement('tr');
            row.dataset.index = index;

            const price = item.priceType === 'wholesale' ? item.fan.price_wholesale : item.fan.price_retail;
            const priceTypeText = item.priceType === 'wholesale' ? 'جملة / Wholesale' : 'مفرق / Retail';

            // Actions cell
            const actionsCell = document.createElement('td');
            const removeBtn = document.createElement('button');
            removeBtn.textContent = 'حذف / Remove';
            removeBtn.className = 'btn btn-danger';
            removeBtn.style.padding = '5px 10px';
            removeBtn.style.fontSize = '12px';
            removeBtn.onclick = (e) => {
                e.stopPropagation();
                this.selectedPriceListIndex = index;
                this.removeFromPriceList();
            };
            actionsCell.appendChild(removeBtn);

            // Quantity cell (editable)
            const qtyCell = document.createElement('td');
            qtyCell.className = 'quantity-cell';
            qtyCell.textContent = item.quantity;
            qtyCell.style.cursor = 'pointer';
            qtyCell.style.color = '#667eea';
            qtyCell.style.fontWeight = '500';
            qtyCell.title = 'انقر نقراً مزدوجاً للتعديل / Double-click to edit';

            // Price type cell (editable)
            const priceTypeCell = document.createElement('td');
            priceTypeCell.className = 'price-type-cell';
            priceTypeCell.textContent = priceTypeText;
            priceTypeCell.style.cursor = 'pointer';
            priceTypeCell.style.color = '#667eea';
            priceTypeCell.style.fontWeight = '500';
            priceTypeCell.title = 'انقر نقراً مزدوجاً للتبديل / Double-click to switch';

            // Price cell
            const priceCell = document.createElement('td');
            priceCell.textContent = price.toFixed(2);

            // Airflow cell
            const airflowCell = document.createElement('td');
            airflowCell.textContent = item.fan.airflow || '';

            // Name cell
            const nameCell = document.createElement('td');
            nameCell.textContent = item.fan.name || '';

            // Add total cell
            const totalCell = document.createElement('td');
            const total = price * item.quantity;
            totalCell.textContent = total.toFixed(2);
            totalCell.style.fontWeight = '600';

            row.appendChild(actionsCell);
            row.appendChild(qtyCell);
            row.appendChild(priceTypeCell);
            row.appendChild(priceCell);
            row.appendChild(totalCell);
            row.appendChild(airflowCell);
            row.appendChild(nameCell);

            tbody.appendChild(row);
        });
    }

    async exportToWord() {
        if (this.selectedFans.length === 0) {
            alert('عرض السعر فارغ / Price list is empty');
            return;
        }

        // Check if JSZip is loaded
        if (typeof JSZip === 'undefined') {
            alert('خطأ: مكتبة JSZip غير متوفرة.\n\nيرجى:\n1. التأكد من الاتصال بالإنترنت\n2. تحديث الصفحة (F5)\n\nError: JSZip library not available.\n\nPlease:\n1. Ensure internet connection\n2. Refresh the page (F5)');
            return;
        }

        // Get customer name and date
        const customerName = prompt('أدخل اسم العميل / Enter customer name:') || 'Customer';
        const date = prompt('أدخل التاريخ / Enter date:', new Date().toLocaleDateString('ar-SA')) || new Date().toLocaleDateString();

        try {
            // Load the template file - try multiple paths
            const templatePaths = [
                'format.docx',
                './format.docx',
                'web/format.docx',
                '../format.docx'
            ];
            
            let templateData = null;
            let loadedPath = null;
            
            for (const templatePath of templatePaths) {
                try {
                    const response = await fetch(templatePath, {
                        method: 'GET',
                        cache: 'no-cache'
                    });
                    
                    if (response.ok) {
                        templateData = await response.arrayBuffer();
                        loadedPath = templatePath;
                        console.log('Template loaded from:', templatePath);
                        break;
                    } else {
                        console.warn('Failed to load from', templatePath, '- Status:', response.status);
                    }
                } catch (err) {
                    console.warn('Error loading from', templatePath, ':', err.message);
                }
            }
            
            if (!templateData) {
                // Show a modal with a button to select the file manually
                // This ensures the file input click is directly from user action
                const modal = document.createElement('div');
                modal.className = 'modal';
                modal.style.display = 'flex';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 500px;">
                        <h2>اختيار ملف القالب / Select Template File</h2>
                        <p style="margin: 20px 0;">
                            لم يتم العثور على ملف format.docx تلقائياً.<br>
                            يرجى اختيار ملف format.docx يدوياً.<br><br>
                            Template file not found automatically.<br>
                            Please select format.docx file manually.
                        </p>
                        <div class="modal-actions">
                            <button id="selectTemplateBtn" class="btn btn-primary">اختيار الملف / Select File</button>
                            <button id="cancelTemplateBtn" class="btn btn-secondary">إلغاء / Cancel</button>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
                
                // Wait for user to click the button
                await new Promise((resolve, reject) => {
                    const selectBtn = document.getElementById('selectTemplateBtn');
                    const cancelBtn = document.getElementById('cancelTemplateBtn');
                    
                    // Create file input
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.accept = '.docx';
                    input.style.display = 'none';
                    document.body.appendChild(input);
                    
                    let resolved = false;
                    
                    // Handle file selection
                    input.addEventListener('change', async (e) => {
                        if (resolved) return;
                        resolved = true;
                        
                        const file = e.target.files[0];
                        if (file) {
                            try {
                                const reader = new FileReader();
                                reader.onload = async (event) => {
                                    try {
                                        document.body.removeChild(modal);
                                        document.body.removeChild(input);
                                        await this.processTemplate(event.target.result, customerName, date);
                                        resolve();
                                    } catch (err) {
                                        console.error('Processing error:', err);
                                        document.body.removeChild(modal);
                                        document.body.removeChild(input);
                                        alert('خطأ في المعالجة: ' + err.message + '\n\nProcessing error: ' + err.message);
                                        reject(err);
                                    }
                                };
                                reader.onerror = (err) => {
                                    console.error('FileReader error:', err);
                                    document.body.removeChild(modal);
                                    document.body.removeChild(input);
                                    alert('خطأ في قراءة الملف / Error reading file');
                                    reject(err);
                                };
                                reader.readAsArrayBuffer(file);
                            } catch (err) {
                                document.body.removeChild(modal);
                                document.body.removeChild(input);
                                reject(err);
                            }
                        } else {
                            document.body.removeChild(modal);
                            document.body.removeChild(input);
                            reject(new Error('لم يتم اختيار ملف / No file selected'));
                        }
                    }, { once: true });
                    
                    // Button click handlers
                    selectBtn.addEventListener('click', () => {
                        input.click();
                    });
                    
                    cancelBtn.addEventListener('click', () => {
                        if (!resolved) {
                            resolved = true;
                            document.body.removeChild(modal);
                            document.body.removeChild(input);
                            reject(new Error('تم الإلغاء / Cancelled'));
                        }
                    });
                });
                return; // Exit early
            }
            
            // Process the template
            await this.processTemplate(templateData, customerName, date);
        } catch (error) {
            console.error('Export error:', error);
            if (error.message !== 'تم الإلغاء / Cancelled') {
                alert('خطأ في التصدير: ' + error.message + '\n\nExport error: ' + error.message);
            }
        }
    }

    async processTemplate(templateData, customerName, date) {
        try {
            const zip = await JSZip.loadAsync(templateData);

            // Get the main document XML
            const documentXmlFile = zip.file('word/document.xml');
            if (!documentXmlFile) {
                throw new Error('ملف document.xml غير موجود في القالب.\n\ndocument.xml not found in template.');
            }
            
            const documentXml = await documentXmlFile.async('string');
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(documentXml, 'text/xml');
            
            // Check for parsing errors
            const parserError = xmlDoc.querySelector('parsererror');
            if (parserError) {
                throw new Error('خطأ في تحليل ملف XML: ' + parserError.textContent);
            }

            // Find all tables in the document
            const tables = xmlDoc.getElementsByTagName('w:tbl');
            
            if (tables.length === 0) {
                throw new Error('لم يتم العثور على جدول في ملف القالب.\n\nNo table found in template file.');
            }

            // Use the first table (or find table with {PRODUCTS_TABLE} placeholder)
            let productTable = null;
            for (let i = 0; i < tables.length; i++) {
                const tableText = tables[i].textContent;
                if (tableText.includes('{PRODUCTS_TABLE}') || tableText.includes('{{PRODUCTS_TABLE}}')) {
                    productTable = tables[i];
                    // Remove placeholder text
                    const cells = productTable.getElementsByTagName('w:tc');
                    for (let cell of cells) {
                        const textNodes = cell.getElementsByTagName('w:t');
                        for (let textNode of textNodes) {
                            if (textNode.textContent.includes('{PRODUCTS_TABLE}') || textNode.textContent.includes('{{PRODUCTS_TABLE}}')) {
                                textNode.textContent = textNode.textContent.replace(/{{\{?PRODUCTS_TABLE\}\}?/g, '');
                            }
                        }
                    }
                    break;
                }
            }

            // If no placeholder found, use the first table
            if (!productTable && tables.length > 0) {
                productTable = tables[0];
            }

            if (!productTable) {
                throw new Error('لم يتم العثور على جدول المنتجات.\n\nProduct table not found.');
            }

            // Get table rows
            const rows = productTable.getElementsByTagName('w:tr');
            
            // Keep header row (first row), remove data rows
            while (rows.length > 1) {
                productTable.removeChild(rows[rows.length - 1]);
            }

            // Add product rows (matching desktop format: الإجمالي, عدد, الإفرادي, النوع)
            const grandTotal = this.selectedFans.reduce((sum, item) => {
                const price = item.priceType === 'wholesale' ? item.fan.price_wholesale : item.fan.price_retail;
                return sum + (price * item.quantity);
            }, 0);

            this.selectedFans.forEach((item) => {
                const price = item.priceType === 'wholesale' ? item.fan.price_wholesale : item.fan.price_retail;
                const total = price * item.quantity;
                
                // Create new row
                const newRow = xmlDoc.createElement('w:tr');
                
                // Create 4 cells: الإجمالي (Total), عدد (Quantity), الإفرادي (Unit Price), النوع (Name)
                const cells = [
                    { value: `$ ${total.toFixed(0)}`, align: 'center' },  // Total
                    { value: String(item.quantity), align: 'center' },      // Quantity
                    { value: price.toFixed(0), align: 'center' },          // Unit Price
                    { value: item.fan.name || '', align: 'right' }          // Name
                ];

                cells.forEach((cellData) => {
                    const cell = xmlDoc.createElement('w:tc');
                    const para = xmlDoc.createElement('w:p');
                    const pPr = xmlDoc.createElement('w:pPr');
                    const jc = xmlDoc.createElement('w:jc');
                    jc.setAttribute('w:val', cellData.align);
                    pPr.appendChild(jc);
                    para.appendChild(pPr);
                    
                    const run = xmlDoc.createElement('w:r');
                    const text = xmlDoc.createElement('w:t');
                    text.setAttribute('xml:space', 'preserve');
                    text.textContent = cellData.value;
                    run.appendChild(text);
                    para.appendChild(run);
                    cell.appendChild(para);
                    newRow.appendChild(cell);
                });

                productTable.appendChild(newRow);
            });

            // Replace placeholders in document
            const serializer = new XMLSerializer();
            let updatedXml = serializer.serializeToString(xmlDoc);
            
            // Replace placeholders
            updatedXml = updatedXml.replace(/{{\{?CUSTOMER_NAME\}\}?/g, customerName);
            updatedXml = updatedXml.replace(/{{\{?DATE\}\}?/g, date);

            // Update the document.xml in the zip
            zip.file('word/document.xml', updatedXml);

            // Generate the output file
            const blob = await zip.generateAsync({
                type: 'blob',
                mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            });

            // Download the file
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `price_list_${customerName.replace(/\s+/g, '_')}_${date.replace(/\//g, '_')}.docx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            alert('تم التصدير بنجاح! / Export successful!');
        } catch (error) {
            console.error('Export error:', error);
            alert('خطأ في التصدير: ' + error.message + '\n\nExport error: ' + error.message);
        }
    }
}

// Global functions for button onclick handlers
let priceListManager;

function addToPriceList() {
    priceListManager.addToPriceList();
}

function confirmAddToPriceList() {
    if (!window._pendingFan || !window._pendingModal) return;

    const fan = window._pendingFan;
    const priceType = document.getElementById('priceTypeSelect').value;
    const quantity = parseInt(document.getElementById('quantityInput').value) || 1;

    priceListManager.selectedFans.push({
        fan: fan,
        priceType: priceType,
        quantity: quantity
    });

    document.body.removeChild(window._pendingModal);
    window._pendingFan = null;
    window._pendingModal = null;

    priceListManager.updatePriceList();
}

function cancelAddToPriceList() {
    if (window._pendingModal) {
        document.body.removeChild(window._pendingModal);
        window._pendingFan = null;
        window._pendingModal = null;
    }
}

function removeFromPriceList() {
    priceListManager.removeFromPriceList();
}

function moveUp() {
    priceListManager.moveUp();
}

function moveDown() {
    priceListManager.moveDown();
}

function sortById() {
    priceListManager.sortById();
}

function exportToWord() {
    priceListManager.exportToWord();
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    priceListManager = new PriceListManager();
});

