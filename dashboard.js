// Dashboard JavaScript functionality

// Global variables
let currentFlightData = [];
let currentInsights = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Add event listeners
    addEventListeners();
    
    // Check for chart resize needs
    window.addEventListener('resize', function() {
        resizeCharts();
    });
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Add event listeners
function addEventListeners() {
    // Refresh insights button
    const refreshBtn = document.getElementById('refresh-insights');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshInsights);
    }
    
    // Export functionality
    const exportBtn = document.getElementById('export-data');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportData);
    }
    
    // Chart interaction handlers
    addChartInteractionHandlers();
}

// Add chart interaction handlers
function addChartInteractionHandlers() {
    // Price trend chart interactions
    const priceTrendElement = document.getElementById('price-trend-chart');
    if (priceTrendElement) {
        priceTrendElement.on('plotly_click', function(data) {
            const pointIndex = data.points[0].pointIndex;
            const selectedDate = data.points[0].x;
            console.log('Selected date:', selectedDate);
            highlightTableRow(selectedDate);
        });
    }
    
    // Routes chart interactions
    const routesElement = document.getElementById('routes-chart');
    if (routesElement) {
        routesElement.on('plotly_click', function(data) {
            const selectedRoute = data.points[0].x;
            console.log('Selected route:', selectedRoute);
            filterTableByRoute(selectedRoute);
        });
    }
}

// Highlight table row based on date
function highlightTableRow(date) {
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        const dateCell = row.cells[0];
        if (dateCell && dateCell.textContent.includes(date)) {
            row.classList.add('table-warning');
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            row.classList.remove('table-warning');
        }
    });
}

// Filter table by route
function filterTableByRoute(route) {
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        const routeInfo = row.textContent;
        if (routeInfo.includes(route)) {
            row.style.display = '';
            row.classList.add('table-info');
        } else {
            row.style.display = 'none';
            row.classList.remove('table-info');
        }
    });
    
    // Add reset filter button
    showResetFilterButton();
}

// Show reset filter button
function showResetFilterButton() {
    let resetBtn = document.getElementById('reset-filter');
    if (!resetBtn) {
        resetBtn = document.createElement('button');
        resetBtn.id = 'reset-filter';
        resetBtn.className = 'btn btn-outline-secondary btn-sm ms-2';
        resetBtn.innerHTML = '<i class="fas fa-times me-1"></i>Reset Filter';
        resetBtn.addEventListener('click', resetTableFilter);
        
        const tableHeader = document.querySelector('.card-header h5');
        if (tableHeader) {
            tableHeader.parentNode.appendChild(resetBtn);
        }
    }
}

// Reset table filter
function resetTableFilter() {
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.style.display = '';
        row.classList.remove('table-info', 'table-warning');
    });
    
    const resetBtn = document.getElementById('reset-filter');
    if (resetBtn) {
        resetBtn.remove();
    }
}

// Refresh insights from API
async function refreshInsights() {
    const refreshBtn = document.getElementById('refresh-insights');
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Refreshing...';
    }
    
    try {
        const response = await fetch('/api/refresh-insights', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                flight_data: currentFlightData
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            updateInsightsDisplay(data.insights);
            showToast('Insights refreshed successfully', 'success');
        } else {
            throw new Error('Failed to refresh insights');
        }
    } catch (error) {
        console.error('Error refreshing insights:', error);
        showToast('Failed to refresh insights', 'error');
    } finally {
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync me-1"></i>Refresh Insights';
        }
    }
}

// Update insights display
function updateInsightsDisplay(insights) {
    // Update price insights
    const priceInsightsElement = document.querySelector('.price-insights');
    if (priceInsightsElement) {
        priceInsightsElement.textContent = insights.price_insights;
    }
    
    // Update demand patterns
    const demandPatternsElement = document.querySelector('.demand-patterns');
    if (demandPatternsElement) {
        demandPatternsElement.textContent = insights.demand_patterns;
    }
    
    // Update recommendations
    const recommendationsElement = document.querySelector('.recommendations-list');
    if (recommendationsElement) {
        recommendationsElement.innerHTML = '';
        insights.recommendations.forEach(recommendation => {
            const li = document.createElement('li');
            li.className = 'mb-2';
            li.innerHTML = `<i class="fas fa-check-circle text-success me-2"></i>${recommendation}`;
            recommendationsElement.appendChild(li);
        });
    }
    
    // Update key statistics
    updateKeyStatistics(insights.key_statistics);
}

// Update key statistics
function updateKeyStatistics(stats) {
    const totalFlightsElement = document.querySelector('.total-flights');
    if (totalFlightsElement) {
        totalFlightsElement.textContent = stats.total_flights;
    }
    
    const avgPriceElement = document.querySelector('.avg-price');
    if (avgPriceElement) {
        avgPriceElement.textContent = `$${stats.avg_price}`;
    }
    
    const cheapestDayElement = document.querySelector('.cheapest-day');
    if (cheapestDayElement) {
        cheapestDayElement.textContent = stats.cheapest_day;
    }
    
    const expensiveDayElement = document.querySelector('.expensive-day');
    if (expensiveDayElement) {
        expensiveDayElement.textContent = stats.most_expensive_day;
    }
}

// Export data functionality
function exportData() {
    const csvContent = convertToCSV(currentFlightData);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'flight_data.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast('Data exported successfully', 'success');
    }
}

// Convert data to CSV
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [];
    
    // Add headers
    csvRows.push(headers.join(','));
    
    // Add data rows
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            return typeof value === 'string' ? `"${value}"` : value;
        });
        csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = getOrCreateToastContainer();
    const toast = createToast(message, type);
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Get or create toast container
function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
    }
    return container;
}

// Create toast element
function createToast(message, type) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const iconClass = type === 'success' ? 'fa-check-circle text-success' : 
                     type === 'error' ? 'fa-exclamation-circle text-danger' : 
                     'fa-info-circle text-info';
    
    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas ${iconClass} me-2"></i>
            <strong class="me-auto">Flight Analytics</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    return toast;
}

// Resize charts on window resize
function resizeCharts() {
    const chartElements = ['price-trend-chart', 'routes-chart', 'demand-chart'];
    chartElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            Plotly.Plots.resize(element);
        }
    });
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Add loading state to form submissions
document.addEventListener('submit', function(e) {
    if (e.target.tagName === 'FORM') {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        }
    }
});

// Performance monitoring
window.addEventListener('load', function() {
    const loadTime = performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart;
    console.log('Page load time:', loadTime, 'ms');
});
