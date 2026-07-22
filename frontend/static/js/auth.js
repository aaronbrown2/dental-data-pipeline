// Authentication handling

// Login form handler
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const demoLoginBtn = document.getElementById('demoLoginBtn');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (demoLoginBtn) {
        demoLoginBtn.addEventListener('click', handleDemoLogin);
    }

    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
});

// Handle user login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    Utils.showSpinner('loginSpinner', true);
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token and redirect
            localStorage.setItem('token', data.access_token);
            Utils.showAlert('alert-container', 'Login successful! Redirecting...', 'success');
            
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            Utils.showAlert('alert-container', data.detail || 'Login failed. Please check your credentials.');
        }
    } catch (error) {
        Utils.showAlert('alert-container', 'Connection error. Please try again.');
        console.error('Login error:', error);
    } finally {
        Utils.showSpinner('loginSpinner', false);
    }
}

async function handleDemoLogin() {
    const demoEmail = 'demo@dental-records.dev';
    const demoPassword = 'DemoPassword123!';
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    if (emailInput) {
        emailInput.value = demoEmail;
    }

    if (passwordInput) {
        passwordInput.value = demoPassword;
    }

    Utils.showSpinner('demoLoginSpinner', true);

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: demoEmail,
                password: demoPassword
            })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            Utils.showAlert('alert-container', 'Demo loaded! Redirecting...', 'success');

            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 700);
        } else {
            Utils.showAlert('alert-container', data.detail || 'Demo login is not available.');
        }
    } catch (error) {
        Utils.showAlert('alert-container', 'Connection error. Please try again.');
        console.error('Demo login error:', error);
    } finally {
        Utils.showSpinner('demoLoginSpinner', false);
    }
}

// Handle user registration
async function handleRegister(event) {
    event.preventDefault();
    
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validation
    if (password !== confirmPassword) {
        Utils.showAlert('alert-container', 'Passwords do not match.');
        return;
    }
    
    if (password.length < 6) {
        Utils.showAlert('alert-container', 'Password must be at least 6 characters long.');
        return;
    }
    
    Utils.showSpinner('registerSpinner', true);
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password,
                first_name: firstName,
                last_name: lastName,
                phone: phone || null
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            Utils.showAlert('alert-container', 'Registration successful! You can now login.', 'success');
            
            // Auto-redirect to login page after success
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            Utils.showAlert('alert-container', data.detail || 'Registration failed. Please try again.');
        }
    } catch (error) {
        Utils.showAlert('alert-container', 'Connection error. Please try again.');
        console.error('Registration error:', error);
    } finally {
        Utils.showSpinner('registerSpinner', false);
    }
}

// Phone number formatting
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 6) {
                value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
            } else if (value.length >= 3) {
                value = value.replace(/(\d{3})(\d{3})/, '($1) $2');
            } else if (value.length > 0) {
                value = value.replace(/(\d{3})/, '($1');
            }
            e.target.value = value;
        });
    }
});

// Password strength indicator
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    if (passwordInput && document.getElementById('registerForm')) {
        passwordInput.addEventListener('input', function(e) {
            const password = e.target.value;
            const strength = getPasswordStrength(password);
            showPasswordStrength(strength);
        });
    }
});

function getPasswordStrength(password) {
    let score = 0;
    
    // Length check
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    
    // Character variety checks
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^a-zA-Z0-9]/.test(password)) score += 1;
    
    return score;
}

function showPasswordStrength(score) {
    // Remove existing strength indicator
    const existingIndicator = document.getElementById('password-strength');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    if (score === 0) return;
    
    const passwordInput = document.getElementById('password');
    const indicator = document.createElement('div');
    indicator.id = 'password-strength';
    indicator.className = 'mt-1';
    
    let text = '';
    let className = '';
    
    if (score <= 2) {
        text = 'Weak';
        className = 'text-danger';
    } else if (score <= 4) {
        text = 'Medium';
        className = 'text-warning';
    } else {
        text = 'Strong';
        className = 'text-success';
    }
    
    indicator.innerHTML = `<small class="${className}">Password strength: ${text}</small>`;
    passwordInput.parentNode.appendChild(indicator);
}
