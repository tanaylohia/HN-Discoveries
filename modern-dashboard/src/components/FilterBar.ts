import { FilterType } from '../types/discovery';

interface FilterBarCallbacks {
    onTypeChange: (type: FilterType) => void;
    onSearchChange: (query: string) => void;
    onRefresh: () => void;
}

export function createFilterBar(callbacks: FilterBarCallbacks): HTMLElement {
    const filterBar = document.createElement('div');
    filterBar.className = 'filter-bar';
    
    filterBar.innerHTML = `
        <div class="container">
            <div class="filter-content">
                <div class="filter-buttons">
                    <button class="filter-btn active" data-type="all">All</button>
                    <button class="filter-btn" data-type="startup">Startups</button>
                    <button class="filter-btn" data-type="innovation">Innovations</button>
                </div>
                
                <div class="search-box">
                    <input 
                        type="text" 
                        class="search-input" 
                        placeholder="Search discoveries..."
                        id="searchInput"
                    >
                    <span class="search-icon">🔍</span>
                </div>
                
                <button class="refresh-btn" id="refreshBtn">
                    <span class="refresh-icon">↻</span>
                    Refresh
                </button>
            </div>
        </div>
    `;
    
    // Add event listeners
    const filterButtons = filterBar.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Update active state
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Trigger callback
            const type = (btn as HTMLElement).dataset.type as FilterType;
            callbacks.onTypeChange(type);
        });
    });
    
    // Search input
    const searchInput = filterBar.querySelector('#searchInput') as HTMLInputElement;
    let searchTimeout: number;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            callbacks.onSearchChange((e.target as HTMLInputElement).value);
        }, 300);
    });
    
    // Refresh button
    const refreshBtn = filterBar.querySelector('#refreshBtn') as HTMLButtonElement;
    refreshBtn.addEventListener('click', () => {
        callbacks.onRefresh();
    });
    
    return filterBar;
}