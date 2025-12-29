// Authentication Management
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        // Check if admin credentials exist, if not create default
        if (!localStorage.getItem('admin_username')) {
            localStorage.setItem('admin_username', 'admin');
            localStorage.setItem('admin_password', this.hashPassword('TechEquipRab*2025'));
        }

        // Check if user is already logged in
        const sessionUser = sessionStorage.getItem('current_user');
        if (sessionUser) {
            this.currentUser = sessionUser;
            this.showMainPage();
        } else {
            this.showLoginPage();
        }

        // Setup login form
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Setup logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });
    }

    hashPassword(password) {
        // Simple hash function (for production, use a proper hashing library)
        let hash = 0;
        for (let i = 0; i < password.length; i++) {
            const char = password.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return hash.toString();
    }

    handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('loginError');

        const storedUsername = localStorage.getItem('admin_username');
        const storedPassword = localStorage.getItem('admin_password');
        const hashedPassword = this.hashPassword(password);

        if (username === storedUsername && hashedPassword === storedPassword) {
            this.currentUser = username;
            sessionStorage.setItem('current_user', username);
            errorDiv.textContent = '';
            this.showMainPage();
        } else {
            errorDiv.textContent = 'اسم المستخدم أو كلمة المرور غير صحيحة / Invalid username or password';
        }
    }

    logout() {
        sessionStorage.removeItem('current_user');
        this.currentUser = null;
        this.showLoginPage();
    }

    showLoginPage() {
        document.getElementById('loginPage').classList.remove('hidden');
        document.getElementById('mainPage').classList.add('hidden');
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
    }

    showMainPage() {
        document.getElementById('loginPage').classList.add('hidden');
        document.getElementById('mainPage').classList.remove('hidden');
        document.getElementById('currentUser').textContent = 
            `المستخدم: ${this.currentUser} / User: ${this.currentUser}`;
    }

    // Admin password change (can be called from browser console or admin panel)
    changePassword(newPassword) {
        if (this.currentUser === 'admin') {
            localStorage.setItem('admin_password', this.hashPassword(newPassword));
            return true;
        }
        return false;
    }
}

// Initialize auth manager
const authManager = new AuthManager();
