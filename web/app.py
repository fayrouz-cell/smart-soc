"""Flask web application for IDS."""

import os
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import shutil

# Import IDS components
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import load_config
from core.alert import Alert
from core.logger import get_logger

try:
    from scapy.all import get_if_list, get_if_addr
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ids-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'data/pcap_samples'
socketio = SocketIO(app, cors_allowed_origins="*")

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'pcap', 'pcapng', 'cap'}

# Global state
ids_instance = None
ids_thread = None
realtime_data = {
    'packets': [],
    'alerts': [],
    'stats': {
        'packet_count': 0,
        'alert_count': 0,
        'start_time': None
    }
}

# User management (simple in-memory for demo - use database in production)
users = {
    'admin': {
        'password': generate_password_hash('admin123'),
        'role': 'admin'
    },
    'user': {
        'password': generate_password_hash('user123'),
        'role': 'user'
    }
}


def login_required(f):
    """Decorator for routes that require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator for routes that require admin role."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Accès refusé. Rôle administrateur requis.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if username and password:
            if username in users and check_password_hash(users[username]['password'], password):
                session['user'] = username
                session['role'] = users[username]['role']
                flash('Connexion réussie!', 'success')
                return redirect(url_for('app_shell'))
            else:
                flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
        else:
            flash('Veuillez remplir tous les champs.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout."""
    session.clear()
    flash('Déconnexion réussie.', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with real-time monitoring."""
    return render_template('dashboard.html')


@app.route('/app')
@login_required
def app_shell():
    """Single page shell to host all IDS views."""
    return render_template('app_shell.html')


@app.route('/history')
@login_required
def history():
    """Alert history page."""
    return render_template('history.html')


@app.route('/alerts')
@login_required
def alerts():
    """Alert configuration page."""
    return render_template('alerts.html')


@app.route('/contact')
@login_required
def contact():
    """Contact page."""
    return render_template('contact.html')


# API Routes
@app.route('/api/stats')
@login_required
def api_stats():
    """Get current statistics."""
    return jsonify(realtime_data['stats'])


@app.route('/api/alerts')
@login_required
def api_alerts():
    """Get alerts with filtering."""
    log_config = load_config().get("logging", {})
    alerts_log = log_config.get("alerts_log", "data/logs/alerts.log")
    
    # Get filter parameters
    rule_filter = request.args.get('rule', '')
    severity_filter = request.args.get('severity', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    limit = int(request.args.get('limit', 100))
    
    alerts = read_alerts_from_log(alerts_log, limit=limit)
    
    # Apply filters
    if rule_filter:
        alerts = [a for a in alerts if rule_filter.lower() in a.get('rule', '').lower()]
    if severity_filter:
        alerts = [a for a in alerts if a.get('severity', '') == severity_filter]
    if date_from:
        alerts = [a for a in alerts if a.get('ts', '') >= date_from]
    if date_to:
        alerts = [a for a in alerts if a.get('ts', '') <= date_to]
    
    return jsonify(alerts)


@app.route('/api/config', methods=['GET', 'POST'])
@admin_required
def api_config():
    """Get or update configuration."""
    if request.method == 'GET':
        config = load_config()
        return jsonify(config)
    else:
        # Update configuration
        new_config = request.json
        config_path = Path('config.yaml')
        # In production, properly save to YAML file
        flash('Configuration mise à jour (non persistée dans cette version).', 'info')
        return jsonify({'status': 'success'})


@app.route('/api/ids/start', methods=['POST'])
@admin_required
def api_ids_start():
    """Start IDS."""
    global ids_instance, ids_thread
    
    if ids_instance and ids_instance.running:
        return jsonify({'status': 'error', 'message': 'IDS déjà en cours d\'exécution'}), 400
    
    try:
        from main import IDS
        
        mode = request.json.get('mode', 'replay')
        interface = request.json.get('interface')
        pcap_path = request.json.get('pcap_path', 'data/pcap_samples/sample_traffic.pcap')
        
        # Validate mode and required parameters
        if mode == 'replay':
            if not pcap_path:
                return jsonify({'status': 'error', 'message': 'Chemin PCAP requis pour le mode replay'}), 400
            pcap_file = Path(pcap_path)
            # Try absolute path first, then relative
            if not pcap_file.exists():
                pcap_file = Path(pcap_path).resolve()
            if not pcap_file.exists():
                return jsonify({
                    'status': 'error', 
                    'message': f'Fichier PCAP introuvable: {pcap_path}. Vérifiez le chemin et réessayez.'
                }), 400
            if not pcap_file.is_file():
                return jsonify({
                    'status': 'error', 
                    'message': f'Le chemin spécifié n\'est pas un fichier: {pcap_path}'
                }), 400
        elif mode == 'live':
            if not interface:
                # Try to auto-detect WiFi interface
                if SCAPY_AVAILABLE:
                    try:
                        interfaces = get_if_list()
                        for iface in interfaces:
                            iface_lower = iface.lower()
                            if any(x in iface_lower for x in ['wi', 'wlan', 'wireless', 'wifi']):
                                interface = iface
                                break
                        if not interface and interfaces:
                            interface = interfaces[0]
                    except Exception:
                        pass
                
                if not interface:
                    return jsonify({
                        'status': 'error', 
                        'message': 'Interface réseau requise pour le mode live. Aucune interface WiFi détectée automatiquement.'
                    }), 400
        
        # Create IDS instance with proper error handling
        try:
            ids_instance = IDS()
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erreur lors de l\'initialisation de l\'IDS: {str(e)}'
            }), 500
        
        ids_instance.sniffer.mode = mode
        if interface:
            ids_instance.sniffer.interface = interface
        if pcap_path:
            # Try to resolve path (absolute or relative)
            pcap_file = Path(pcap_path)
            if not pcap_file.is_absolute():
                pcap_file = Path.cwd() / pcap_file
            ids_instance.sniffer.pcap_path = str(pcap_file.resolve())
        
        # Store original callbacks
        original_alert_callback = ids_instance._handle_alert
        original_packet_callback = ids_instance._handle_packet
        
        # Override alert callback to emit via WebSocket
        def web_alert_callback(alert: Alert):
            try:
                original_alert_callback(alert)
                alert_dict = alert.to_dict()
                
                # Update realtime data
                realtime_data['alerts'].append(alert_dict)
                if len(realtime_data['alerts']) > 100:
                    realtime_data['alerts'].pop(0)
                
                # Update stats immediately
                realtime_data['stats']['alert_count'] = ids_instance.alert_count
                
                # Emit to all connected clients with namespace
                socketio.emit('new_alert', alert_dict, broadcast=True, namespace='/')
                
                # Emit stats update
                socketio.emit('stats_update', {
                    'packet_count': ids_instance.packet_count,
                    'alert_count': ids_instance.alert_count
                }, broadcast=True, namespace='/')
                
                print(f"[WebSocket] Emitted alert: {alert.rule} from {alert.src}")
            except Exception as e:
                print(f"Error in web_alert_callback: {e}")
                import traceback
                traceback.print_exc()
        
        ids_instance._handle_alert = web_alert_callback
        
        # Override packet callback
        def web_packet_callback(packet_record):
            try:
                original_packet_callback(packet_record)
                packet_dict = packet_record.to_dict()
                
                # Update realtime data
                realtime_data['packets'].append(packet_dict)
                if len(realtime_data['packets']) > 100:
                    realtime_data['packets'].pop(0)
                
                # Update stats immediately
                realtime_data['stats']['packet_count'] = ids_instance.packet_count
                realtime_data['stats']['alert_count'] = ids_instance.alert_count
                
                # Emit every packet for accurate rate calculation
                socketio.emit('new_packet', packet_dict, broadcast=True, namespace='/')
                
                # Emit stats update every 10 packets to reduce overhead
                if ids_instance.packet_count % 10 == 0:
                    socketio.emit('stats_update', {
                        'packet_count': ids_instance.packet_count,
                        'alert_count': ids_instance.alert_count
                    }, broadcast=True, namespace='/')
                    
            except Exception as e:
                print(f"Error in web_packet_callback: {e}")
                import traceback
                traceback.print_exc()
        
        ids_instance._handle_packet = web_packet_callback
        
        # Reset realtime data for a clean session
        realtime_data['alerts'] = []
        realtime_data['packets'] = []
        realtime_data['stats']['packet_count'] = 0
        realtime_data['stats']['alert_count'] = 0
        realtime_data['stats']['start_time'] = datetime.now().isoformat()
        
        def run_ids():
            try:
                ids_instance.start()
            except Exception as e:
                print(f"Error in IDS thread: {e}")
                import traceback
                traceback.print_exc()
        
        ids_thread = threading.Thread(target=run_ids, daemon=True)
        ids_thread.start()
        
        # Give it a moment to start and process some packets
        time.sleep(1.0)
        
        # Load existing alerts from log and emit them
        try:
            log_config = load_config().get("logging", {})
            alerts_log = log_config.get("alerts_log", "data/logs/alerts.log")
            existing_alerts = read_alerts_from_log(alerts_log, limit=50)
            # Emit recent alerts to update the dashboard
            for alert in existing_alerts[-20:]:  # Last 20 alerts
                socketio.emit('new_alert', alert, broadcast=True, namespace='/')
                print(f"[WebSocket] Emitted existing alert: {alert.get('rule', 'UNKNOWN')}")
        except Exception as e:
            print(f"Error loading existing alerts: {e}")
        
        if ids_instance.running:
            return jsonify({
                'status': 'success', 
                'message': f'IDS démarré en mode {mode}',
                'mode': mode
            })
        else:
            return jsonify({
                'status': 'error', 
                'message': 'Échec du démarrage de l\'IDS. Vérifiez les logs.'
            }), 500
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error starting IDS: {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error', 
            'message': f'Erreur lors du démarrage: {error_msg}'
        }), 500


@app.route('/api/ids/stop', methods=['POST'])
@admin_required
def api_ids_stop():
    """Stop IDS."""
    global ids_instance
    
    if not ids_instance or not ids_instance.running:
        return jsonify({'status': 'error', 'message': 'IDS non démarré'}), 400
    
    try:
        ids_instance.stop()
        return jsonify({'status': 'success', 'message': 'IDS arrêté'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/ids/status')
@login_required
def api_ids_status():
    """Get IDS status."""
    if ids_instance and ids_instance.running:
        # Calculate critical, warning, info counts from alerts
        critical_count = 0
        warning_count = 0
        info_count = 0
        signature_count = 0
        anomaly_count = 0
        
        if realtime_data.get('alerts'):
            for alert in realtime_data['alerts']:
                severity = alert.get('severity', 'INFO')
                if severity == 'CRITICAL':
                    critical_count += 1
                elif severity == 'WARNING':
                    warning_count += 1
                elif severity == 'INFO':
                    info_count += 1
                
                # Count signatures and anomalies
                rule = alert.get('rule', '')
                if any(x in rule for x in ['PORT_SCAN', 'SYN_FLOOD', 'PING_SWEEP', 'SUSPICIOUS']):
                    signature_count += 1
                elif any(x in rule for x in ['ANOMALY', 'ML']):
                    anomaly_count += 1
        
        stats = {
            'packet_count': ids_instance.packet_count,
            'alert_count': ids_instance.alert_count,
            'critical_count': critical_count,
            'warning_count': warning_count,
            'info_count': info_count,
            'signature_count': signature_count,
            'anomaly_count': anomaly_count,
            'start_time': realtime_data['stats'].get('start_time')
        }
        
        return jsonify({
            'running': True,
            'stats': stats
        })
    
    return jsonify({
        'running': False,
        'stats': {
            'packet_count': 0,
            'alert_count': 0,
            'critical_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'signature_count': 0,
            'anomaly_count': 0
        }
    })


def _is_valid_ip(ip: str) -> bool:
    """Check if IP address is valid and not filtered."""
    if not ip or ip == 'N/A' or ip == '0.0.0.0':
        return False
    
    # Filter loopback
    if ip.startswith('127.'):
        return False
    
    # Filter APIPA (Automatic Private IP Addressing)
    if ip.startswith('169.254.'):
        return False
    
    # Filter link-local IPv6
    if ip.startswith('fe80:'):
        return False
    
    return True


def _detect_interface_type(iface_name: str, iface_addr: str) -> tuple:
    """
    Detect interface type and status.
    Returns: (type, status, display_name)
    """
    iface_lower = iface_name.lower()
    addr_lower = iface_addr.lower() if iface_addr else ''
    
    # Check for loopback
    if 'lo' in iface_lower or 'loopback' in iface_lower or iface_addr == '127.0.0.1':
        return ('Loopback', 'Inactive', iface_name)
    
    # Check for VPN interfaces
    vpn_keywords = ['vpn', 'tun', 'tap', 'ppp', 'l2tp', 'pptp', 'openvpn', 'nordvpn', 'expressvpn']
    if any(keyword in iface_lower for keyword in vpn_keywords):
        return ('VPN', 'Active' if _is_valid_ip(iface_addr) else 'Inactive', iface_name)
    
    # Check for virtual interfaces
    virtual_keywords = ['virtualbox', 'vmware', 'hyper-v', 'vbox', 'vmnet', 'virtual', 'wsl']
    if any(keyword in iface_lower for keyword in virtual_keywords):
        return ('Virtual', 'Active' if _is_valid_ip(iface_addr) else 'Inactive', iface_name)
    
    # Check for WiFi
    wifi_keywords = ['wi', 'wlan', 'wireless', 'wifi', '802.11']
    if any(keyword in iface_lower for keyword in wifi_keywords):
        return ('WiFi', 'Active' if _is_valid_ip(iface_addr) else 'Inactive', iface_name)
    
    # Check for Ethernet
    ethernet_keywords = ['eth', 'ethernet', 'enp', 'ens', 'en0', 'en1', 'local area connection']
    if any(keyword in iface_lower for keyword in ethernet_keywords):
        return ('Ethernet', 'Active' if _is_valid_ip(iface_addr) else 'Inactive', iface_name)
    
    # Default
    return ('Other', 'Active' if _is_valid_ip(iface_addr) else 'Inactive', iface_name)


@app.route('/api/interfaces')
@login_required
def api_interfaces():
    """Get available network interfaces with filtering."""
    if not SCAPY_AVAILABLE:
        return jsonify({'interfaces': [], 'error': 'Scapy not available'})
    
    try:
        interfaces_list = get_if_list()
        interfaces_info = []
        
        for iface in interfaces_list:
            try:
                addr = get_if_addr(iface)
                
                # Skip if no address or invalid address
                if not addr or not _is_valid_ip(addr):
                    continue
                
                # Detect interface type
                iface_type, status, display_name = _detect_interface_type(iface, addr)
                
                # Skip loopback interfaces
                if iface_type == 'Loopback':
                    continue
                
                # Skip inactive interfaces (no valid IP)
                if status == 'Inactive':
                    continue
                
                interfaces_info.append({
                    'name': iface,
                    'display_name': display_name,
                    'address': addr,
                    'type': iface_type,
                    'status': status
                })
            except Exception as e:
                # Skip interfaces that cause errors
                continue
        
        # Sort by type priority, then by name
        type_order = {
            'WiFi': 0,
            'Ethernet': 1,
            'VPN': 2,
            'Virtual': 3,
            'Other': 4
        }
        interfaces_info.sort(key=lambda x: (
            type_order.get(x['type'], 99),
            x['display_name']
        ))
        
        return jsonify({
            'interfaces': interfaces_info,
            'count': len(interfaces_info)
        })
    except Exception as e:
        return jsonify({'interfaces': [], 'error': str(e)})


@app.route('/api/pcap/list', methods=['GET'])
@login_required
def api_pcap_list():
    """List PCAP files in a directory."""
    try:
        directory = request.args.get('directory', 'data/pcap_samples')
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return jsonify({'files': [], 'error': f'Directory not found: {directory}'})
        
        if not directory_path.is_dir():
            return jsonify({'files': [], 'error': f'Path is not a directory: {directory}'})
        
        # Find all .pcap and .pcapng files
        pcap_files = []
        for ext in ['*.pcap', '*.pcapng', '*.cap']:
            pcap_files.extend(directory_path.glob(ext))
            pcap_files.extend(directory_path.glob(ext.upper()))
        
        # Sort by modification time (newest first)
        pcap_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        files_info = []
        for pcap_file in pcap_files:
            try:
                stat = pcap_file.stat()
                size_mb = stat.st_size / (1024 * 1024)
                files_info.append({
                    'name': pcap_file.name,
                    'path': str(pcap_file.relative_to(Path.cwd())),
                    'full_path': str(pcap_file.resolve()),
                    'size': stat.st_size,
                    'size_mb': round(size_mb, 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                continue
        
        return jsonify({
            'files': files_info,
            'directory': str(directory_path.resolve()),
            'count': len(files_info)
        })
    except Exception as e:
        return jsonify({'files': [], 'error': str(e)})


@app.route('/api/pcap/directories', methods=['GET'])
@login_required
def api_pcap_directories():
    """Get common PCAP directories."""
    try:
        base_dirs = [
            'data/pcap_samples',
            'data',
            '.'
        ]
        
        directories = []
        for base_dir in base_dirs:
            base_path = Path(base_dir)
            if base_path.exists() and base_path.is_dir():
                directories.append({
                    'name': base_dir,
                    'path': str(base_path.resolve()),
                    'exists': True
                })
        
        return jsonify({'directories': directories})
    except Exception as e:
        return jsonify({'directories': [], 'error': str(e)})


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/pcap/upload', methods=['POST'])
@login_required
def api_pcap_upload():
    """Upload a PCAP file."""
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'Aucun fichier sélectionné'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': f'Type de fichier non autorisé. Extensions autorisées: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        upload_dir = Path(app.config['UPLOAD_FOLDER'])
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if file already exists
        file_path = upload_dir / filename
        if file_path.exists():
            # Add timestamp to avoid overwriting
            name_parts = file_path.stem, file_path.suffix
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name_parts[0]}_{timestamp}{name_parts[1]}"
            file_path = upload_dir / filename
        
        # Save file
        file.save(str(file_path))
        
        # Get file info
        stat = file_path.stat()
        size_mb = stat.st_size / (1024 * 1024)
        
        return jsonify({
            'status': 'success',
            'message': f'Fichier uploadé avec succès: {filename}',
            'file': {
                'name': filename,
                'path': str(file_path.relative_to(Path.cwd())),
                'full_path': str(file_path.resolve()),
                'size': stat.st_size,
                'size_mb': round(size_mb, 2)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de l\'upload: {str(e)}'
        }), 500


@app.route('/api/pcap/generate-examples', methods=['POST'])
@admin_required
def api_generate_examples():
    """Generate example PCAP files."""
    try:
        import subprocess
        import sys
        
        script_path = Path('tools/generate_examples.py')
        if not script_path.exists():
            return jsonify({
                'status': 'error',
                'message': 'Script de génération introuvable'
            }), 404
        
        # Run the generation script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': 'Fichiers d\'exemple générés avec succès',
                'output': result.stdout
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Erreur lors de la génération: {result.stderr}'
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': 'Timeout lors de la génération des fichiers'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur: {str(e)}'
        }), 500


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"[WebSocket] Client connected: {request.sid}")
    emit('connected', {'message': 'Connecté au serveur IDS'})
    
    # Send existing alerts to newly connected client
    try:
        log_config = load_config().get("logging", {})
        alerts_log = log_config.get("alerts_log", "data/logs/alerts.log")
        existing_alerts = read_alerts_from_log(alerts_log, limit=20)
        for alert in existing_alerts[-20:]:  # Last 20 alerts
            emit('new_alert', alert)
    except Exception as e:
        print(f"Error sending existing alerts on connect: {e}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"[WebSocket] Client disconnected: {request.sid}")


def read_alerts_from_log(log_path: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Read alerts from log file."""
    log_file = Path(log_path)
    if not log_file.exists():
        return []
    
    alerts = []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if limit > 0:
                lines = lines[-limit:]
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    if line.startswith("{"):
                        alert = json.loads(line)
                    elif "{" in line:
                        json_start = line.find("{")
                        json_str = line[json_start:]
                        alert = json.loads(json_str)
                    else:
                        continue
                    alerts.append(alert)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading alerts log: {e}")
    
    return alerts


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

