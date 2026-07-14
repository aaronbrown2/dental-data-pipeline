// Global app configuration
const API_BASE = window.location.origin;

// Utility functions
const Utils = {
    // Show alert message
    showAlert(containerId, message, type = 'danger') {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        container.innerHTML = '';
        container.appendChild(alert);
        
        // Auto-dismiss success messages
        if (type === 'success') {
            setTimeout(() => {
                alert.remove();
            }, 3000);
        }
    },

    // Show loading spinner
    showSpinner(elementId, show = true) {
        const spinner = document.getElementById(elementId);
        if (spinner) {
            spinner.classList.toggle('d-none', !show);
        }
    },

    // Format date
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Capitalize first letter
    capitalize(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
};

// API helper functions
const API = {
    // Make authenticated API request
    async request(endpoint, options = {}) {
        const token = localStorage.getItem('token');
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, config);
            
            if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('token');
                window.location.href = 'login.html';
                return;
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // GET request
    async get(endpoint) {
        return this.request(endpoint);
    },

    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // PUT request
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    },

    // Upload file
    async upload(endpoint, formData) {
        const token = localStorage.getItem('token');
        const config = {
            method: 'POST',
            body: formData
        };

        if (token) {
            config.headers = {
                Authorization: `Bearer ${token}`
            };
        }

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, config);
            
            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = 'login.html';
                return;
            }

            let data = null;

            if (response.headers.get("content-type")?.includes("application/json")) {
                data = await response.json();
            }

            if (!response.ok) {
                throw new Error(data?.detail || 'Upload failed');
            }

            return data;
        } catch (error) {
            console.error('Upload failed:', error);
            throw error;
        }
    }
};

// Authentication helpers
const Auth = {
    // Check if user is logged in
    isLoggedIn() {
        return !!localStorage.getItem('token');
    },

    // Get current user info
    async getCurrentUser() {
        if (!this.isLoggedIn()) return null;
        
        try {
            return await API.get('/auth/me');
        } catch (error) {
            console.error('Failed to get current user:', error);
            return null;
        }
    },

    // Logout user
    logout() {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    },

    // Redirect to login if not authenticated
    requireAuth() {
        if (!this.isLoggedIn()) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    }
};

// Page initialization
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication on protected pages
    const protectedPages = ['dashboard.html', 'profile.html', 'appointments.html', 'radiographs.html'];
    const currentPage = window.location.pathname.split('/').pop();
    
    if (protectedPages.includes(currentPage)) {
        if (!Auth.requireAuth()) {
            return;
        }
        
        // Load user info for protected pages
        loadUserInfo();
    }
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add logout functionality
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            Auth.logout();
        });
    }

    // Add toggle password functionality
    const togglePassword = document.getElementById('togglePassword');
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const passwordField = document.getElementById('password');
            const icon = this.querySelector('i');
            
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                icon.className = 'fas fa-eye-slash';
            } else {
                passwordField.type = 'password';
                icon.className = 'fas fa-eye';
            }
        });
    }
});

// Load user info for navigation
async function loadUserInfo() {
    try {
        const user = await Auth.getCurrentUser();
        if (user) {
            const userNameElements = document.querySelectorAll('#userName, #welcomeName');
            userNameElements.forEach(el => {
                if (el) el.textContent = user.first_name || 'User';
            });
        }
    } catch (error) {
        console.error('Failed to load user info:', error);
    }
}

// Global error handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    // You could show a global error message here
});

// Export for use in other scripts
window.Utils = Utils;
window.API = API;
window.Auth = Auth;