let currentFilter = 'all';
let allDiscoveries = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadDiscoveries();
    setupEventListeners();
    
    // Auto-refresh every 5 minutes
    setInterval(loadDiscoveries, 5 * 60 * 1000);
});

function setupEventListeners() {
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            renderDiscoveries();
        });
    });
    
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', () => {
        triggerRefresh();
    });
}

async function loadDiscoveries() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const discoveriesContainer = document.getElementById('discoveries');
    
    loading.style.display = 'block';
    error.style.display = 'none';
    discoveriesContainer.innerHTML = '';
    
    try {
        // Load from the reports directory
        const response = await fetch('/reports/latest.json');
        if (!response.ok) throw new Error('Failed to load discoveries');
        
        const data = await response.json();
        allDiscoveries = data.discoveries;
        
        updateStats(data.metadata);
        renderDiscoveries();
        
    } catch (err) {
        error.textContent = `Error loading discoveries: ${err.message}`;
        error.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
}

function updateStats(metadata) {
    document.getElementById('totalCount').textContent = metadata.total_discoveries;
    document.getElementById('startupCount').textContent = metadata.total_startups;
    document.getElementById('innovationCount').textContent = metadata.total_innovations;
    document.getElementById('lastUpdate').textContent = formatTime(metadata.generated_at_ist);
}

function formatTime(timeStr) {
    // Extract just the time portion
    const match = timeStr.match(/at (\d+:\d+ [AP]M)/);
    return match ? match[1] : timeStr;
}

function renderDiscoveries() {
    const container = document.getElementById('discoveries');
    container.innerHTML = '';
    
    const filtered = currentFilter === 'all' 
        ? allDiscoveries 
        : allDiscoveries.filter(d => d.type === currentFilter);
    
    filtered.forEach(discovery => {
        const card = createDiscoveryCard(discovery);
        container.appendChild(card);
    });
}

function createDiscoveryCard(discovery) {
    const card = document.createElement('div');
    card.className = 'discovery-card';
    
    const typeClass = discovery.type === 'startup' ? 'type-startup' : 'type-innovation';
    
    card.innerHTML = `
        <div class="discovery-header">
            <span class="discovery-type ${typeClass}">${discovery.type}</span>
            <span class="discovery-score">${discovery.innovation_score.toFixed(1)}/10</span>
        </div>
        
        <h3 class="discovery-title">${discovery.name}</h3>
        <div class="discovery-category">${discovery.category}</div>
        
        <p class="discovery-summary">${discovery.summary}</p>
        
        ${discovery.why_interesting ? `
            <div class="discovery-why">
                <strong>Why it's interesting:</strong> ${discovery.why_interesting}
            </div>
        ` : ''}
        
        ${discovery.key_features && discovery.key_features.length > 0 ? `
            <div class="discovery-features">
                ${discovery.key_features.map(f => `<span class="feature-tag">${f}</span>`).join('')}
            </div>
        ` : ''}
        
        <div class="discovery-footer">
            <div class="discovery-links">
                <a href="${discovery.hn_url}" target="_blank" class="discovery-link">
                    💬 HN Discussion
                </a>
                ${discovery.url ? `
                    <a href="${discovery.url}" target="_blank" class="discovery-link">
                        🔗 Website
                    </a>
                ` : ''}
            </div>
            <div class="discovery-stats">
                <span class="discovery-stat">▲ ${discovery.hn_score}</span>
                <span class="discovery-stat">💬 ${discovery.hn_comments}</span>
            </div>
        </div>
    `;
    
    return card;
}

async function triggerRefresh() {
    const refreshBtn = document.getElementById('refreshBtn');
    refreshBtn.disabled = true;
    refreshBtn.textContent = '⏳ Refreshing...';
    
    try {
        // In production, this would trigger the Python script
        // For now, we'll simulate it
        const response = await fetch('/api/refresh', {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Refresh failed');
        
        // Wait a bit for the process to complete
        setTimeout(() => {
            loadDiscoveries();
            refreshBtn.disabled = false;
            refreshBtn.textContent = '🔄 Refresh Now';
        }, 3000);
        
    } catch (err) {
        alert('Refresh failed. Please try again.');
        refreshBtn.disabled = false;
        refreshBtn.textContent = '🔄 Refresh Now';
    }
}