// Admin Panel JavaScript Functionality
let currentSection = 'dashboard';
let charts = {};

// Section Navigation
function showSection(sectionName) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.admin-menu-item').forEach(m => m.classList.remove('active'));
    
    document.getElementById(sectionName).classList.add('active');
    event.target.classList.add('active');
    
    currentSection = sectionName;
    
    if (sectionName === 'analytics') {
        setTimeout(initCharts, 100);
    } else if (sectionName === 'users') {
        loadUsers();
    } else if (sectionName === 'ads') {
        loadAds();
    } else if (sectionName === 'content') {
        loadContent();
    } else if (sectionName === 'reports') {
        loadReports();
    } else if (sectionName === 'revenue') {
        setTimeout(initRevenueChart, 100);
    }
}

// Dashboard Stats Animation with real data
async function animateStats() {
    try {
        const response = await fetch('/admin/stats');
        const stats = await response.json();
        
        const statsMap = [
            { id: 'totalUsers', target: stats.totalUsers },
            { id: 'activeSessions', target: stats.activeSessions },
            { id: 'totalDownloads', target: stats.totalDownloads },
            { id: 'activeInstalls', target: stats.activeInstalls },
            { id: 'totalVideos', target: stats.totalVideos },
            { id: 'totalViews', target: stats.totalViews },
            { id: 'adViews', target: stats.adViews },
            { id: 'totalRevenue', target: stats.totalRevenue }
        ];
        
        statsMap.forEach(stat => {
            const element = document.getElementById(stat.id);
            if (element) {
                animateNumber(element, stat.target, stat.id === 'totalRevenue');
            }
        });
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function animateNumber(element, target, isCurrency = false) {
    let current = 0;
    const increment = target / 100;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        let displayValue = Math.floor(current);
        if (isCurrency) {
            displayValue = '$' + displayValue.toLocaleString();
        } else if (displayValue >= 1000000) {
            displayValue = (displayValue / 1000000).toFixed(1) + 'M';
        } else if (displayValue >= 1000) {
            displayValue = (displayValue / 1000).toFixed(1) + 'K';
        }
        
        element.textContent = displayValue;
    }, 20);
}

// Charts Initialization with real data
function initCharts() {
    fetch('/admin/chart-data')
        .then(response => response.json())
        .then(data => {
            initUserChart(data.userGrowth);
            initViewsChart(data.viewsData);
            initRevenueChart(data.revenueBreakdown);
            initCategoryChart(data.categories);
        })
        .catch(error => console.error('Error loading chart data:', error));
}

function initUserChart(userData) {
    const ctx = document.getElementById('userChart');
    if (!ctx || charts.userChart) return;
    
    charts.userChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'New Sessions',
                data: userData,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { 
                    labels: { color: '#fff', font: { size: 12 } } 
                } 
            },
            scales: {
                y: { 
                    ticks: { color: '#fff', font: { size: 11 } }, 
                    grid: { color: 'rgba(255,255,255,0.1)' } 
                },
                x: { 
                    ticks: { color: '#fff', font: { size: 11 } }, 
                    grid: { color: 'rgba(255,255,255,0.1)' } 
                }
            }
        }
    });
}

function initViewsChart(viewsData) {
    const ctx = document.getElementById('viewsChart');
    if (!ctx || charts.viewsChart) return;
    
    charts.viewsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Views',
                data: viewsData,
                backgroundColor: 'rgba(102, 126, 234, 0.8)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { 
                    labels: { color: '#fff', font: { size: 12 } } 
                } 
            },
            scales: {
                y: { 
                    ticks: { color: '#fff', font: { size: 11 } }, 
                    grid: { color: 'rgba(255,255,255,0.1)' } 
                },
                x: { 
                    ticks: { color: '#fff', font: { size: 11 } }, 
                    grid: { color: 'rgba(255,255,255,0.1)' } 
                }
            }
        }
    });
}

function initRevenueChart(revenueData) {
    const ctx = document.getElementById('revenueChart');
    if (!ctx || charts.revenueChart) return;
    
    charts.revenueChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Ads', 'Premium', 'Creator Fund'],
            datasets: [{
                data: revenueData,
                backgroundColor: ['#667eea', '#764ba2', '#f093fb']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { 
                    labels: { color: '#fff', font: { size: 12 } } 
                } 
            }
        }
    });
}

function initCategoryChart(categoryData) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx || charts.categoryChart) return;
    
    charts.categoryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Music', 'Movies', 'Sports', 'Gaming', 'Other'],
            datasets: [{
                data: categoryData,
                backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#4ade80', '#f59e0b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { 
                    labels: { color: '#fff', font: { size: 12 } } 
                } 
            }
        }
    });
}

function initRevenueChart() {
    const ctx = document.getElementById('monthlyRevenueChart');
    if (!ctx || charts.monthlyRevenueChart) return;
    
    charts.monthlyRevenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Revenue ($)',
                data: [8500, 9200, 10100, 11300, 10800, 12450],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#fff' } } },
            scales: {
                y: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                x: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } }
            }
        }
    });
}

// Users Management
async function loadUsers() {
    const tbody = document.getElementById('usersTable');
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Loading users...</td></tr>';
    
    try {
        const response = await fetch('/admin/users');
        const users = await response.json();
        
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No users found</td></tr>';
            return;
        }
        
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.email}</td>
                <td>${new Date(user.joined).toLocaleDateString()}</td>
                <td><span style="color: ${user.status === 'active' ? '#4ade80' : '#ef4444'}">${user.status}</span></td>
                <td>${user.videos || 0}</td>
                <td>${user.views || 0}</td>
                <td>
                    <button class="action-btn btn-edit" onclick="editUser('${user.id}')">Edit</button>
                    <button class="action-btn btn-delete" onclick="deleteUser('${user.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #ef4444;">Failed to load users</td></tr>';
    }
}

// Ads Management
function showUploadAdForm() {
    document.getElementById('uploadAdForm').style.display = 'block';
}

function hideUploadAdForm() {
    document.getElementById('uploadAdForm').style.display = 'none';
    document.getElementById('adUploadForm').reset();
}

async function uploadAd() {
    const title = document.getElementById('adTitle').value;
    const file = document.getElementById('adVideoFile').files[0];
    const clickUrl = document.getElementById('adClickUrl').value;
    
    if (!title || !file) {
        alert('Please fill in all required fields');
        return;
    }
    
    const formData = new FormData();
    formData.append('title', title);
    formData.append('video', file);
    formData.append('clickUrl', clickUrl);
    
    try {
        const response = await fetch('/admin/upload-ad', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            alert('Ad uploaded successfully!');
            hideUploadAdForm();
            loadAds();
        } else {
            alert('Failed to upload ad');
        }
    } catch (error) {
        alert('Upload failed: ' + error.message);
    }
}

async function loadAds() {
    const tbody = document.getElementById('adsTable');
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Loading ads...</td></tr>';
    
    try {
        const response = await fetch('/admin/ads');
        const ads = await response.json();
        
        if (ads.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No ads uploaded yet</td></tr>';
            return;
        }
        
        tbody.innerHTML = ads.map(ad => `
            <tr>
                <td>${ad.title}</td>
                <td><video width="100" height="60" controls><source src="${ad.videoFile}" type="video/mp4"></video></td>
                <td>${ad.clickUrl ? `<a href="${ad.clickUrl}" target="_blank">${ad.clickUrl}</a>` : 'N/A'}</td>
                <td>${ad.views || 0}</td>
                <td>${new Date(ad.uploaded).toLocaleDateString()}</td>
                <td>
                    <button class="action-btn btn-delete" onclick="deleteAd('${ad.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #ef4444;">Failed to load ads</td></tr>';
    }
}

// Content Management
async function loadContent() {
    const tbody = document.getElementById('contentTable');
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Loading content...</td></tr>';
    
    try {
        const response = await fetch('/admin/content');
        const content = await response.json();
        
        if (content.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No content found</td></tr>';
            return;
        }
        
        tbody.innerHTML = content.map(item => `
            <tr>
                <td>${item.title}</td>
                <td>${item.category}</td>
                <td>${item.views || 0}</td>
                <td><span style="color: ${item.status === 'approved' ? '#4ade80' : '#f59e0b'}">${item.status}</span></td>
                <td>${item.reports || 0}</td>
                <td>
                    <button class="action-btn btn-edit" onclick="moderateContent('${item.id}', 'approve')">Approve</button>
                    <button class="action-btn btn-delete" onclick="moderateContent('${item.id}', 'remove')">Remove</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #ef4444;">Failed to load content</td></tr>';
    }
}

// Reports Management
async function loadReports() {
    const tbody = document.getElementById('reportsTable');
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Loading reports...</td></tr>';
    
    try {
        const response = await fetch('/admin/reports');
        const reports = await response.json();
        
        if (reports.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No reports found</td></tr>';
            return;
        }
        
        tbody.innerHTML = reports.map(report => `
            <tr>
                <td>${report.contentId}</td>
                <td>${report.reason}</td>
                <td>${report.reporter}</td>
                <td>${new Date(report.date).toLocaleDateString()}</td>
                <td><span style="color: ${report.status === 'resolved' ? '#4ade80' : '#f59e0b'}">${report.status}</span></td>
                <td>
                    <button class="action-btn btn-edit" onclick="resolveReport('${report.id}')">Resolve</button>
                    <button class="action-btn btn-delete" onclick="dismissReport('${report.id}')">Dismiss</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #ef4444;">Failed to load reports</td></tr>';
    }
}

// Action Functions
async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    try {
        const response = await fetch(`/admin/users/${userId}`, { method: 'DELETE' });
        if (response.ok) {
            loadUsers();
        } else {
            alert('Failed to delete user');
        }
    } catch (error) {
        alert('Delete failed: ' + error.message);
    }
}

async function deleteAd(adId) {
    if (!confirm('Are you sure you want to delete this ad?')) return;
    
    try {
        const response = await fetch(`/admin/ads/${adId}`, { method: 'DELETE' });
        if (response.ok) {
            loadAds();
        } else {
            alert('Failed to delete ad');
        }
    } catch (error) {
        alert('Delete failed: ' + error.message);
    }
}

async function moderateContent(contentId, action) {
    try {
        const response = await fetch(`/admin/content/${contentId}/${action}`, { method: 'POST' });
        if (response.ok) {
            loadContent();
        } else {
            alert(`Failed to ${action} content`);
        }
    } catch (error) {
        alert(`Action failed: ${error.message}`);
    }
}

async function resolveReport(reportId) {
    try {
        const response = await fetch(`/admin/reports/${reportId}/resolve`, { method: 'POST' });
        if (response.ok) {
            loadReports();
        } else {
            alert('Failed to resolve report');
        }
    } catch (error) {
        alert('Action failed: ' + error.message);
    }
}

async function dismissReport(reportId) {
    try {
        const response = await fetch(`/admin/reports/${reportId}/dismiss`, { method: 'POST' });
        if (response.ok) {
            loadReports();
        } else {
            alert('Failed to dismiss report');
        }
    } catch (error) {
        alert('Action failed: ' + error.message);
    }
}

// Initialize Admin Panel
document.addEventListener('DOMContentLoaded', function() {
    animateStats();
    
    // Auto-refresh stats every 30 seconds
    setInterval(() => {
        if (currentSection === 'dashboard') {
            animateStats();
        }
    }, 30000);
});

// Mobile sidebar toggle
function toggleSidebar() {
    const sidebar = document.querySelector('.admin-sidebar');
    sidebar.classList.toggle('active');
}