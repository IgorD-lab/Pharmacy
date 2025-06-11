// Pharmacy System JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add confirmation dialog for rejection
    const rejectButtons = document.querySelectorAll('[data-bs-target="#rejectModal"]');
    rejectButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Clear previous content
            document.getElementById('reason').value = '';
        });
    });

    // Add click handlers for table rows (if needed)
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on buttons
            if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'A' && !e.target.closest('button') && !e.target.closest('a')) {
                // Add subtle highlight effect
                row.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
                setTimeout(function() {
                    row.style.backgroundColor = '';
                }, 200);
            }
        });
    });

    // Form validation helpers
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Add loading state to submit buttons
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
                submitBtn.disabled = true;
                
                // Re-enable button after 3 seconds as fallback
                setTimeout(function() {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    });

    // Enhanced search functionality for dashboard table
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterTable();
        });
    }

    // Table sorting functionality
    const sortableHeaders = document.querySelectorAll('.sortable');
    let currentSort = { column: null, direction: 'asc' };
    
    sortableHeaders.forEach(function(header) {
        header.addEventListener('click', function() {
            const sortType = this.getAttribute('data-sort');
            sortTable(sortType);
        });
        header.style.cursor = 'pointer';
    });

    function sortTable(column) {
        const table = document.getElementById('prescriptionsTable');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Determine sort direction
        if (currentSort.column === column) {
            currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            currentSort.direction = 'asc';
        }
        currentSort.column = column;
        
        // Update header icons
        sortableHeaders.forEach(header => {
            const icon = header.querySelector('i');
            if (header.getAttribute('data-sort') === column) {
                icon.className = currentSort.direction === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
            } else {
                icon.className = 'fas fa-sort';
            }
        });
        
        // Sort rows
        rows.sort((a, b) => {
            let aVal, bVal;
            
            switch(column) {
                case 'id':
                    aVal = parseInt(a.cells[0].textContent.replace('#', ''));
                    bVal = parseInt(b.cells[0].textContent.replace('#', ''));
                    break;
                case 'patient':
                    aVal = a.cells[1].textContent.trim();
                    bVal = b.cells[1].textContent.trim();
                    break;
                case 'date':
                    aVal = new Date(a.cells[2].textContent.trim());
                    bVal = new Date(b.cells[2].textContent.trim());
                    break;
                case 'status':
                    aVal = a.cells[4].textContent.trim();
                    bVal = b.cells[4].textContent.trim();
                    break;
                default:
                    aVal = a.textContent;
                    bVal = b.textContent;
            }
            
            if (currentSort.direction === 'asc') {
                return aVal > bVal ? 1 : -1;
            } else {
                return aVal < bVal ? 1 : -1;
            }
        });
        
        // Reorder rows in DOM
        rows.forEach(row => tbody.appendChild(row));
        
        // Reapply filters
        filterTable();
    }

    function filterTable() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const statusFilter = document.getElementById('statusFilter');
        const selectedStatus = statusFilter ? statusFilter.value.toLowerCase() : '';
        const tableRows = document.querySelectorAll('#prescriptionsTable tbody tr');
        
        tableRows.forEach(function(row) {
            const text = row.textContent.toLowerCase();
            const statusCell = row.cells[4]; // Status column is the 5th column (index 4)
            const statusBadge = statusCell ? statusCell.querySelector('.badge') : null;
            const rowStatus = statusBadge ? statusBadge.textContent.toLowerCase().trim() : '';
            
            const matchesSearch = !searchTerm || text.includes(searchTerm);
            const matchesStatus = !selectedStatus || selectedStatus === '' || rowStatus === selectedStatus;
            
            if (matchesSearch && matchesStatus) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    // Status filter functionality
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            filterTable();
        });
    }

    // Enhanced alert system for wizard processing
    function showProcessingAlert(title, message, type = 'info', actions = []) {
        const alertId = 'processing-alert-' + Date.now();
        const alertHtml = `
            <div id="${alertId}" class="modal fade" tabindex="-1" role="dialog">
                <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content">
                        <div class="modal-header bg-${type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'primary'} text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                                ${title}
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p class="mb-3">${message}</p>
                            ${actions.length > 0 ? `
                                <div class="d-flex gap-2 justify-content-end">
                                    ${actions.map(action => `
                                        <button type="button" class="btn btn-${action.type || 'secondary'}" 
                                                onclick="${action.onclick}" data-bs-dismiss="modal">
                                            ${action.text}
                                        </button>
                                    `).join('')}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', alertHtml);
        const modal = new bootstrap.Modal(document.getElementById(alertId));
        modal.show();
        
        // Clean up after modal is hidden
        document.getElementById(alertId).addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
        
        return modal;
    }

    // Global function for wizard alerts
    window.showWizardAlert = showProcessingAlert;

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + / to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }

        // Escape to close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(function(modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });

    // Add smooth scrolling to anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading animation to navigation links
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            // Add loading indicator
            const icon = this.querySelector('i');
            if (icon && !icon.classList.contains('fa-spin')) {
                const originalClass = icon.className;
                icon.className = 'fas fa-spinner fa-spin me-1';
                
                // Restore original icon after page load or 3 seconds
                setTimeout(function() {
                    icon.className = originalClass;
                }, 3000);
            }
        });
    });

    // Initialize any charts if Chart.js is loaded
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }

    // Initialize any data tables if needed
    if (typeof DataTable !== 'undefined') {
        initializeDataTables();
    }
});

// Utility Functions
function showNotification(message, type = 'info') {
    // Create a temporary alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Chart initialization function
function initializeCharts() {
    // Prescription status chart
    const statusChartCtx = document.getElementById('statusChart');
    if (statusChartCtx) {
        new Chart(statusChartCtx, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'Approved', 'Rejected'],
                datasets: [{
                    data: [
                        document.querySelectorAll('.badge:contains("Pending")').length,
                        document.querySelectorAll('.badge:contains("Approved")').length,
                        document.querySelectorAll('.badge:contains("Rejected")').length
                    ],
                    backgroundColor: ['#ffc107', '#198754', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// DataTables initialization
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    tables.forEach(function(table) {
        new DataTable(table, {
            responsive: true,
            pageLength: 25,
            order: [[0, 'desc']], // Sort by first column (usually ID) descending
            columnDefs: [
                { targets: [-1], orderable: false } // Disable sorting on Actions column
            ]
        });
    });
}

// Form validation helpers
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        }
    });
    
    return isValid;
}

// API helpers for AJAX requests
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Request failed:', error);
        showNotification('Request failed. Please try again.', 'danger');
        throw error;
    }
}

// Local storage helpers
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Failed to save to localStorage:', error);
    }
}

function loadFromLocalStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (error) {
        console.error('Failed to load from localStorage:', error);
        return null;
    }
}

// Export functions for global use
window.PharmacySystem = {
    showNotification,
    formatDate,
    formatTime,
    validateForm,
    makeRequest,
    saveToLocalStorage,
    loadFromLocalStorage
};
