// Database Management using localStorage
class Database {
    constructor() {
        this.init();
    }

    init() {
        // Initialize empty databases if they don't exist
        if (!localStorage.getItem('fans_db')) {
            localStorage.setItem('fans_db', JSON.stringify([]));
        }
        if (!localStorage.getItem('sheet_metal_db')) {
            localStorage.setItem('sheet_metal_db', JSON.stringify([]));
        }
        if (!localStorage.getItem('flexible_db')) {
            localStorage.setItem('flexible_db', JSON.stringify([]));
        }
    }

    // Generic methods
    getTableName(productType) {
        const tables = {
            'fans': 'fans_db',
            'sheet_metal': 'sheet_metal_db',
            'flexible': 'flexible_db'
        };
        return tables[productType] || 'fans_db';
    }

    getAll(productType) {
        const tableName = this.getTableName(productType);
        const data = localStorage.getItem(tableName);
        return JSON.parse(data || '[]');
    }

    saveAll(productType, data) {
        const tableName = this.getTableName(productType);
        localStorage.setItem(tableName, JSON.stringify(data));
    }

    getNextId(productType) {
        const items = this.getAll(productType);
        if (items.length === 0) return 1;
        return Math.max(...items.map(item => item.id || 0)) + 1;
    }

    // Fans operations
    addFan(fanData) {
        const fans = this.getAll('fans');
        const newFan = {
            id: this.getNextId('fans'),
            name: fanData.name,
            description: fanData.description || null,
            airflow: fanData.airflow || null,
            price_wholesale: parseFloat(fanData.price_wholesale),
            price_retail: parseFloat(fanData.price_retail),
            quantity: parseInt(fanData.quantity) || 0,
            catalog_file_path: fanData.catalog_file_path || null
        };
        fans.push(newFan);
        this.saveAll('fans', fans);
        return newFan;
    }

    updateFan(id, fanData) {
        const fans = this.getAll('fans');
        const index = fans.findIndex(f => f.id === id);
        if (index !== -1) {
            fans[index] = { ...fans[index], ...fanData, id: id };
            this.saveAll('fans', fans);
            return fans[index];
        }
        return null;
    }

    deleteFan(id) {
        const fans = this.getAll('fans');
        const filtered = fans.filter(f => f.id !== id);
        this.saveAll('fans', filtered);
    }

    getFanById(id) {
        const fans = this.getAll('fans');
        return fans.find(f => f.id === id) || null;
    }

    searchFans(query) {
        const fans = this.getAll('fans');
        const lowerQuery = query.toLowerCase();
        return fans.filter(fan => 
            (fan.name && fan.name.toLowerCase().includes(lowerQuery)) ||
            (fan.airflow && fan.airflow.toLowerCase().includes(lowerQuery)) ||
            (fan.description && fan.description.toLowerCase().includes(lowerQuery))
        );
    }

    // Sheet Metal operations
    addSheetMetal(data) {
        const items = this.getAll('sheet_metal');
        const newItem = {
            id: this.getNextId('sheet_metal'),
            thickness: data.thickness || null,
            dimensions: data.dimensions || null,
            measurement: data.measurement || null,
            cost: parseFloat(data.cost),
            extra: data.extra || null
        };
        items.push(newItem);
        this.saveAll('sheet_metal', items);
        return newItem;
    }

    updateSheetMetal(id, data) {
        const items = this.getAll('sheet_metal');
        const index = items.findIndex(item => item.id === id);
        if (index !== -1) {
            items[index] = { ...items[index], ...data, id: id };
            this.saveAll('sheet_metal', items);
            return items[index];
        }
        return null;
    }

    deleteSheetMetal(id) {
        const items = this.getAll('sheet_metal');
        const filtered = items.filter(item => item.id !== id);
        this.saveAll('sheet_metal', filtered);
    }

    getSheetMetalById(id) {
        const items = this.getAll('sheet_metal');
        return items.find(item => item.id === id) || null;
    }

    searchSheetMetal(query) {
        const items = this.getAll('sheet_metal');
        const lowerQuery = query.toLowerCase();
        return items.filter(item => 
            (item.thickness && item.thickness.toLowerCase().includes(lowerQuery)) ||
            (item.dimensions && item.dimensions.toLowerCase().includes(lowerQuery)) ||
            (item.measurement && item.measurement.toLowerCase().includes(lowerQuery))
        );
    }

    // Flexible operations
    addFlexible(data) {
        const items = this.getAll('flexible');
        const newItem = {
            id: this.getNextId('flexible'),
            description: data.description || null,
            diameter: data.diameter || null,
            collection: data.collection || null,
            meter: parseFloat(data.meter)
        };
        items.push(newItem);
        this.saveAll('flexible', items);
        return newItem;
    }

    updateFlexible(id, data) {
        const items = this.getAll('flexible');
        const index = items.findIndex(item => item.id === id);
        if (index !== -1) {
            items[index] = { ...items[index], ...data, id: id };
            this.saveAll('flexible', items);
            return items[index];
        }
        return null;
    }

    deleteFlexible(id) {
        const items = this.getAll('flexible');
        const filtered = items.filter(item => item.id !== id);
        this.saveAll('flexible', filtered);
    }

    getFlexibleById(id) {
        const items = this.getAll('flexible');
        return items.find(item => item.id === id) || null;
    }

    searchFlexible(query) {
        const items = this.getAll('flexible');
        const lowerQuery = query.toLowerCase();
        return items.filter(item => 
            (item.diameter && item.diameter.toLowerCase().includes(lowerQuery)) ||
            (item.collection && item.collection.toLowerCase().includes(lowerQuery)) ||
            (item.description && item.description.toLowerCase().includes(lowerQuery))
        );
    }

    // Export database (for backup)
    exportData() {
        return {
            fans: this.getAll('fans'),
            sheet_metal: this.getAll('sheet_metal'),
            flexible: this.getAll('flexible'),
            export_date: new Date().toISOString()
        };
    }

    // Import database (for restore)
    importData(data) {
        if (data.fans) this.saveAll('fans', data.fans);
        if (data.sheet_metal) this.saveAll('sheet_metal', data.sheet_metal);
        if (data.flexible) this.saveAll('flexible', data.flexible);
    }
}

// Initialize database
const db = new Database();

