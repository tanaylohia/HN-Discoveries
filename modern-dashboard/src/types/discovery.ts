export interface Discovery {
    id: number;
    type: 'startup' | 'innovation';
    title: string;
    name: string;
    url: string | null;
    hn_url: string;
    hn_score: number;
    hn_comments: number;
    posted_at: string;
    category: string;
    stage: string;
    innovation_score: number;
    summary: string;
    why_interesting: string;
    coolness_factor: string;
    key_features: string[];
    target_audience: string;
    technical_details: string;
    business_model: string;
    founder_info: string;
}

export interface Metadata {
    timestamp: string;
    generated_at: string;
    generated_at_ist: string;
    total_discoveries: number;
    total_startups: number;
    total_innovations: number;
}

export interface DiscoveryData {
    metadata: Metadata;
    discoveries: Discovery[];
}

export type FilterType = 'all' | 'startup' | 'innovation';

export interface FilterOptions {
    type: FilterType;
    searchQuery: string;
    minScore: number;
    maxScore: number;
    categories: string[];
}