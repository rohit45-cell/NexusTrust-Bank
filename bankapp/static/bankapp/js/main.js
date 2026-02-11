// Main JavaScript for NexusTrust Bank

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-IN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    }).format(new Date(date));
}

// Show loading spinner
function showLoading() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.id = 'loadingSpinner';
    spinner.style.position = 'fixed';
    spinner.style.top = '50%';
    spinner.style.left = '50%';
    spinner.style.transform = 'translate(-50%, -50%)';
    document.body.appendChild(spinner);
}

// Hide loading spinner
function hideLoading() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.remove();
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.getElementById('toastContainer').appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Confirm action
function confirmAction(message) {
    return confirm(message);
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }).catch(function(err) {
        showToast('Failed to copy text', 'danger');
    });
}

// Validate Indian phone number
function validateIndianPhone(phone) {
    const regex = /^[6-9]\d{9}$/;
    return regex.test(phone);
}

// Validate PAN card
function validatePAN(pan) {
    const regex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    return regex.test(pan);
}

// Validate Aadhaar
function validateAadhaar(aadhaar) {
    const regex = /^\d{12}$/;
    return regex.test(aadhaar);
}

// Validate pincode
function validatePincode(pincode) {
    const regex = /^\d{6}$/;
    return regex.test(pincode);
}

// Auto-hide alerts
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Password strength meter
function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength += 1;
    if (password.match(/[a-z]+/)) strength += 1;
    if (password.match(/[A-Z]+/)) strength += 1;
    if (password.match(/[0-9]+/)) strength += 1;
    if (password.match(/[$@#&!]+/)) strength += 1;
    
    return strength;
}

// Update password strength indicator
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.querySelector('#id_password1, #id_new_password1');
    if (passwordInput) {
        const strengthMeter = document.createElement('div');
        strengthMeter.className = 'progress mt-2';
        strengthMeter.style.height = '5px';
        strengthMeter.innerHTML = '<div class="progress-bar" role="progressbar" style="width: 0%"></div>';
        passwordInput.parentNode.appendChild(strengthMeter);
        
        passwordInput.addEventListener('input', function() {
            const strength = checkPasswordStrength(this.value);
            const progressBar = strengthMeter.querySelector('.progress-bar');
            
            if (strength <= 2) {
                progressBar.style.width = '33%';
                progressBar.className = 'progress-bar bg-danger';
            } else if (strength <= 4) {
                progressBar.style.width = '66%';
                progressBar.className = 'progress-bar bg-warning';
            } else {
                progressBar.style.width = '100%';
                progressBar.className = 'progress-bar bg-success';
            }
        });
    }
});