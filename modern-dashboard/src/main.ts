import './styles/main.css';
import { Discovery, FilterType, FilterOptions } from './types/discovery';
import { fetchDiscoveries } from './utils/api';
import { filterDiscoveries } from './utils/filters';
import { createHeader } from './components/Header';
import { createFilterBar } from './components/FilterBar';
import { createDiscoveryCard } from './components/DiscoveryCard';

class App {
    private discoveries: Discovery[] = [];
    private filteredDiscoveries: Discovery[] = [];
    private filterOptions: FilterOptions = {
        type: 'all',
        searchQuery: '',
        minScore: 0,
        maxScore: 10,
        categories: []
    };
    
    private container: HTMLElement;
    private gridContainer: HTMLElement | null = null;
    
    constructor() {
        this.container = document.getElementById('app')!;
        this.init();
    }
    
    private async init() {
        // Show loading state
        this.showLoading();
        
        try {
            // Fetch data
            const data = await fetchDiscoveries();
            this.discoveries = data.discoveries;
            this.filteredDiscoveries = [...this.discoveries];
            
            // Build UI
            this.buildUI(data.metadata);
            
            // Initial render
            this.renderDiscoveries();
        } catch (error) {
            this.showError('Failed to load discoveries. Please try refreshing the page.');
            console.error('Error loading data:', error);
        }
    }
    
    private buildUI(metadata: any) {
        // Clear container
        this.container.innerHTML = '';
        
        // Add header
        const header = createHeader(metadata);
        this.container.appendChild(header);
        
        // Add filter bar
        const filterBar = createFilterBar({
            onTypeChange: (type: FilterType) => {
                this.filterOptions.type = type;
                this.applyFilters();
            },
            onSearchChange: (query: string) => {
                this.filterOptions.searchQuery = query;
                this.applyFilters();
            },
            onRefresh: () => {
                this.handleRefresh();
            }
        });
        this.container.appendChild(filterBar);
        
        // Add main content area
        const main = document.createElement('main');
        main.className = 'container';
        
        // Create grid container
        this.gridContainer = document.createElement('div');
        this.gridContainer.className = 'discoveries-grid';
        main.appendChild(this.gridContainer);
        
        this.container.appendChild(main);
    }
    
    private applyFilters() {
        this.filteredDiscoveries = filterDiscoveries(this.discoveries, this.filterOptions);
        this.renderDiscoveries();
    }
    
    private renderDiscoveries() {
        if (!this.gridContainer) return;
        
        // Clear existing cards
        this.gridContainer.innerHTML = '';
        
        if (this.filteredDiscoveries.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // Sort by score (highest first)
        const sorted = [...this.filteredDiscoveries].sort((a, b) => 
            b.innovation_score - a.innovation_score
        );
        
        // Create and append cards
        sorted.forEach(discovery => {
            const card = createDiscoveryCard(discovery);
            this.gridContainer!.appendChild(card);
        });
    }
    
    private showLoading() {
        this.container.innerHTML = `
            <div class="loading-container">
                <div class="loader"></div>
            </div>
        `;
    }
    
    private showError(message: string) {
        this.container.innerHTML = `
            <div class="container">
                <div class="empty-state">
                    <h3>Error</h3>
                    <p>${message}</p>
                </div>
            </div>
        `;
    }
    
    private showEmptyState() {
        if (!this.gridContainer) return;
        
        this.gridContainer.innerHTML = `
            <div class="empty-state">
                <h3>No discoveries found</h3>
                <p>Try adjusting your filters or search query.</p>
            </div>
        `;
    }
    
    private async handleRefresh() {
        const refreshBtn = document.querySelector('#refreshBtn') as HTMLButtonElement;
        if (!refreshBtn) return;
        
        // Update button state
        refreshBtn.disabled = true;
        refreshBtn.classList.add('loading');
        refreshBtn.innerHTML = '<span class="refresh-icon">↻</span> Refreshing...';
        
        try {
            // Call the backend API to trigger a refresh
            const response = await fetch('/api/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error('Refresh failed');
            }
            
            // Wait a bit for the backend to process
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Reload the data
            await this.init();
            
        } catch (error) {
            console.error('Error refreshing:', error);
            alert('Failed to refresh data. Please try again.');
        } finally {
            // Reset button state
            refreshBtn.disabled = false;
            refreshBtn.classList.remove('loading');
            refreshBtn.innerHTML = '<span class="refresh-icon">↻</span> Refresh';
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
});