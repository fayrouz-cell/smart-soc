// Alerts configuration page JavaScript

// Load current configuration
function loadConfig() {
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            // Populate signature detection settings
            if (data.signatures) {
                const portscan = data.signatures.portscan || {};
                document.getElementById('portscan-enabled').checked = portscan.enabled !== false;
                document.getElementById('portscan-threshold').value = portscan.ports_threshold || 20;
                document.getElementById('portscan-window').value = portscan.window_seconds || 10;
                
                const synflood = data.signatures.syn_flood || {};
                document.getElementById('synflood-enabled').checked = synflood.enabled !== false;
                document.getElementById('synflood-threshold').value = synflood.syn_threshold || 200;
                document.getElementById('synflood-window').value = synflood.window_seconds || 10;
                
                const pingsweep = data.signatures.ping_sweep || {};
                document.getElementById('pingsweep-enabled').checked = pingsweep.enabled !== false;
                document.getElementById('pingsweep-threshold').value = pingsweep.hosts_threshold || 50;
                document.getElementById('pingsweep-window').value = pingsweep.window_seconds || 30;
                
                const suspicious = data.signatures.suspicious_ports || {};
                document.getElementById('suspicious-ports-enabled').checked = suspicious.enabled !== false;
                if (suspicious.ports) {
                    document.getElementById('suspicious-ports').value = suspicious.ports.join(',');
                }
            }
            
            // Populate anomaly detection settings
            if (data.anomaly) {
                document.getElementById('anomaly-rate-threshold').value = data.anomaly.packet_rate_threshold || 1000;
                document.getElementById('anomaly-payload-threshold').value = data.anomaly.payload_size_threshold_bytes || 10000;
                document.getElementById('anomaly-ml-enabled').checked = data.anomaly.use_ml === true;
            }
        })
        .catch(error => {
            console.error('Error loading config:', error);
            alert('Erreur lors du chargement de la configuration');
        });
}

// Save signatures configuration
function saveSignaturesConfig(event) {
    event.preventDefault();
    
    const config = {
        signatures: {
            portscan: {
                enabled: document.getElementById('portscan-enabled').checked,
                ports_threshold: parseInt(document.getElementById('portscan-threshold').value),
                window_seconds: parseInt(document.getElementById('portscan-window').value)
            },
            syn_flood: {
                enabled: document.getElementById('synflood-enabled').checked,
                syn_threshold: parseInt(document.getElementById('synflood-threshold').value),
                window_seconds: parseInt(document.getElementById('synflood-window').value)
            },
            ping_sweep: {
                enabled: document.getElementById('pingsweep-enabled').checked,
                hosts_threshold: parseInt(document.getElementById('pingsweep-threshold').value),
                window_seconds: parseInt(document.getElementById('pingsweep-window').value)
            },
            suspicious_ports: {
                enabled: document.getElementById('suspicious-ports-enabled').checked,
                ports: document.getElementById('suspicious-ports').value.split(',').map(p => parseInt(p.trim())).filter(p => !isNaN(p))
            }
        }
    };
    
    fetch('/api/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Configuration des signatures enregistrée avec succès');
        } else {
            alert('Erreur lors de l\'enregistrement');
        }
    })
    .catch(error => {
        console.error('Error saving config:', error);
        alert('Erreur lors de l\'enregistrement de la configuration');
    });
}

// Save anomaly configuration
function saveAnomalyConfig(event) {
    event.preventDefault();
    
    const config = {
        anomaly: {
            packet_rate_threshold: parseInt(document.getElementById('anomaly-rate-threshold').value),
            payload_size_threshold_bytes: parseInt(document.getElementById('anomaly-payload-threshold').value),
            use_ml: document.getElementById('anomaly-ml-enabled').checked
        }
    };
    
    fetch('/api/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Configuration des anomalies enregistrée avec succès');
        } else {
            alert('Erreur lors de l\'enregistrement');
        }
    })
    .catch(error => {
        console.error('Error saving config:', error);
        alert('Erreur lors de l\'enregistrement de la configuration');
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    loadConfig();
    
    const signaturesForm = document.getElementById('signatures-form');
    if (signaturesForm) {
        signaturesForm.addEventListener('submit', saveSignaturesConfig);
    }
    
    const anomalyForm = document.getElementById('anomaly-form');
    if (anomalyForm) {
        anomalyForm.addEventListener('submit', saveAnomalyConfig);
    }
});













