// Claude Framework Dashboard JavaScript

// Auto-refresh functionality
let autoRefresh = true;
let refreshInterval;

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    startAutoRefresh();
});

function initializeDashboard() {
    console.log('Claude Framework Dashboard initialized');
    updateLastRefresh();
}

function refreshDashboard() {
    location.reload();
}

function viewLogs() {
    // Placeholder - would open logs view
    alert('Logs view would open here');
}

function checkHealth() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            console.log('Health check:', data);
            alert('Health check completed - see console for details');
        })
        .catch(error => {
            console.error('Health check failed:', error);
            alert('Health check failed - see console for details');
        });
}

function startAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }

    refreshInterval = setInterval(() => {
        if (autoRefresh) {
            refreshDashboard();
        }
    }, 30000); // Refresh every 30 seconds
}

function toggleAutoRefresh() {
    autoRefresh = !autoRefresh;
    console.log('Auto-refresh:', autoRefresh ? 'enabled' : 'disabled');
}

function updateLastRefresh() {
    const now = new Date().toLocaleString();
    const timestampElements = document.querySelectorAll('.timestamp');
    timestampElements.forEach(el => {
        if (el.textContent.includes('Last updated:')) {
            el.textContent = `Last updated: ${now}`;
        }
    });
}

// Export functions for global access
window.refreshDashboard = refreshDashboard;
window.viewLogs = viewLogs;
window.checkHealth = checkHealth;
window.toggleAutoRefresh = toggleAutoRefresh;