// ============================================
// DASHBOARD JAVASCRIPT - COMPLETE REDESIGN
// Advanced, Fluid, Real-time IDS Dashboard
// ============================================

// Global State
let socket;
let alertsChart;
let packetsChart;
let alertTimelineChart;

// Statistics
let stats = {
    packetCount: 0,
    alertCount: 0,
    criticalCount: 0,
    warningCount: 0,
    infoCount: 0,
    signatureCount: 0,
    anomalyCount: 0,
    mlAlertCount: 0,
    packetRate: 0,
    signatureRate: 0
};

// Data Collections
let packetTimestamps = [];
let alertTimeline = [];
let alertTypeData = {};
let packetRateData = [];
let alertFrequencyData = [];
let displayedAlertIds = new Set();
let initialAlertsLoaded = false;
let logsPaused = false;
let signatureTimestamps = []; // Track signature detection times
let lastPacketCount = 0;
let lastSignatureCount = 0;

// IDS State
let idsRunning = false;
let currentInterface = '';
let currentMode = 'replay';
let startTime = null;
let scanStartTime = null; // Time when scan started
let scanElapsedSeconds = 0; // Accumulated scan time when paused
let lastScanStartTime = null;

// Chart Configuration
const chartColors = {
    cyan: '#00f5ff',
    violet: '#8a2be2',
    danger: '#ff0055',
    warning: '#ffaa00',
    success: '#00ff88',
    info: '#00f5ff'
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('[Dashboard] Initializing...');
    
    // Initialize WebSocket
    initWebSocket();
    
    // Initialize Charts
    initCharts();
    
    // Initialize Event Listeners
    initEventListeners();
    
    // Initialize all stat displays to 0
    updateStatDisplay('stat-packets', 0);
    updateStatDisplay('stat-packets-rate', 0);
    updateStatDisplay('stat-alerts', 0);
    updateStatDisplay('stat-critical', 0);
    updateStatDisplay('stat-warning', 0);
    updateStatDisplay('stat-info', 0);
    updateStatDisplay('stat-signatures', 0);
    updateStatDisplay('stat-signature-rate', 0);
    updateStatDisplay('stat-anomalies', 0);
    updateStatDisplay('stat-ml-alerts', 0);
    updatePacketRateBadge();
    updateAlertsBadge();
    
    // Load Initial Data
    loadInterfaces();
    updateIDSStatus();
    
    // Initialize timeline first
    updateTimelineUI();
    
    // Load existing alerts (will populate timeline)
    loadExistingAlerts();
    
    // Start Update Intervals
    startUpdateIntervals();
    
    // Add debug logging
    addLogEntry('SYSTEM', 'Dashboard initialisé', 'success');
    console.log('[Dashboard] Initialization complete');
    
    // Debug: Log WebSocket events
    if (socket) {
        socket.onAny((event, ...args) => {
            console.log('[WebSocket Event]', event, args);
        });
    }
});

// ============================================
// WEBSOCKET CONNECTION
// ============================================

function initWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('[WebSocket] Connected');
        showNotification('Connexion WebSocket établie', 'success');
        updateIDSStatus();
        setTimeout(loadExistingAlerts, 500);
    });
    
    socket.on('disconnect', function() {
        console.log('[WebSocket] Disconnected');
        showNotification('Connexion WebSocket perdue', 'error');
    });
    
    socket.on('connect_error', function(error) {
        console.error('[WebSocket] Connection error:', error);
        showNotification('Erreur de connexion WebSocket', 'error');
    });
    
    socket.on('reconnect', function(attemptNumber) {
        console.log('[WebSocket] Reconnected after', attemptNumber, 'attempts');
        showNotification('Connexion WebSocket rétablie', 'success');
        loadExistingAlerts();
    });
    
    socket.on('new_alert', function(alert) {
        console.log('[WebSocket] Received alert:', alert.rule, alert.severity);
        handleNewAlert(alert);
        // Force DOM update after alert processing
        requestAnimationFrame(() => {
            updateStatDisplay('stat-alerts', stats.alertCount, true);
            updateStatDisplay('stat-critical', stats.criticalCount, true);
            updateStatDisplay('stat-warning', stats.warningCount, true);
            updateStatDisplay('stat-info', stats.infoCount, true);
            updateAlertsBadge();
        });
    });
    
    socket.on('new_packet', function(packet) {
        console.log('[WebSocket] Received packet:', packet.protocol, packet.src, '→', packet.dst);
        handleNewPacket(packet);
        // Force DOM update after packet processing
        requestAnimationFrame(() => {
            updateStatDisplay('stat-packets', stats.packetCount, true);
            updateStatDisplay('stat-packets-rate', Math.round(stats.packetRate), true);
            updatePacketRateBadge();
        });
    });
    
    socket.on('stats_update', function(data) {
        console.log('[WebSocket] Stats update received:', data);
        // Update stats from server push (force update)
        let needsUpdate = false;
        
        if (data.packet_count !== undefined) {
            const oldCount = stats.packetCount;
            stats.packetCount = data.packet_count;
            if (stats.packetCount !== oldCount) {
                needsUpdate = true;
                console.log(`[Stats] Packet count: ${oldCount} -> ${stats.packetCount}`);
            }
        }
        if (data.alert_count !== undefined) {
            const oldCount = stats.alertCount;
            stats.alertCount = data.alert_count;
            if (stats.alertCount !== oldCount) {
                needsUpdate = true;
                console.log(`[Stats] Alert count: ${oldCount} -> ${stats.alertCount}`);
            }
        }
        
        // Force update all stats if any changed
        if (needsUpdate) {
            requestAnimationFrame(() => {
                updateStatDisplay('stat-packets', stats.packetCount, true);
                updateStatDisplay('stat-alerts', stats.alertCount, true);
                updateAlertsBadge();
            });
        }
    });
    
    socket.on('connected', function(data) {
        console.log('[WebSocket] Server confirmation:', data.message);
    });
}

// ============================================
// CHART INITIALIZATION
// ============================================

function initCharts() {
    // Packet Rate Chart
    const packetsCtx = document.getElementById('packets-chart');
    if (packetsCtx) {
        packetsChart = new Chart(packetsCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Paquets/minute',
                    data: [],
                    borderColor: chartColors.cyan,
                    backgroundColor: 'rgba(0, 245, 255, 0.1)',
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 2,
                    pointHoverRadius: 4,
                    pointBackgroundColor: chartColors.cyan,
                    pointBorderColor: '#0a0a0f',
                    pointBorderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 0
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: chartColors.cyan,
                            font: {
                                family: 'Orbitron',
                                size: 12,
                                weight: 600
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(10, 10, 15, 0.95)',
                        borderColor: chartColors.cyan,
                        borderWidth: 2,
                        titleColor: chartColors.cyan,
                        bodyColor: '#e0e0e0',
                        font: {
                            family: 'Fira Code',
                            size: 11
                        },
                        padding: 12
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#b0b0b0',
                            font: {
                                family: 'Fira Code',
                                size: 10
                            }
                        },
                        grid: {
                            color: 'rgba(0, 245, 255, 0.1)',
                            lineWidth: 1
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#b0b0b0',
                            font: {
                                family: 'Fira Code',
                                size: 10
                            }
                        },
                        grid: {
                            color: 'rgba(0, 245, 255, 0.1)',
                            lineWidth: 1
                        }
                    }
                }
            }
        });
    }
    
    // Alert Frequency Chart
    const alertsCtx = document.getElementById('alerts-chart');
    if (alertsCtx) {
        alertsChart = new Chart(alertsCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        chartColors.danger,
                        chartColors.warning,
                        chartColors.cyan,
                        chartColors.violet,
                        chartColors.success
                    ],
                    borderColor: '#0a0a0f',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#e0e0e0',
                            font: {
                                family: 'Orbitron',
                                size: 11,
                                weight: 600
                            },
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(10, 10, 15, 0.95)',
                        borderColor: chartColors.cyan,
                        borderWidth: 2,
                        titleColor: chartColors.cyan,
                        bodyColor: '#e0e0e0',
                        font: {
                            family: 'Fira Code',
                            size: 11
                        },
                        padding: 12
                    }
                }
            }
        });
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

function initEventListeners() {
    // IDS Control Buttons
    const startBtn = document.getElementById('btn-start-ids');
    const stopBtn = document.getElementById('btn-stop-ids');
    const modeSelect = document.getElementById('capture-mode');
    
    if (startBtn) {
        startBtn.addEventListener('click', startIDS);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', stopIDS);
    }
    
    if (modeSelect) {
        modeSelect.addEventListener('change', function() {
            toggleModeUI(this.value);
        });
    }
    
    // Interface Refresh
    const refreshInterfacesBtn = document.getElementById('btn-refresh-interfaces');
    if (refreshInterfacesBtn) {
        refreshInterfacesBtn.addEventListener('click', loadInterfaces);
    }
    
    // PCAP Controls
    const browsePcapBtn = document.getElementById('btn-browse-pcap');
    const uploadPcapBtn = document.getElementById('btn-upload-pcap');
    const uploadPcapInput = document.getElementById('pcap-upload');
    
    if (browsePcapBtn) {
        browsePcapBtn.addEventListener('click', function() {
            showPcapBrowser();
        });
    }
    
    if (uploadPcapBtn && uploadPcapInput) {
        uploadPcapBtn.addEventListener('click', function() {
            uploadPcapInput.click();
        });
        
        uploadPcapInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                uploadPcapFile(this.files[0]);
            }
        });
    }
    
    // Log Controls
    const clearLogsBtn = document.getElementById('btn-clear-logs');
    const toggleLogsBtn = document.getElementById('btn-toggle-logs');
    
    if (clearLogsBtn) {
        clearLogsBtn.addEventListener('click', clearLogs);
    }
    
    if (toggleLogsBtn) {
        toggleLogsBtn.addEventListener('click', toggleLogs);
    }
    
    // Packet Stream Controls
    const clearPacketsBtn = document.getElementById('btn-clear-packets');
    if (clearPacketsBtn) {
        clearPacketsBtn.addEventListener('click', clearPacketStream);
    }
    
    // Alert Controls
    const filterAlertsBtn = document.getElementById('btn-filter-alerts');
    if (filterAlertsBtn) {
        filterAlertsBtn.addEventListener('click', function() {
            const modal = new bootstrap.Modal(document.getElementById('alertFilterModal'));
            modal.show();
        });
    }
    
    // Alert Export
    const exportAlertBtn = document.getElementById('btn-export-alert');
    if (exportAlertBtn) {
        exportAlertBtn.addEventListener('click', exportCurrentAlert);
    }
}

// ============================================
// ALERT HANDLING
// ============================================

function handleNewAlert(alert, options = {}) {
    const {
        skipStats = false,
        skipLog = false,
        skipChartUpdate = false,
        skipDuplicates = true
    } = options;
    
    // Ensure all required fields
    if (!alert.id) alert.id = 'alert-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    if (!alert.severity) alert.severity = 'INFO';
    if (!alert.rule) alert.rule = 'UNKNOWN';
    if (!alert.description) alert.description = 'No description';
    if (!alert.src) alert.src = 'N/A';
    if (!alert.dst) alert.dst = 'N/A';
    if (!alert.ts) alert.ts = new Date().toISOString();
    if (!alert.meta) alert.meta = {};
    
    if (skipDuplicates && displayedAlertIds.has(alert.id)) {
        return;
    }
    
    // Update statistics
    if (!skipStats) {
        updateAlertStats(alert);
    }
    
    // Add to UI
    addAlertToUI(alert);
    
    // Update charts first
    updateAlertTypeData(alert);
    if (!skipChartUpdate) {
        updateAlertsChart();
    }
    
    // Add to timeline (this will update the UI immediately)
    addToTimeline(alert);
    
    // Log for debugging
    console.log(`[Timeline] Added alert to timeline: ${alert.rule} (${alertTimeline.length} total)`);
    
    // Add log entry
    if (!skipLog) {
        addLogEntry('ALERT', `[${alert.rule}] ${alert.description}`, alert.severity.toLowerCase());
    }
    
    displayedAlertIds.add(alert.id);
}

function addAlertToUI(alert) {
    const container = document.getElementById('alerts-container');
    if (!container) return;
    
    // Remove placeholder
    const noAlerts = document.getElementById('no-alerts-message');
    if (noAlerts) {
        noAlerts.remove();
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
    
    const ruleName = ruleTranslations[alert.rule] || alert.rule;
    
    const severity = alert.severity || 'INFO';
    const severityClass = `severity-${severity.toLowerCase()}`;
    
    // Get severity color
    let severityColor = chartColors.cyan;
    if (severity === 'CRITICAL') severityColor = chartColors.danger;
    else if (severity === 'WARNING') severityColor = chartColors.warning;
    
    // Format metadata
    let metadataHtml = '';
    if (alert.meta && Object.keys(alert.meta).length > 0) {
        const metadataId = 'meta-' + alert.id.replace(/[^a-zA-Z0-9]/g, '');
        metadataHtml = `
            <div class="alert-metadata-toggle">
                <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#${metadataId}">
                    <i class="bi bi-code-square"></i> Métadonnées
                </button>
                <div class="collapse mt-2" id="${metadataId}">
                    <div class="alert-metadata-content">${JSON.stringify(alert.meta, null, 2)}</div>
                </div>
            </div>
        `;
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert-item ${severityClass}`;
    alertDiv.dataset.alertId = alert.id;
    // Traduire la sévérité
    const severityTranslations = {
        'CRITICAL': 'Critique',
        'WARNING': 'Avertissement',
        'INFO': 'Information'
    };
    const severityName = severityTranslations[severity] || severity;
    
    alertDiv.innerHTML = `
        <div class="alert-header-row">
            <div class="alert-title">
                <span class="alert-rule" style="color: ${severityColor};">
                    <strong>${ruleName}</strong>
                    <small class="text-muted" style="font-size: 0.75rem; margin-left: 0.5rem;"><code>${alert.rule || 'UNKNOWN'}</code></small>
                </span>
                <span class="alert-severity-badge" style="background: rgba(${severity === 'CRITICAL' ? '255, 0, 85' : severity === 'WARNING' ? '255, 170, 0' : '0, 245, 255'}, 0.2); border-color: ${severityColor}; color: ${severityColor};">
                    ${severityName}
                </span>
                </div>
            <div class="alert-time">${formatTimestamp(alert.ts)}</div>
            </div>
        <div class="alert-description">${escapeHtml(alert.description || 'Aucune description')}</div>
        <div class="alert-details-grid">
            <div class="alert-detail-item">
                <div class="alert-detail-label">Source IP</div>
                <div class="alert-detail-value">${escapeHtml(alert.src || 'N/A')}</div>
                ${alert.meta?.src_port || alert.meta?.sport ? `<small class="text-muted">Port: ${alert.meta.src_port || alert.meta.sport}</small>` : ''}
        </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Destination IP</div>
                <div class="alert-detail-value">${escapeHtml(alert.dst || 'N/A')}</div>
                ${alert.meta?.dst_port || alert.meta?.dport ? `<small class="text-muted">Port: ${alert.meta.dst_port || alert.meta.dport}</small>` : ''}
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
                <div class="alert-detail-label">Identifiant</div>
                <div class="alert-detail-value">${alert.id ? alert.id.substring(0, 8) : 'N/A'}</div>
                    </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Date et Heure</div>
                <div class="alert-detail-value">${formatTimestamp(alert.ts)}</div>
                </div>
            </div>
                ${metadataHtml}
    `;
    
    // Add click handler for modal
    alertDiv.addEventListener('click', function() {
        showAlertDetail(alert);
    });
    
    container.insertBefore(alertDiv, container.firstChild);
    
    // Keep only last 50 alerts
    const alerts = container.querySelectorAll('.alert-item');
    if (alerts.length > 50) {
        alerts[alerts.length - 1].remove();
    }
    
    // Update badge
    updateAlertsBadge();
    
    // Scroll to top to show new alert
    container.scrollTop = 0;
}

function showAlertDetail(alert) {
    const modal = new bootstrap.Modal(document.getElementById('alertDetailModal'));
    const content = document.getElementById('alert-detail-content');
    
    if (!content) return;
    
    const severity = alert.severity || 'INFO';
    let severityColor = chartColors.cyan;
    if (severity === 'CRITICAL') severityColor = chartColors.danger;
    else if (severity === 'WARNING') severityColor = chartColors.warning;
    
    content.innerHTML = `
        <div class="alert-details-grid mb-3">
            <div class="alert-detail-item">
                <div class="alert-detail-label">Règle</div>
                <div class="alert-detail-value" style="color: ${severityColor}; font-weight: 700;">${escapeHtml(alert.rule || 'UNKNOWN')}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Sévérité</div>
                <div class="alert-detail-value" style="color: ${severityColor};">${severity}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Source IP</div>
                <div class="alert-detail-value">${escapeHtml(alert.src || 'N/A')}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Destination</div>
                <div class="alert-detail-value">${escapeHtml(alert.dst || 'N/A')}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">Timestamp</div>
                <div class="alert-detail-value">${formatTimestamp(alert.ts)}</div>
            </div>
            <div class="alert-detail-item">
                <div class="alert-detail-label">ID</div>
                <div class="alert-detail-value">${escapeHtml(alert.id || 'N/A')}</div>
            </div>
        </div>
        <div class="mb-3">
            <div class="alert-detail-label">Description</div>
            <div class="alert-description">${escapeHtml(alert.description || 'No description')}</div>
        </div>
        ${alert.meta && Object.keys(alert.meta).length > 0 ? `
            <div>
                <div class="alert-detail-label">Métadonnées</div>
                <div class="alert-metadata-content">${JSON.stringify(alert.meta, null, 2)}</div>
            </div>
        ` : ''}
    `;
    
    // Store current alert for export
    content.dataset.currentAlert = JSON.stringify(alert);
    
    modal.show();
}

function exportCurrentAlert() {
    const content = document.getElementById('alert-detail-content');
    if (!content || !content.dataset.currentAlert) return;
    
    const alert = JSON.parse(content.dataset.currentAlert);
    const blob = new Blob([JSON.stringify(alert, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `alert-${alert.id || Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    showNotification('Alert exportée avec succès', 'success');
}

// ============================================
// PACKET HANDLING
// ============================================

function handleNewPacket(packet) {
    // Add timestamp for rate calculation
    const now = Date.now();
    packetTimestamps.push(now);
    
    // Clean old timestamps (keep last 60 seconds)
    const cutoff = now - 60000;
    packetTimestamps = packetTimestamps.filter(ts => ts > cutoff);
    
    // Calculate rate (packets in last 60 seconds = packets/min)
    stats.packetRate = packetTimestamps.length;
    
    // Update statistics (increment local count)
    stats.packetCount++;
    
    // Force update display immediately with requestAnimationFrame
    requestAnimationFrame(() => {
        updateStatDisplay('stat-packets', stats.packetCount, true);
        updateStatDisplay('stat-packets-rate', Math.round(stats.packetRate), true);
        updatePacketRateBadge();
    });
    
    // Add to UI
    addPacketToUI(packet);
    
    // Add log entry (throttled to avoid spam)
    if (stats.packetCount % 10 === 0) {
        addLogEntry('PACKET', `${stats.packetCount} paquets capturés`, 'info');
    }
}

function addPacketToUI(packet) {
    const container = document.getElementById('packet-stream');
    if (!container) return;
    
    // Remove placeholder
    const placeholder = container.querySelector('.packet-placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    
    const protocol = packet.protocol || 'UNKNOWN';
    const src = packet.src || 'N/A';
    const dst = packet.dst || 'N/A';
    const sport = packet.sport || '';
    const dport = packet.dport || '';
    
    const packetDiv = document.createElement('div');
    packetDiv.className = 'packet-entry';
    packetDiv.innerHTML = `
        <div class="d-flex align-items-center gap-2 flex-wrap">
        <span class="packet-protocol">[${protocol}]</span>
            <div class="packet-flow">
                <span class="packet-src">${escapeHtml(src)}:${sport}</span>
                <span class="packet-arrow">→</span>
                <span class="packet-dst">${escapeHtml(dst)}:${dport}</span>
            </div>
        </div>
        <span class="packet-time">${formatTimestamp(packet.ts)}</span>
    `;
    
    container.insertBefore(packetDiv, container.firstChild);
    
    // Keep only last 100 packets
    const packets = container.querySelectorAll('.packet-entry');
    if (packets.length > 100) {
        packets[packets.length - 1].remove();
    }
    
    // Update packet rate badge
    updatePacketRateBadge();
}

function clearPacketStream() {
    const container = document.getElementById('packet-stream');
    if (container) {
        container.innerHTML = `
            <div class="packet-placeholder">
                <i class="bi bi-diagram-3 text-muted" style="font-size: 3rem;"></i>
                <p class="text-muted mt-2">Aucun paquet capturé</p>
            </div>
        `;
    }
    packetTimestamps = [];
    stats.packetRate = 0;
    updatePacketRateBadge();
}

// ============================================
// STATISTICS UPDATES
// ============================================

// Function removed - now handled in handleNewPacket

function updateAlertStats(alert) {
    stats.alertCount++;
    
    const severity = alert.severity || 'INFO';
    if (severity === 'CRITICAL') stats.criticalCount++;
    else if (severity === 'WARNING') stats.warningCount++;
    else if (severity === 'INFO') stats.infoCount++;
    
    // Determine if signature or anomaly
    const rule = alert.rule || '';
    const now = Date.now();
    
    if (rule.includes('PORT_SCAN') || rule.includes('SYN_FLOOD') || rule.includes('PING_SWEEP') || rule.includes('SUSPICIOUS')) {
        stats.signatureCount++;
        signatureTimestamps.push(now);
        
        // Clean old signature timestamps (keep last 60 seconds)
    const cutoff = now - 60000;
        signatureTimestamps = signatureTimestamps.filter(ts => ts > cutoff);
        
        // Calculate signature rate
        stats.signatureRate = signatureTimestamps.length; // signatures/min
    } else if (rule.includes('ANOMALY') || rule.includes('ML')) {
        stats.anomalyCount++;
        if (rule.includes('ML')) stats.mlAlertCount++;
    }
    
    // Force update displays immediately with requestAnimationFrame
    requestAnimationFrame(() => {
        updateStatDisplay('stat-alerts', stats.alertCount, true);
        updateStatDisplay('stat-critical', stats.criticalCount, true);
        updateStatDisplay('stat-warning', stats.warningCount, true);
        updateStatDisplay('stat-info', stats.infoCount, true);
        updateStatDisplay('stat-signatures', stats.signatureCount, true);
        updateStatDisplay('stat-signature-rate', Math.round(stats.signatureRate), true);
        updateStatDisplay('stat-anomalies', stats.anomalyCount, true);
        updateStatDisplay('stat-ml-alerts', stats.mlAlertCount, true);
    });
}

// Store last displayed values to detect changes reliably
const lastDisplayedValues = {};

function updateStatDisplay(id, value, forceUpdate = false) {
    const element = document.getElementById(id);
    if (!element) {
        console.warn(`[updateStatDisplay] Element not found: ${id}`);
        return;
    }
    
    const newValue = Math.round(value) || 0;
    const lastValue = lastDisplayedValues[id] !== undefined ? lastDisplayedValues[id] : null;
    
    // Always update if forced or value changed
    if (forceUpdate || lastValue === null || newValue !== lastValue) {
        // Update the stored value
        lastDisplayedValues[id] = newValue;
        
        // Use requestAnimationFrame to ensure DOM updates happen
        requestAnimationFrame(() => {
            // Use direct update for immediate feedback
            const formattedValue = newValue.toLocaleString();
            
            // Force update even if text seems the same (handles formatting issues)
            if (forceUpdate || element.textContent !== formattedValue) {
                element.textContent = formattedValue;
                
                // Force reflow to ensure browser updates
                void element.offsetHeight;
            }
            
            // Add visual feedback for changes (only if value actually changed and not initial load)
            if (lastValue !== null && newValue !== lastValue && lastValue >= 0) {
                element.style.transform = 'scale(1.1)';
                element.style.textShadow = '0 0 15px currentColor';
                element.style.transition = 'all 0.2s ease';
        setTimeout(() => {
                    if (element) {
                        element.style.transform = 'scale(1)';
                        element.style.textShadow = '';
                    }
        }, 200);
    }
        });
        
        // Debug log for troubleshooting
        if (forceUpdate && newValue !== lastValue) {
            console.log(`[updateStatDisplay] ${id}: ${lastValue} -> ${newValue} (forced: ${forceUpdate})`);
        }
    }
}

// ============================================
// CHART UPDATES
// ============================================

function updateAlertTypeData(alert) {
    const rule = alert.rule || 'UNKNOWN';
    if (!alertTypeData[rule]) {
        alertTypeData[rule] = 0;
    }
    alertTypeData[rule]++;
}

function updateAlertsChart() {
    if (!alertsChart) return;
    
    const labels = Object.keys(alertTypeData);
    const data = Object.values(alertTypeData);
    
    alertsChart.data.labels = labels;
    alertsChart.data.datasets[0].data = data;
    alertsChart.update('none');
}

/**
 * Refresh alert type data from server and update chart
 * This ensures the alerts chart stays in sync even if WebSocket events are missed
 */
function refreshAlertsChartFromServer() {
    if (!idsRunning || !alertsChart) return;
    
    fetch('/api/alerts?limit=100')
        .then(response => response.json())
        .then(alerts => {
            if (alerts && alerts.length > 0) {
                // Reset alert type data
                alertTypeData = {};
                
                // Rebuild alert type data from server
                alerts.forEach(alert => {
                    const rule = alert.rule || 'UNKNOWN';
                    if (!alertTypeData[rule]) {
                        alertTypeData[rule] = 0;
                    }
                    alertTypeData[rule]++;
                });
                
                // Update chart with fresh data
                updateAlertsChart();
                
                // Synchronize UI components with any new alerts
                alerts
                    .sort((a, b) => {
                        const timeA = new Date(a.ts || 0).getTime();
                        const timeB = new Date(b.ts || 0).getTime();
                        return timeA - timeB; // Oldest first
                    })
                    .forEach(alert => {
                        if (!alert.id) return;
                        if (!displayedAlertIds.has(alert.id)) {
                            handleNewAlert(alert, {
                                skipStats: true,
                                skipChartUpdate: true,
                                skipLog: !initialAlertsLoaded,
                                skipDuplicates: false
                            });
                        }
                    });
                
                if (!initialAlertsLoaded) {
                    initialAlertsLoaded = true;
                }
            }
        })
        .catch(error => {
            console.error('[Alerts Chart] Error refreshing from server:', error);
        });
}

function updatePacketsChart() {
    if (!packetsChart) return;
    
    const now = new Date();
    const timeLabel = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    // Calculate current rate
        const oneSecondAgo = Date.now() - 1000;
        const packetsInLastSecond = packetTimestamps.filter(ts => ts > oneSecondAgo).length;
    const packetsPerMinute = packetsInLastSecond * 60;
    
    const labels = packetsChart.data.labels;
    const data = packetsChart.data.datasets[0].data;
    
    labels.push(timeLabel);
    data.push(Math.round(packetsPerMinute));
    
    // Keep last 30 data points
    if (labels.length > 30) {
        labels.shift();
        data.shift();
    }
    
    packetsChart.update('none');
}

// ============================================
// TIMELINE
// ============================================

function addToTimeline(alert) {
    // Add alert to timeline (most recent first)
    alertTimeline.unshift(alert); // Add at beginning
    
    // Keep only last 30 for timeline (increased from 20)
    if (alertTimeline.length > 30) {
        alertTimeline.pop(); // Remove oldest
    }
    
    // Update UI immediately
    updateTimelineUI();
}

function updateTimelineUI() {
    const container = document.getElementById('alert-timeline');
    if (!container) return;
    
    // Update timeline count badge
    const timelineBadge = document.getElementById('timeline-count-badge');
    if (timelineBadge) {
        timelineBadge.textContent = alertTimeline.length;
    }
    
    // Remove placeholder
    const placeholder = container.querySelector('.timeline-placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    
    // Clear container
    container.innerHTML = '';
    
    if (alertTimeline.length === 0) {
        // Show placeholder if no alerts
        container.innerHTML = `
            <div class="timeline-placeholder text-center p-5">
                <i class="bi bi-clock-history text-muted" style="font-size: 3rem;"></i>
                <p class="text-muted mt-2">Timeline des alertes apparaîtra ici</p>
                <small class="text-muted">Les alertes seront affichées en temps réel</small>
            </div>
        `;
        return;
    }
    
    // Add timeline items (most recent first - already sorted)
    alertTimeline.forEach((alert, index) => {
        const severity = alert.severity || 'INFO';
        const severityClass = `severity-${severity.toLowerCase()}`;
        
        // Get severity color
        let severityColor = chartColors.cyan;
        if (severity === 'CRITICAL') severityColor = chartColors.danger;
        else if (severity === 'WARNING') severityColor = chartColors.warning;
        
        const timelineItem = document.createElement('div');
        timelineItem.className = `timeline-item ${severityClass} timeline-item-new`;
        timelineItem.style.animationDelay = `${index * 0.05}s`; // Stagger animation
        timelineItem.innerHTML = `
            <div class="timeline-content">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="timeline-time" style="font-family: 'Fira Code', monospace; color: var(--text-muted); font-size: 0.85rem;">
                        <i class="bi bi-clock"></i> ${formatTimestamp(alert.ts)}
                    </div>
                    <span class="badge" style="background: rgba(${severity === 'CRITICAL' ? '255, 0, 85' : severity === 'WARNING' ? '255, 170, 0' : '0, 245, 255'}, 0.2); border-color: ${severityColor}; color: ${severityColor};">
                        ${severity}
                    </span>
                </div>
                <div class="timeline-rule" style="color: ${severityColor}; font-weight: 700; margin-bottom: 0.5rem;">
                    <i class="bi bi-shield-exclamation"></i> ${escapeHtml(alert.rule || 'UNKNOWN')}
                </div>
                <div class="alert-description" style="color: var(--text-primary); font-size: 0.9rem; line-height: 1.5;">
                    ${escapeHtml(alert.description || 'No description')}
                </div>
                <div class="mt-2" style="font-size: 0.8rem; color: var(--text-muted);">
                    <span><i class="bi bi-arrow-right-circle"></i> ${escapeHtml(alert.src || 'N/A')}</span>
                    <span class="ms-3"><i class="bi bi-arrow-left-circle"></i> ${escapeHtml(alert.dst || 'N/A')}</span>
                </div>
            </div>
        `;
        
        // Add click handler to show details
        timelineItem.style.cursor = 'pointer';
        timelineItem.addEventListener('click', function() {
            showAlertDetail(alert);
        });
        
        timelineItem.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
        });
        
        timelineItem.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
        
        container.appendChild(timelineItem);
    });
    
    // Add animation for new items (only the first one if it's a new alert)
    const newItems = container.querySelectorAll('.timeline-item-new');
    if (newItems.length > 0) {
        // Only animate the first item (newest) if it was just added
        const firstItem = newItems[0];
        if (firstItem) {
            firstItem.style.opacity = '0';
            firstItem.style.transform = 'translateX(-30px) scale(0.95)';
            setTimeout(() => {
                firstItem.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                firstItem.style.opacity = '1';
                firstItem.style.transform = 'translateX(0) scale(1)';
                
                // Remove animation class after animation
                setTimeout(() => {
                    firstItem.classList.remove('timeline-item-new');
                }, 500);
            }, 10);
        }
        
        // Animate other items with stagger
        Array.from(newItems).slice(1).forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateX(-20px)';
            setTimeout(() => {
                item.style.transition = 'all 0.4s ease-out';
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
                setTimeout(() => {
                    item.classList.remove('timeline-item-new');
                }, 400);
            }, (index + 1) * 50);
        });
    }
}

// ============================================
// LOG VIEWER
// ============================================

function addLogEntry(level, message, type = 'info') {
    if (logsPaused) return;
    
    const container = document.getElementById('log-viewer');
    if (!container) return;
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    logEntry.innerHTML = `
        <span class="log-time">[${timeStr}]</span>
        <span class="log-level">[${level}]</span>
        <span class="log-message">${escapeHtml(message)}</span>
    `;
    
    container.insertBefore(logEntry, container.firstChild);
    
    // Keep only last 100 log entries
    const entries = container.querySelectorAll('.log-entry');
    if (entries.length > 100) {
        entries[entries.length - 1].remove();
    }
}

function clearLogs() {
    const container = document.getElementById('log-viewer');
    if (container) {
        container.innerHTML = `
            <div class="log-entry log-info">
                <span class="log-time">[00:00:00]</span>
                <span class="log-level">[INFO]</span>
                <span class="log-message">Logs effacés</span>
            </div>
        `;
    }
}

function toggleLogs() {
    logsPaused = !logsPaused;
    const icon = document.getElementById('logs-toggle-icon');
    if (icon) {
        icon.className = logsPaused ? 'bi bi-play-fill' : 'bi bi-pause-fill';
    }
    addLogEntry('SYSTEM', logsPaused ? 'Logs en pause' : 'Logs repris', 'info');
}

// ============================================
// IDS CONTROL
// ============================================

function startIDS() {
    const mode = document.getElementById('capture-mode').value;
    const pcapPathInput = document.getElementById('pcap-path');
    const interfaceSelect = document.getElementById('interface');
    
    let pcapPath = '';
    let interface = '';
    
    if (mode === 'replay') {
        if (pcapPathInput && pcapPathInput.value) {
            pcapPath = pcapPathInput.value.trim();
        }
        if (!pcapPath) {
            showNotification('Veuillez spécifier un fichier PCAP', 'error');
        return;
    }
        addLogEntry('SYSTEM', `Mode REPLAY sélectionné: ${pcapPath}`, 'info');
    } else if (mode === 'live') {
        if (interfaceSelect && interfaceSelect.value) {
            interface = interfaceSelect.value;
        }
        if (!interface) {
            showNotification('Veuillez sélectionner une interface réseau', 'error');
        return;
        }
        addLogEntry('SYSTEM', `Mode LIVE sélectionné: ${interface}`, 'info');
    }
    
    const data = { mode: mode };
    if (pcapPath) data.pcap_path = pcapPath;
    if (interface) data.interface = interface;
    
    addLogEntry('SYSTEM', 'Démarrage de l\'IDS...', 'info');
    
    fetch('/api/ids/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('IDS démarré avec succès', 'success');
            resetStats();
            lastPacketCount = 0;
            lastSignatureCount = 0;
            scanStartTime = new Date(); // Set scan start time
            updateIDSStatus();
            addLogEntry('SYSTEM', `IDS démarré en mode ${mode}`, 'success');
            addLogEntry('SYSTEM', 'Capture de paquets en cours...', 'info');
        } else {
            showNotification('Erreur: ' + data.message, 'error');
            addLogEntry('ERROR', 'Échec du démarrage: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error starting IDS:', error);
        showNotification('Erreur lors du démarrage', 'error');
        addLogEntry('ERROR', 'Erreur: ' + error.message, 'error');
    });
}

function stopIDS() {
    fetch('/api/ids/stop', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('IDS arrêté avec succès', 'success');
            scanStartTime = null; // Reset scan start time
            updateIDSStatus();
            addLogEntry('SYSTEM', 'IDS arrêté', 'info');
        } else {
            showNotification('Erreur: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error stopping IDS:', error);
        showNotification('Erreur lors de l\'arrêt', 'error');
    });
}

function updateIDSStatus() {
    fetch('/api/ids/status')
        .then(response => response.json())
        .then(data => {
            idsRunning = data.running;
            
            const statusDot = document.getElementById('status-dot');
            const statusText = document.getElementById('status-text');
            const startBtn = document.getElementById('btn-start-ids');
            const stopBtn = document.getElementById('btn-stop-ids');
            
            if (data.running) {
                if (statusDot) {
                    statusDot.classList.add('active');
                }
                if (statusText) {
                    statusText.textContent = 'En cours';
                }
                if (startBtn) startBtn.disabled = true;
                if (stopBtn) stopBtn.disabled = false;
                
                // Update scan start time
                if (data.stats && data.stats.start_time) {
                    if (!scanStartTime) {
                        scanStartTime = new Date(data.stats.start_time);
                    }
                } else if (data.stats && !scanStartTime) {
                    scanStartTime = new Date(); // Fallback to current time
                }
                
                // Update stats from server (force update)
                if (data.stats) {
                    const oldPacketCount = stats.packetCount;
                    const oldAlertCount = stats.alertCount;
                    
                    stats.packetCount = data.stats.packet_count || 0;
                    stats.alertCount = data.stats.alert_count || 0;
                    stats.criticalCount = data.stats.critical_count || 0;
                    stats.warningCount = data.stats.warning_count || 0;
                    stats.infoCount = data.stats.info_count || 0;
                    stats.signatureCount = data.stats.signature_count || 0;
                    stats.anomalyCount = data.stats.anomaly_count || 0;
                    
                    // Force update all displays (updateStatDisplay already uses requestAnimationFrame internally)
                    updateStatDisplay('stat-packets', stats.packetCount, true);
                    updateStatDisplay('stat-alerts', stats.alertCount, true);
                    updateStatDisplay('stat-critical', stats.criticalCount, true);
                    updateStatDisplay('stat-warning', stats.warningCount, true);
                    updateStatDisplay('stat-info', stats.infoCount, true);
                    updateStatDisplay('stat-signatures', stats.signatureCount, true);
                    updateStatDisplay('stat-anomalies', stats.anomalyCount, true);
                    requestAnimationFrame(() => {
                        updateAlertsBadge();
                    });
                    
                    // Update scan duration
                    updateScanDuration();
                }
            } else {
                if (statusDot) {
                    statusDot.classList.remove('active');
                }
                if (statusText) {
                    statusText.textContent = 'Arrêté';
                }
                if (startBtn) startBtn.disabled = false;
                if (stopBtn) stopBtn.disabled = true;
                
                // Reset scan duration when stopped
                scanStartTime = null;
                updateScanDuration();
            }
        })
        .catch(error => console.error('Error fetching status:', error));
}

// ============================================
// INTERFACE MANAGEMENT
// ============================================

function loadInterfaces() {
    fetch('/api/interfaces')
        .then(response => response.json())
        .then(data => {
            const interfaceSelect = document.getElementById('interface');
            const interfaceInfo = document.getElementById('interface-info');
            
            if (!interfaceSelect) return;
            
            interfaceSelect.innerHTML = '<option value="">Sélectionner...</option>';
            
            if (data.interfaces && data.interfaces.length > 0) {
                data.interfaces.forEach(iface => {
                            const option = document.createElement('option');
                            option.value = iface.name;
                    option.textContent = `${iface.display_name || iface.name} (${iface.address || 'N/A'})`;
                            option.dataset.type = iface.type;
                    option.dataset.address = iface.address;
                    interfaceSelect.appendChild(option);
                });
                
                if (interfaceInfo) {
                    interfaceInfo.innerHTML = `<i class="bi bi-check-circle text-success"></i> ${data.count || data.interfaces.length} interface(s) disponible(s)`;
                }
            } else {
                if (interfaceInfo) {
                    interfaceInfo.innerHTML = `<i class="bi bi-exclamation-triangle text-warning"></i> Aucune interface détectée`;
                }
            }
        })
        .catch(error => {
            console.error('Error loading interfaces:', error);
            showNotification('Erreur lors du chargement des interfaces', 'error');
        });
}

function toggleModeUI(mode) {
    const pcapGroup = document.getElementById('pcap-path-group');
    const interfaceGroup = document.getElementById('interface-group');
    
    if (mode === 'live') {
        if (pcapGroup) pcapGroup.style.display = 'none';
        if (interfaceGroup) interfaceGroup.style.display = 'block';
        loadInterfaces();
    } else {
        if (pcapGroup) pcapGroup.style.display = 'block';
        if (interfaceGroup) interfaceGroup.style.display = 'none';
    }
}

// ============================================
// PCAP MANAGEMENT
// ============================================

function showPcapBrowser() {
    const modal = new bootstrap.Modal(document.getElementById('pcapBrowserModal'));
    const fileList = document.getElementById('pcap-file-list');
    
    if (fileList) {
        fileList.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary"></div></div>';
    }
    
    fetch('/api/pcap/list')
            .then(response => response.json())
            .then(data => {
            if (fileList) {
                if (data.files && data.files.length > 0) {
                    fileList.innerHTML = '';
                    data.files.forEach(file => {
                        const fileItem = document.createElement('div');
                        fileItem.className = 'pcap-file-item';
                        fileItem.innerHTML = `
                            <div>
                                <div class="pcap-file-name">${escapeHtml(file.name)}</div>
                                <div class="pcap-file-size">${(file.size_mb || 0).toFixed(2)} MB</div>
                            </div>
                            <i class="bi bi-chevron-right"></i>
                        `;
                        fileItem.addEventListener('click', function() {
                            const pcapPathInput = document.getElementById('pcap-path');
                            if (pcapPathInput) {
                                pcapPathInput.value = file.path;
                            }
                            modal.hide();
                            showNotification('Fichier PCAP sélectionné', 'success');
                        });
                        fileList.appendChild(fileItem);
                    });
                } else {
                    fileList.innerHTML = '<div class="text-center p-5 text-muted">Aucun fichier PCAP trouvé</div>';
                }
            }
        })
        .catch(error => {
            console.error('Error loading PCAP files:', error);
            if (fileList) {
                fileList.innerHTML = '<div class="text-center p-5 text-danger">Erreur lors du chargement</div>';
            }
        });
    
    modal.show();
}

function uploadPcapFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const uploadBtn = document.getElementById('btn-upload-pcap');
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Upload...';
    }
    
    fetch('/api/pcap/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Fichier uploadé avec succès', 'success');
            const pcapPathInput = document.getElementById('pcap-path');
            if (pcapPathInput && data.file) {
                pcapPathInput.value = data.file.path;
            }
            addLogEntry('SYSTEM', `Fichier PCAP uploadé: ${data.file.name}`, 'success');
        } else {
            showNotification('Erreur: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        showNotification('Erreur lors de l\'upload', 'error');
    })
    .finally(() => {
        if (uploadBtn) {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="bi bi-cloud-upload"></i> Upload PCAP';
        }
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function formatTimestamp(ts) {
    if (!ts) return 'N/A';
    try {
        const date = new Date(ts);
        return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch (e) {
        return ts;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    const existing = document.querySelectorAll('.hacker-notification');
    existing.forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `hacker-notification hacker-notification-${type}`;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi ${type === 'success' ? 'bi-check-circle' : type === 'error' ? 'bi-x-circle' : 'bi-info-circle'} me-2"></i>
            <span>${escapeHtml(message)}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
            setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function resetStats() {
    stats = {
        packetCount: 0,
        alertCount: 0,
        criticalCount: 0,
        warningCount: 0,
        infoCount: 0,
        signatureCount: 0,
        anomalyCount: 0,
        mlAlertCount: 0,
        packetRate: 0,
        signatureRate: 0
    };
    
    packetTimestamps = [];
    signatureTimestamps = [];
    alertTimeline = [];
    alertTypeData = {};
    packetRateData = [];
    alertFrequencyData = [];
    lastPacketCount = 0;
    lastSignatureCount = 0;
    displayedAlertIds.clear();
    initialAlertsLoaded = false;
    scanStartTime = null;
    scanElapsedSeconds = 0;
    lastScanStartTime = null;
    displayedAlertIds.clear();
    initialAlertsLoaded = false;
    
    // Reset last displayed values
    Object.keys(lastDisplayedValues).forEach(key => {
        delete lastDisplayedValues[key];
    });
    
    // Clear UI
    clearPacketStream();
    clearLogs();
    
    // Reset all stat displays
    updateStatDisplay('stat-packets', 0);
    updateStatDisplay('stat-packets-rate', 0);
    updateStatDisplay('stat-alerts', 0);
    updateStatDisplay('stat-critical', 0);
    updateStatDisplay('stat-warning', 0);
    updateStatDisplay('stat-info', 0);
    updateStatDisplay('stat-signatures', 0);
    updateStatDisplay('stat-signature-rate', 0);
    updateStatDisplay('stat-anomalies', 0);
    updateStatDisplay('stat-ml-alerts', 0);
    
    // Reset charts
    if (packetsChart) {
        packetsChart.data.labels = [];
        packetsChart.data.datasets[0].data = [];
        packetsChart.update();
    }
    
    if (alertsChart) {
        alertsChart.data.labels = [];
        alertsChart.data.datasets[0].data = [];
        alertsChart.update();
    }
    
    // Clear alerts container
    const alertsContainer = document.getElementById('alerts-container');
    if (alertsContainer) {
        alertsContainer.innerHTML = `
            <div class="text-center p-5" id="no-alerts-message">
                <i class="bi bi-shield-check text-muted" style="font-size: 4rem;"></i>
                <p class="text-muted mt-3">Aucune alerte pour le moment</p>
            </div>
        `;
    }
    
    // Clear timeline
    updateTimelineUI();
    
    updateAlertsBadge();
    updatePacketRateBadge();
}

function updateAlertsBadge() {
    const badge = document.getElementById('alerts-count-badge');
    if (badge) {
        badge.textContent = stats.alertCount;
    }
}

function updatePacketRateBadge() {
    const badge = document.getElementById('packet-rate-badge');
    if (badge) {
        const rate = Math.round(stats.packetRate) || 0;
        badge.textContent = `${rate} pkt/min`;
        
        // Update color based on rate
        if (rate > 3000) {
            badge.className = 'badge bg-danger';
        } else if (rate > 1000) {
            badge.className = 'badge bg-warning';
        } else {
            badge.className = 'badge bg-info';
        }
    }
}

function loadExistingAlerts() {
    fetch('/api/alerts?limit=50')
            .then(response => response.json())
        .then(alerts => {
            if (alerts && alerts.length > 0) {
                console.log(`[Dashboard] Loading ${alerts.length} existing alerts`);
                
                alertTimeline = [];
                alertTypeData = {};
                displayedAlertIds.clear();
                
                const alertsContainer = document.getElementById('alerts-container');
                if (alertsContainer) {
                    alertsContainer.innerHTML = '';
                }
                
                alerts.sort((a, b) => {
                    const timeA = new Date(a.ts || 0).getTime();
                    const timeB = new Date(b.ts || 0).getTime();
                    return timeA - timeB; // Oldest first to maintain order when unshifting
                });
                
                alerts.forEach(alert => {
                    handleNewAlert(alert, {
                        skipStats: true,
                        skipLog: true,
                        skipChartUpdate: true,
                        skipDuplicates: false
                    });
                });
                
                updateAlertsChart();
                updateTimelineUI();
                updateAlertsBadge();
                
                initialAlertsLoaded = true;
                console.log(`[Dashboard] Loaded ${alerts.length} alerts into timeline`);
                } else {
                updateTimelineUI();
                }
            })
            .catch(error => {
            console.error('Error loading existing alerts:', error);
            // Initialize empty timeline on error
            updateTimelineUI();
        });
}

// ============================================
// UPDATE INTERVALS
// ============================================

/**
 * Force update all dashboard statistics from server
 * This ensures all values are updated regularly, even if WebSocket events are missed
 */
function updateAllStatsFromServer() {
    if (!idsRunning) return;
    
    fetch('/api/ids/status')
            .then(response => response.json())
            .then(data => {
            if (data.running && data.stats) {
                // Store old values to detect changes
                const oldPacketCount = stats.packetCount;
                const oldAlertCount = stats.alertCount;
                const oldCriticalCount = stats.criticalCount;
                const oldWarningCount = stats.warningCount;
                const oldInfoCount = stats.infoCount;
                const oldSignatureCount = stats.signatureCount;
                const oldAnomalyCount = stats.anomalyCount;
                
                // Update all stats from server (source of truth)
                stats.packetCount = data.stats.packet_count || 0;
                stats.alertCount = data.stats.alert_count || 0;
                stats.criticalCount = data.stats.critical_count || 0;
                stats.warningCount = data.stats.warning_count || 0;
                stats.infoCount = data.stats.info_count || 0;
                stats.signatureCount = data.stats.signature_count || 0;
                stats.anomalyCount = data.stats.anomaly_count || 0;
                stats.mlAlertCount = data.stats.ml_alert_count || 0;
                
                // Calculate packet rate from timestamps
                const now = Date.now();
                const packetCutoff = now - 60000;
                packetTimestamps = packetTimestamps.filter(ts => ts > packetCutoff);
                stats.packetRate = packetTimestamps.length;
                
                // Calculate signature rate from timestamps
                const signatureCutoff = now - 60000;
                signatureTimestamps = signatureTimestamps.filter(ts => ts > signatureCutoff);
                stats.signatureRate = signatureTimestamps.length;
                
                // Force update ALL displays every second (regardless of changes)
                requestAnimationFrame(() => {
                    // Always update packet count
                    updateStatDisplay('stat-packets', stats.packetCount, true);
                    updateStatDisplay('stat-packets-rate', Math.round(stats.packetRate), true);
                    
                    // Always update alert counts
                    updateStatDisplay('stat-alerts', stats.alertCount, true);
                    updateStatDisplay('stat-critical', stats.criticalCount, true);
                    updateStatDisplay('stat-warning', stats.warningCount, true);
                    updateStatDisplay('stat-info', stats.infoCount, true);
                    
                    // Always update signature and anomaly counts
                    updateStatDisplay('stat-signatures', stats.signatureCount, true);
                    updateStatDisplay('stat-signature-rate', Math.round(stats.signatureRate), true);
                    updateStatDisplay('stat-anomalies', stats.anomalyCount, true);
                    updateStatDisplay('stat-ml-alerts', stats.mlAlertCount, true);
                    
                    // Update badges
                    updatePacketRateBadge();
                    updateAlertsBadge();
                });
                
                // Log changes for debugging
                if (stats.packetCount !== oldPacketCount || stats.alertCount !== oldAlertCount) {
                    console.log(`[Stats Update] Packets: ${oldPacketCount} -> ${stats.packetCount}, Alerts: ${oldAlertCount} -> ${stats.alertCount}`);
                }
                }
            })
            .catch(error => {
            console.error('[Stats Update] Error fetching stats:', error);
        });
}

/**
 * Update scan duration display
 */
function updateScanDuration() {
    const durationElement = document.getElementById('scan-duration');
    const startTimeElement = document.getElementById('scan-start-time');
    
    if (!durationElement) return;
    
    let totalSeconds = scanElapsedSeconds;
    
    if (scanStartTime) {
        const now = new Date();
        totalSeconds += Math.floor((now - scanStartTime) / 1000);
    }
    
    durationElement.textContent = formatDuration(totalSeconds);
    
    if (startTimeElement) {
        const displayTime = lastScanStartTime || scanStartTime;
        if (displayTime) {
            startTimeElement.textContent = `Démarré à ${displayTime.toLocaleTimeString('fr-FR')}`;
        } else {
            startTimeElement.textContent = 'Non démarré';
        }
    }
}

function formatDuration(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function finalizeScanDuration() {
    if (scanStartTime) {
        const now = new Date();
        scanElapsedSeconds += Math.floor((now - scanStartTime) / 1000);
        scanStartTime = null;
    }
}

function startUpdateIntervals() {
    // Update IDS status every 3 seconds (more frequent for better responsiveness)
    setInterval(updateIDSStatus, 3000);
    
    // Update scan duration every second
    setInterval(updateScanDuration, 1000);
    
    // Update packet rate chart every second
    setInterval(updatePacketsChart, 1000);
    
    // CRITICAL: Update alerts chart every 2 seconds
    // This ensures the chart updates even if WebSocket events are missed
    setInterval(function() {
        if (idsRunning) {
            refreshAlertsChartFromServer();
        }
    }, 2000); // Update every 2 seconds
    
    // CRITICAL: Update ALL statistics from server every second
    // This ensures all values are updated regularly, even if WebSocket events are missed
    setInterval(function() {
        updateAllStatsFromServer();
    }, 1000);
    
    // Update all rate indicators every second (recalculate from timestamps)
    setInterval(function() {
        if (!idsRunning) return;
        
        const now = Date.now();
        
        // Recalculate packet rate from timestamps
        const packetCutoff = now - 60000;
        packetTimestamps = packetTimestamps.filter(ts => ts > packetCutoff);
        stats.packetRate = packetTimestamps.length;
        
        // Update packet rate display (force update with requestAnimationFrame)
        requestAnimationFrame(() => {
            updateStatDisplay('stat-packets-rate', Math.round(stats.packetRate), true);
            updatePacketRateBadge();
        });
        
        // Recalculate signature rate
        const signatureCutoff = now - 60000;
        signatureTimestamps = signatureTimestamps.filter(ts => ts > signatureCutoff);
        stats.signatureRate = signatureTimestamps.length;
        
        // Update signature rate display (force update with requestAnimationFrame)
        requestAnimationFrame(() => {
            updateStatDisplay('stat-signature-rate', Math.round(stats.signatureRate), true);
        });
    }, 1000);
    
    // Additional sync for packet timestamps (every 500ms) - helps with rate calculation
    // This is supplementary to the main updateAllStatsFromServer() which runs every second
    setInterval(function() {
        if (idsRunning) {
            fetch('/api/ids/status')
            .then(response => response.json())
            .then(data => {
                if (data.running && data.stats) {
                    const serverPacketCount = data.stats.packet_count || 0;
                    
                    // Calculate packet rate from server difference
                    if (serverPacketCount > lastPacketCount) {
                        const packetDiff = serverPacketCount - lastPacketCount;
                        const now = Date.now();
                        
                        // Add timestamps for new packets
                        for (let i = 0; i < packetDiff; i++) {
                            packetTimestamps.push(now - (packetDiff - i) * 10); // Distribute over time
                        }
                        
                        // Clean old timestamps
                        const cutoff = now - 60000;
                        packetTimestamps = packetTimestamps.filter(ts => ts > cutoff);
                        stats.packetRate = packetTimestamps.length;
                        
                        lastPacketCount = serverPacketCount;
                        
                        // Update packet rate immediately
                        requestAnimationFrame(() => {
                            updateStatDisplay('stat-packets-rate', Math.round(stats.packetRate), true);
                            updatePacketRateBadge();
                        });
                    }
                }
            })
            .catch(error => {
                // Silently handle errors to avoid log spam
            });
        }
    }, 500); // Update every 500ms for more responsive rate calculation
}
