import { Discovery } from '../types/discovery';
import { formatScore, calculateScorePercentage, truncateText } from '../utils/formatters';

export function createDiscoveryCard(discovery: Discovery): HTMLElement {
    const card = document.createElement('div');
    card.className = `discovery-card ${discovery.type}`;
    
    // Calculate score circle progress
    const percentage = calculateScorePercentage(discovery.innovation_score);
    const circumference = 2 * Math.PI * 28; // radius = 28
    const strokeDashoffset = circumference - (percentage / 100) * circumference;
    
    card.innerHTML = `
        <div class="card-header">
            <span class="type-badge ${discovery.type}">${discovery.type}</span>
            <div class="score-circle">
                <svg width="60" height="60">
                    <circle class="score-circle-bg" cx="30" cy="30" r="28"></circle>
                    <circle 
                        class="score-circle-progress" 
                        cx="30" 
                        cy="30" 
                        r="28"
                        stroke-dasharray="${circumference}"
                        stroke-dashoffset="${strokeDashoffset}"
                    ></circle>
                </svg>
                <span class="score-text">${formatScore(discovery.innovation_score)}</span>
            </div>
        </div>
        
        <h3 class="card-title">${discovery.name}</h3>
        <p class="card-category">${discovery.category}</p>
        
        <p class="card-summary">${truncateText(discovery.summary, 150)}</p>
        
        ${discovery.key_features.length > 0 ? `
            <div class="card-features">
                ${discovery.key_features.slice(0, 3).map(feature => 
                    `<span class="feature-tag">${feature}</span>`
                ).join('')}
            </div>
        ` : ''}
        
        <div class="card-footer">
            <div class="card-links">
                <a href="${discovery.hn_url}" target="_blank" class="card-link">
                    HN Discussion →
                </a>
                ${discovery.url ? `
                    <a href="${discovery.url}" target="_blank" class="card-link">
                        Website →
                    </a>
                ` : ''}
            </div>
            <div class="card-stats">
                <span>▲ ${discovery.hn_score}</span>
                <span>💬 ${discovery.hn_comments}</span>
            </div>
        </div>
    `;
    
    // Add click handler to expand card
    card.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        if (!target.classList.contains('card-link') && !target.closest('.card-link')) {
            showDetailModal(discovery);
        }
    });
    
    return card;
}

function showDetailModal(discovery: Discovery): void {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <button class="modal-close">&times;</button>
            
            <div class="modal-header">
                <h2>${discovery.name}</h2>
                <span class="type-badge ${discovery.type}">${discovery.type}</span>
            </div>
            
            <div class="modal-body">
                <div class="modal-section">
                    <h3>Summary</h3>
                    <p>${discovery.summary}</p>
                </div>
                
                <div class="modal-section">
                    <h3>Why It's Interesting</h3>
                    <p>${discovery.why_interesting}</p>
                </div>
                
                ${discovery.coolness_factor ? `
                    <div class="modal-section">
                        <h3>Coolness Factor</h3>
                        <p>${discovery.coolness_factor}</p>
                    </div>
                ` : ''}
                
                ${discovery.technical_details ? `
                    <div class="modal-section">
                        <h3>Technical Details</h3>
                        <p>${discovery.technical_details}</p>
                    </div>
                ` : ''}
                
                ${discovery.key_features.length > 0 ? `
                    <div class="modal-section">
                        <h3>Key Features</h3>
                        <ul>
                            ${discovery.key_features.map(feature => 
                                `<li>${feature}</li>`
                            ).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="modal-section">
                    <h3>Details</h3>
                    <p><strong>Category:</strong> ${discovery.category}</p>
                    <p><strong>Stage:</strong> ${discovery.stage}</p>
                    <p><strong>Target Audience:</strong> ${discovery.target_audience}</p>
                    ${discovery.founder_info ? `<p><strong>Founder Info:</strong> ${discovery.founder_info}</p>` : ''}
                    ${discovery.business_model ? `<p><strong>Business Model:</strong> ${discovery.business_model}</p>` : ''}
                </div>
            </div>
            
            <div class="modal-footer">
                <a href="${discovery.hn_url}" target="_blank" class="modal-link">
                    View on Hacker News
                </a>
                ${discovery.url ? `
                    <a href="${discovery.url}" target="_blank" class="modal-link">
                        Visit Website
                    </a>
                ` : ''}
            </div>
        </div>
    `;
    
    // Add modal styles
    const style = document.createElement('style');
    style.textContent = `
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 20px;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .modal-content {
            background: var(--bg-card);
            border-radius: 20px;
            max-width: 800px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            padding: 2rem;
            position: relative;
            animation: slideUp 0.3s ease;
        }
        
        @keyframes slideUp {
            from { 
                opacity: 0;
                transform: translateY(50px);
            }
            to { 
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .modal-close {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 2rem;
            cursor: pointer;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.2s ease;
        }
        
        .modal-close:hover {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
        }
        
        .modal-header h2 {
            font-size: 2rem;
            color: var(--primary-color);
        }
        
        .modal-section {
            margin-bottom: 2rem;
        }
        
        .modal-section h3 {
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }
        
        .modal-section p {
            color: var(--text-secondary);
            line-height: 1.6;
        }
        
        .modal-section ul {
            list-style: none;
            padding: 0;
        }
        
        .modal-section li {
            padding: 0.5rem 0;
            padding-left: 1.5rem;
            position: relative;
            color: var(--text-secondary);
        }
        
        .modal-section li::before {
            content: "→";
            position: absolute;
            left: 0;
            color: var(--primary-color);
        }
        
        .modal-footer {
            display: flex;
            gap: 1rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border-color);
        }
        
        .modal-link {
            padding: 0.75rem 1.5rem;
            background: var(--primary-color);
            color: white;
            text-decoration: none;
            border-radius: 30px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .modal-link:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(modal);
    
    // Close handlers
    const closeBtn = modal.querySelector('.modal-close');
    closeBtn?.addEventListener('click', () => {
        modal.remove();
        style.remove();
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
            style.remove();
        }
    });
}