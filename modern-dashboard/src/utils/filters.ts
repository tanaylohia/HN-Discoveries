import { Discovery, FilterOptions } from '../types/discovery';

export function filterDiscoveries(discoveries: Discovery[], options: FilterOptions): Discovery[] {
    return discoveries.filter(discovery => {
        // Filter by type
        if (options.type !== 'all' && discovery.type !== options.type) {
            return false;
        }

        // Filter by search query
        if (options.searchQuery) {
            const query = options.searchQuery.toLowerCase();
            const searchableText = [
                discovery.name,
                discovery.title,
                discovery.summary,
                discovery.category,
                discovery.why_interesting
            ].join(' ').toLowerCase();
            
            if (!searchableText.includes(query)) {
                return false;
            }
        }

        // Filter by score range
        if (discovery.innovation_score < options.minScore || 
            discovery.innovation_score > options.maxScore) {
            return false;
        }

        // Filter by categories if specified
        if (options.categories.length > 0) {
            const discoveryCategories = discovery.category.toLowerCase().split(',').map(c => c.trim());
            const hasMatchingCategory = options.categories.some(cat => 
                discoveryCategories.some(dCat => dCat.includes(cat.toLowerCase()))
            );
            if (!hasMatchingCategory) {
                return false;
            }
        }

        return true;
    });
}

export function extractUniqueCategories(discoveries: Discovery[]): string[] {
    const categoriesSet = new Set<string>();
    
    discoveries.forEach(discovery => {
        const categories = discovery.category.split(',').map(c => c.trim());
        categories.forEach(cat => categoriesSet.add(cat));
    });
    
    return Array.from(categoriesSet).sort();
}