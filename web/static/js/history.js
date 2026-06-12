// History page JavaScript

let currentLimit = 100;
let allAlerts = [];

// Load alerts
function loadAlerts() {
    const ruleFilter = document.getElementById('filter-rule').value;
    const severityFilter = document.getElementById('filter-severity').value;
    const dateFrom = document.getElementById('filter-date-from').value;
    const dateTo = document.getElementById('filter-date-to').value;
    
    let url = `/api/alerts?limit=${currentLimit}`;
    if (ruleFilter) url += `&rule=${ruleFilter}`;
    if (severityFilter) url += `&severity=${severityFilter}`;
    if (dateFrom) url += `&date_from=${dateFrom}`;
    if (dateTo) url += `&date_to=${dateTo}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Trier du plus récent au plus ancien
            allAlerts = data.sort((a, b) => {
                const timeA = new Date(a.ts || 0).getTime();
                const timeB = new Date(b.ts || 0).getTime();
                return timeB - timeA; // Plus récent en premier
            });
            displayAlerts(allAlerts);
        })
        .catch(error => {
            console.error('Error loading alerts:', error);
            document.getElementById('alerts-tbody').innerHTML = 
                '<tr><td colspan="7" class="text-center text-danger">Erreur lors du chargement des alertes</td></tr>';
        });
}

// Display alerts in table
function displayAlerts(alerts) {
    const tbody = document.getElementById('alerts-tbody');
    
    if (alerts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Aucune alerte trouvée</td></tr>';
        return;
    }
    
    // Traduire les règles en français
    const ruleTranslations = {
        'PORT_SCAN': 'Scan de Ports',
        'SYN_FLOOD': 'Inondation SYN',
        'PING_SWEEP': 'Balayage Ping',
        'SUSPICIOUS_PORT': 'Port Suspect',
        'ANOMALY_HIGH_RATE': 'Anomalie - Taux Élevé',
        'ANOMALY_LARGE_PAYLOAD': 'Anomalie - Charge Utile Large',
        'ANOMALY_ML': 'Anomalie Machine Learning'
    };
    
    tbody.innerHTML = alerts.map(alert => {
        const severityBadge = getSeverityBadge(alert.severity);
        const ruleName = ruleTranslations[alert.rule] || alert.rule;
        const protocol = alert.meta?.protocol || alert.meta?.proto || 'N/A';
        const srcPort = alert.meta?.src_port || alert.meta?.sport || '';
        const dstPort = alert.meta?.dst_port || alert.meta?.dport || '';
        
        return `
            <tr onclick="showAlertDetail('${alert.id}')" style="cursor: pointer; transition: all 0.2s;">
                <td>${formatTimestamp(alert.ts)}</td>
                <td>
                    <strong>${ruleName}</strong><br>
                    <small class="text-muted"><code>${alert.rule}</code></small>
                </td>
                <td>${severityBadge}</td>
                <td>
                    ${alert.src || 'N/A'}
                    ${srcPort ? `<br><small class="text-muted">Port: ${srcPort}</small>` : ''}
                </td>
                <td>
                    ${alert.dst || 'N/A'}
                    ${dstPort ? `<br><small class="text-muted">Port: ${dstPort}</small>` : ''}
                </td>
                <td>
                    ${truncate(alert.description, 60)}
                    ${protocol !== 'N/A' ? `<br><small class="text-muted">Protocole: ${protocol}</small>` : ''}
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); showAlertDetail('${alert.id}')" title="Voir les détails">
                        <i class="bi bi-eye"></i> Détails
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Show alert detail modal avec tous les détails
function showAlertDetail(alertId) {
    const alert = allAlerts.find(a => a.id === alertId);
    if (!alert) return;
    
    // Traduire les règles en français
    const ruleTranslations = {
        'PORT_SCAN': 'Scan de Ports',
        'SYN_FLOOD': 'Inondation SYN',
        'PING_SWEEP': 'Balayage Ping',
        'SUSPICIOUS_PORT': 'Port Suspect',
        'ANOMALY_HIGH_RATE': 'Anomalie - Taux Élevé',
        'ANOMALY_LARGE_PAYLOAD': 'Anomalie - Charge Utile Large',
        'ANOMALY_ML': 'Anomalie Machine Learning'
    };
    
    const ruleName = ruleTranslations[alert.rule] || alert.rule;
    
    // Traduire la sévérité
    const severityTranslations = {
        'CRITICAL': 'Critique',
        'WARNING': 'Avertissement',
        'INFO': 'Information'
    };
    const severityName = severityTranslations[alert.severity] || alert.severity;
    
    const modalContent = document.getElementById('alert-detail-content');
    modalContent.innerHTML = `
        <div class="alert-details-grid">
            <div class="alert-detail-item">
                <div class="alert-detail-label">Identifiant</div>
                <div class="alert-detail-value">${alert.id || 'N/A'}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Date et Heure</div>
                <div class="alert-detail-value">${formatTimestamp(alert.ts)}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Type d'Alerte</div>
                <div class="alert-detail-value">${ruleName}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Code Règle</div>
                <div class="alert-detail-value"><code>${alert.rule || 'N/A'}</code></div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Niveau de Gravité</div>
                <div class="alert-detail-value">${getSeverityBadge(alert.severity)} ${severityName}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Adresse IP Source</div>
                <div class="alert-detail-value">${alert.src || 'N/A'}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Adresse IP Destination</div>
                <div class="alert-detail-value">${alert.dst || 'N/A'}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Port Source</div>
                <div class="alert-detail-value">${alert.meta?.src_port || alert.meta?.sport || 'N/A'}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Port Destination</div>
                <div class="alert-detail-value">${alert.meta?.dst_port || alert.meta?.dport || 'N/A'}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Protocole</div>
                <div class="alert-detail-value">${alert.meta?.protocol || alert.meta?.proto || 'N/A'}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Taille du Paquet</div>
                <div class="alert-detail-value">${alert.meta?.packet_size || alert.meta?.size || 'N/A'} octets</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Taille de la Charge Utile</div>
                <div class="alert-detail-value">${alert.meta?.payload_size || alert.meta?.payload || 'N/A'} octets</div>
            </div>
        </div>
        <hr style="border-color: rgba(0, 245, 255, 0.3);">
        <div class="row">
            <div class="col-12">
                <div class="alert-detail-label">Description Complète</div>
                <div class="alert-detail-value" style="margin-top: 0.5rem; line-height: 1.6;">${alert.description || 'Aucune description disponible'}</div>
            </div>
        </div>
        ${alert.meta && Object.keys(alert.meta).length > 0 ? `
        <hr style="border-color: rgba(0, 245, 255, 0.3);">
        <div class="row">
            <div class="col-12">
                <div class="alert-detail-label">Métadonnées Complètes</div>
                <div class="alert-metadata-content">
<pre style="margin: 0; color: var(--neon-cyan); font-family: 'Fira Code', monospace;">${JSON.stringify(alert.meta, null, 2)}</pre>
                </div>
            </div>
        </div>
        ` : ''}
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('alertModal'));
    modal.show();
}

// Apply filters
function applyFilters() {
    currentLimit = 100;
    loadAlerts();
}

// Reset filters
function resetFilters() {
    document.getElementById('filter-rule').value = '';
    document.getElementById('filter-severity').value = '';
    document.getElementById('filter-date-from').value = '';
    document.getElementById('filter-date-to').value = '';
    currentLimit = 100;
    loadAlerts();
}

// Load more alerts
function loadMore() {
    currentLimit += 100;
    loadAlerts();
}

// Helper functions
function getSeverityBadge(severity) {
    const badges = {
        'CRITICAL': '<span class="badge bg-danger">CRITIQUE</span>',
        'WARNING': '<span class="badge bg-warning text-dark">AVERTISSEMENT</span>',
        'INFO': '<span class="badge bg-info">INFO</span>'
    };
    return badges[severity] || '<span class="badge bg-secondary">' + severity + '</span>';
}

function formatTimestamp(ts) {
    if (!ts) return 'N/A';
    try {
        const date = new Date(ts);
        return date.toLocaleString('fr-FR');
    } catch (e) {
        return ts;
    }
}

function truncate(str, length) {
    if (!str) return '';
    return str.length > length ? str.substring(0, length) + '...' : str;
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    loadAlerts();
    
    document.getElementById('btn-apply-filters').addEventListener('click', applyFilters);
    document.getElementById('btn-reset-filters').addEventListener('click', resetFilters);
    
    const loadMoreBtn = document.getElementById('btn-load-more');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMore);
    }
});

// Make functions globally available
window.showAlertDetail = showAlertDetail;







