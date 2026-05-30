#!/usr/bin/env python3
"""Gestionnaire d'export multi-formats"""

import json
import csv
from datetime import datetime
from pathlib import Path

class ExportManager:
    """Exporte les resultats dans differents formats"""
    
    @staticmethod
    def export_json(results: dict, filename: str) -> str:
        """Export en JSON"""
        output = {
            'metadata': {
                'tool': 'SENTRAX AI Suite',
                'version': '2.0',
                'date': datetime.now().isoformat()
            },
            'results': results
        }
        
        filepath = Path(filename).with_suffix('.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    @staticmethod
    def export_csv(results: dict, filename: str) -> str:
        """Export en CSV"""
        filepath = Path(filename).with_suffix('.csv')
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Port', 'Service', 'Status', 'Banner', 'OS', 'CVEs'])
            
            for port in results.get('open_ports', []):
                writer.writerow([
                    port.get('port', ''),
                    port.get('service', ''),
                    'OPEN',
                    port.get('banner', '')[:100],
                    results.get('os', {}).get('guess', ''),
                    ', '.join([cve['cve_id'] for cve in port.get('vulnerabilities', [])])
                ])
        
        return str(filepath)
    
    @staticmethod
    def export_html(results: dict, filename: str) -> str:
        """Export en HTML avec style"""
        filepath = Path(filename).with_suffix('.html')
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SENTRAX AI Suite - Rapport</title>
    <style>
        body {{
            background: #0a0a0a;
            color: #00ff88;
            font-family: 'Courier New', monospace;
            margin: 20px;
        }}
        h1 {{
            color: #00ff88;
            border-bottom: 2px solid #00ff88;
            padding-bottom: 10px;
        }}
        .info {{
            background: #1a1a1a;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #333;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background: #00ff88;
            color: #000;
        }}
        .critical {{ color: #ff4444; }}
        .high {{ color: #ff8844; }}
        .medium {{ color: #ffcc00; }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <h1>🔍 SENTRAX AI Suite - Rapport d'analyse</h1>
    
    <div class="info">
        <strong>Cible:</strong> {results.get('target', 'N/A')}<br>
        <strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        <strong>OS detecte:</strong> {results.get('os', {}).get('guess', 'Inconnu')}
    </div>
    
    <h2>📊 Ports ouverts</h2>
    <table>
        <thead>
            <tr><th>Port</th><th>Service</th><th>Banner</th><th>Vulnerabilites</th></tr>
        </thead>
        <tbody>
'''
        
        for port in results.get('open_ports', []):
            vulns = '<br>'.join([f"{cve['cve_id']} ({cve['severity']})" 
                                for cve in port.get('vulnerabilities', [])])
            html += f'''
            <tr>
                <td>{port.get('port', '')}</td>
                <td>{port.get('service', '')}</td>
                <td>{port.get('banner', '')[:80]}</td>
                <td class="{port.get('severity', '').lower()}">{vulns}</td>
            </tr>'''
        
        html += '''
        </tbody>
    </table>
    
    <div class="footer">
        SENTRAX AI Suite v2.0 - Rapport genere automatiquement
    </div>
</body>
</html>
'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    @staticmethod
    def export_txt(results: dict, filename: str) -> str:
        """Export en TXT"""
        filepath = Path(filename).with_suffix('.txt')
        
        content = []
        content.append("="*60)
        content.append("SENTRAX AI SUITE - RAPPORT DE SCAN")
        content.append("="*60)
        content.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"Cible: {results.get('target', 'N/A')}")
        content.append(f"OS: {results.get('os', {}).get('guess', 'Inconnu')}")
        content.append("="*60)
        content.append("")
        content.append("PORTS OUVERTS:")
        content.append("-"*40)
        
        for port in results.get('open_ports', []):
            content.append(f"  Port {port.get('port')}: {port.get('service')}")
            if port.get('banner'):
                content.append(f"    Banner: {port.get('banner')[:100]}")
        
        content.append("")
        content.append("="*60)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        return str(filepath)