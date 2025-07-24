import { Metadata } from '../types/discovery';

export function createHeader(metadata: Metadata): HTMLElement {
    const header = document.createElement('header');
    header.className = 'header';
    
    header.innerHTML = `
        <div class="container">
            <div class="header-content">
                <h1 class="title">HN Discoveries</h1>
                <p class="subtitle">Curated Startups & Technical Innovations from Hacker News</p>
                
                <div class="stats-bar">
                    <div class="stat">
                        <span class="stat-number">${metadata.total_discoveries}</span>
                        <span class="stat-label">Total Discoveries</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">${metadata.total_startups}</span>
                        <span class="stat-label">Startups</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">${metadata.total_innovations}</span>
                        <span class="stat-label">Innovations</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">${new Date(metadata.generated_at).toLocaleTimeString('en-US', { 
                            hour: 'numeric', 
                            minute: '2-digit',
                            hour12: true 
                        })}</span>
                        <span class="stat-label">Last Updated</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return header;
}