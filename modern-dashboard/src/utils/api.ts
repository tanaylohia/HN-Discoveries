import { DiscoveryData } from '../types/discovery';

export async function fetchDiscoveries(): Promise<DiscoveryData> {
    try {
        // Try to fetch from the server
        const response = await fetch('/reports/latest.json');
        if (!response.ok) {
            throw new Error('Failed to fetch data');
        }
        return await response.json();
    } catch (error) {
        // Fallback: try to load from parent directory
        try {
            const response = await fetch('../reports/latest.json');
            if (!response.ok) {
                throw new Error('Failed to fetch data');
            }
            return await response.json();
        } catch {
            // If all fails, return mock data for demo
            console.warn('Using mock data. Run "py main.py --run-once" to generate real data.');
            return getMockData();
        }
    }
}

function getMockData(): DiscoveryData {
    return {
        metadata: {
            timestamp: new Date().toISOString(),
            generated_at: new Date().toISOString(),
            generated_at_ist: new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }),
            total_discoveries: 0,
            total_startups: 0,
            total_innovations: 0
        },
        discoveries: []
    };
}