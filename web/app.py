#!/usr/bin/env python3
"""Version web de SENTRAX AI Suite - Interface Flask"""

from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import sys
import os
import json
import socket
import threading
from datetime import datetime
from pathlib import Path
import io

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'SENTRAX-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

# Variables globales
scan_results = {}
scan_in_progress = False
current_scan_id = None

# ==================== ROUTES PRINCIPALES ====================

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    """API: Statut du serveur"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'name': 'SENTRAX AI Suite Web'
    })

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """API: Lance un scan"""
    global scan_in_progress, scan_results, current_scan_id
    
    if scan_in_progress:
        return jsonify({'error': 'Un scan est deja en cours'}), 409
    
    data = request.get_json()
    target = data.get('target', '').strip()
    scan_type = data.get('type', 'quick')
    
    if not target:
        return jsonify({'error': 'Cible non specifiee'}), 400
    
    scan_in_progress = True
    current_scan_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Lance le scan dans un thread separe
    thread = threading.Thread(target=run_scan, args=(target, scan_type, current_scan_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'scan_id': current_scan_id,
        'message': 'Scan lance',
        'status': 'in_progress'
    })

@app.route('/api/results/<scan_id>')
def api_results(scan_id):
    """API: Recupere les resultats d'un scan"""
    if scan_id in scan_results:
        return jsonify({
            'scan_id': scan_id,
            'status': 'completed',
            'results': scan_results[scan_id]
        })
    else:
        return jsonify({
            'scan_id': scan_id,
            'status': 'pending',
            'message': 'Scan en cours ou non trouve'
        })

@app.route('/api/scanners')
def api_scanners():
    """API: Liste des scanners disponibles"""
    scanners = [
        {'id': 'quick', 'name': 'Scan Rapide', 'ports': 23, 'time': '~5 secondes'},
        {'id': 'full', 'name': 'Scan Complet', 'ports': 1000, 'time': '~30 secondes'},
        {'id': 'custom', 'name': 'Scan Personnalise', 'ports': 'variable', 'time': 'variable'}
    ]
    return jsonify(scanners)

# ==================== FONCTIONS DE SCAN ====================

def run_scan(target, scan_type, scan_id):
    """Execute un scan reseau"""
    global scan_results, scan_in_progress
    
    results = {
        'target': target,
        'scan_type': scan_type,
        'timestamp': datetime.now().isoformat(),
        'open_ports': [],
        'error': None
    }
    
    try:
        # Resolution DNS
        ip = socket.gethostbyname(target)
        results['ip'] = ip
        
        # Selection des ports selon le type
        if scan_type == 'quick':
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 
                     993, 995, 3306, 3389, 5432, 5900, 8080, 8443]
        elif scan_type == 'full':
            ports = list(range(1, 1001))
        else:
            ports = [22, 80, 443, 8080]
        
        # Scan des ports
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)
                result = sock.connect_ex((ip, port))
                
                if result == 0:
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = "unknown"
                    
                    results['open_ports'].append({
                        'port': port,
                        'service': service,
                        'status': 'open'
                    })
                sock.close()
            except:
                pass
        
        results['total_open'] = len(results['open_ports'])
        
    except Exception as e:
        results['error'] = str(e)
    
    finally:
        scan_results[scan_id] = results
        scan_in_progress = False

# ==================== TEMPLATE HTML ====================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SENTRAX AI Suite - Web Scanner</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
            font-family: 'Courier New', 'Consolas', monospace;
            color: #00ff88;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Header */
        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #00ff88;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            text-shadow: 0 0 10px #00ff88;
            letter-spacing: 2px;
        }
        
        .header p {
            color: #888;
            margin-top: 10px;
        }
        
        /* Scan Card */
        .scan-card {
            background: #111;
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 0 20px rgba(0,255,136,0.1);
        }
        
        .scan-card h2 {
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        
        .input-group {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .input-group input {
            flex: 1;
            padding: 12px;
            background: #1a1a1a;
            border: 1px solid #00ff88;
            color: #00ff88;
            font-family: monospace;
            font-size: 14px;
            border-radius: 5px;
        }
        
        .input-group input:focus {
            outline: none;
            box-shadow: 0 0 10px #00ff88;
        }
        
        .scan-type {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .scan-type label {
            display: flex;
            align-items: center;
            gap: 5px;
            cursor: pointer;
        }
        
        .scan-type input {
            cursor: pointer;
        }
        
        button {
            background: #00ff88;
            color: #000;
            border: none;
            padding: 12px 30px;
            font-size: 16px;
            font-weight: bold;
            font-family: monospace;
            cursor: pointer;
            border-radius: 5px;
            transition: all 0.3s;
        }
        
        button:hover {
            background: #00cc66;
            transform: scale(1.02);
            box-shadow: 0 0 20px #00ff88;
        }
        
        button:disabled {
            background: #444;
            cursor: not-allowed;
            transform: none;
        }
        
        /* Results */
        .results-card {
            background: #111;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            display: none;
        }
        
        .results-card.active {
            display: block;
        }
        
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }
        
        .results-header h3 {
            color: #00ff88;
        }
        
        .results-content {
            background: #0a0a0a;
            padding: 15px;
            border-radius: 5px;
            max-height: 400px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 13px;
        }
        
        .port-item {
            padding: 8px;
            border-bottom: 1px solid #1a1a1a;
            font-family: monospace;
        }
        
        .port-item:hover {
            background: #1a1a1a;
        }
        
        .port-number {
            color: #00ff88;
            font-weight: bold;
        }
        
        .port-service {
            color: #888;
            margin-left: 20px;
        }
        
        .error {
            color: #ff4444;
        }
        
        .success {
            color: #00ff88;
        }
        
        /* Loading */
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid #333;
            border-top: 3px solid #00ff88;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 20px;
            color: #555;
            font-size: 12px;
            border-top: 1px solid #1a1a1a;
            margin-top: 30px;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1a1a1a;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #00ff88;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 SENTRAX AI SUITE</h1>
            <p>Web Scanner - Interface de cybersecurite nouvelle generation</p>
        </div>
        
        <div class="scan-card">
            <h2>📡 Nouveau scan</h2>
            <div class="input-group">
                <input type="text" id="target" placeholder="IP ou domaine (ex: scanme.nmap.org, google.com, 192.168.1.1)">
            </div>
            <div class="scan-type">
                <label>
                    <input type="radio" name="scan_type" value="quick" checked> Scan rapide (23 ports)
                </label>
                <label>
                    <input type="radio" name="scan_type" value="full"> Scan complet (1000 ports)
                </label>
                <label>
                    <input type="radio" name="scan_type" value="custom"> Scan personnalise (22,80,443)
                </label>
            </div>
            <button onclick="startScan()" id="scanBtn">🚀 LANCER LE SCAN</button>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Scan en cours... Veuillez patienter</p>
        </div>
        
        <div class="results-card" id="resultsCard">
            <div class="results-header">
                <h3>📊 Resultats du scan</h3>
                <button onclick="exportResults()" style="padding: 5px 15px; font-size: 12px;">💾 Exporter</button>
            </div>
            <div class="results-content" id="resultsContent">
                <span class="port-item">En attente des resultats...</span>
            </div>
        </div>
        
        <div class="footer">
            SENTRAX AI Suite v1.0 | Web Interface | Developpe par Pat's Ndaye
        </div>
    </div>
    
    <script>
        let currentScanId = null;
        
        async function startScan() {
            const target = document.getElementById('target').value.trim();
            const scanType = document.querySelector('input[name="scan_type"]:checked').value;
            
            if (!target) {
                alert('Veuillez entrer une IP ou un domaine');
                return;
            }
            
            // Desactiver le bouton
            const btn = document.getElementById('scanBtn');
            btn.disabled = true;
            btn.textContent = '⏳ SCAN EN COURS...';
            
            // Afficher le chargement
            document.getElementById('loading').classList.add('active');
            document.getElementById('resultsCard').classList.remove('active');
            
            try {
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target: target, type: scanType})
                });
                
                const data = await response.json();
                
                if (data.scan_id) {
                    currentScanId = data.scan_id;
                    checkResults();
                } else {
                    showError(data.error || 'Erreur lors du lancement du scan');
                }
            } catch (error) {
                showError('Erreur de connexion: ' + error.message);
            }
        }
        
        async function checkResults() {
            if (!currentScanId) return;
            
            try {
                const response = await fetch(`/api/results/${currentScanId}`);
                const data = await response.json();
                
                if (data.status === 'completed') {
                    displayResults(data.results);
                    document.getElementById('loading').classList.remove('active');
                    document.getElementById('scanBtn').disabled = false;
                    document.getElementById('scanBtn').textContent = '🚀 LANCER LE SCAN';
                } else {
                    // Verifier dans 1 seconde
                    setTimeout(checkResults, 1000);
                }
            } catch (error) {
                showError('Erreur lors de la recuperation des resultats');
            }
        }
        
        function displayResults(results) {
            const container = document.getElementById('resultsContent');
            const card = document.getElementById('resultsCard');
            
            if (results.error) {
                container.innerHTML = `<span class="error">❌ Erreur: ${results.error}</span>`;
                card.classList.add('active');
                return;
            }
            
            let html = `
                <div class="port-item"><strong>Cible:</strong> ${results.target}</div>
                <div class="port-item"><strong>IP:</strong> ${results.ip || 'N/A'}</div>
                <div class="port-item"><strong>Type:</strong> ${results.scan_type}</div>
                <div class="port-item"><strong>Date:</strong> ${new Date(results.timestamp).toLocaleString()}</div>
                <div class="port-item"><strong>Total ports ouverts:</strong> ${results.total_open}</div>
                <div style="margin-top: 15px; margin-bottom: 10px;"><strong>Details:</strong></div>
            `;
            
            if (results.open_ports.length === 0) {
                html += '<div class="port-item">Aucun port ouvert trouve</div>';
            } else {
                for (const port of results.open_ports) {
                    html += `
                        <div class="port-item">
                            <span class="port-number">Port ${port.port}</span>
                            <span class="port-service">${port.service}</span>
                            <span style="color:#00ff88;"> ✓ ouvert</span>
                        </div>
                    `;
                }
            }
            
            container.innerHTML = html;
            card.classList.add('active');
        }
        
        function showError(message) {
            const container = document.getElementById('resultsContent');
            container.innerHTML = `<span class="error">❌ ${message}</span>`;
            document.getElementById('resultsCard').classList.add('active');
            document.getElementById('loading').classList.remove('active');
            document.getElementById('scanBtn').disabled = false;
            document.getElementById('scanBtn').textContent = '🚀 LANCER LE SCAN';
        }
        
        function exportResults() {
            const content = document.getElementById('resultsContent').innerText;
            const blob = new Blob([content], {type: 'text/plain'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `SENTRAX_scan_${new Date().toISOString()}.txt`;
            a.click();
            URL.revokeObjectURL(url);
        }
        
        // Entree au clavier
        document.getElementById('target').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                startScan();
            }
        });
    </script>
</body>
</html>
'''

# ==================== LANCEMENT ====================

if __name__ == '__main__':
    print("="*50)
    print("🧠 SENTRAX AI Suite - Web Interface")
    print("="*50)
    print(f"\n📡 Serveur demarre sur http://localhost:5000")
    print(f"📡 Acces depuis le reseau: http://{socket.gethostbyname(socket.gethostname())}:5000")
    print("\n⚠️  Pour arreter: Ctrl+C")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)