#!/usr/bin/env python3
"""Generateur de rapports pour SENTRAX AI Suite"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

class ReportGenerator:
    """Genere des rapports dans differents formats"""
    
    @staticmethod
    def generate_text_report(results: List[Dict], target: str, scan_type: str) -> str:
        """Genere un rapport au format texte"""
        
        report = []
        report.append("="*70)
        report.append("SENTRAX AI SUITE - RAPPORT DE SCAN")
        report.append("="*70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Cible: {target}")
        report.append(f"Type de scan: {scan_type}")
        report.append(f"Ports scannes: {len(results)}")
        report.append("="*70)
        report.append("")
        
        if results:
            report.append("RESULTATS DETAILLES:")
            report.append("-"*50)
            
            for r in results:
                port = r.get('port', '?')
                service = r.get('service', 'unknown')
                status = r.get('status', 'closed')
                banner = r.get('banner', '')
                
                if status == 'open':
                    report.append(f"  [+] Port {port}: {service}")
                    if banner:
                        report.append(f"      Banner: {banner[:100]}")
            report.append("")
        
        report.append("-"*50)
        report.append(f"Resume: {len([r for r in results if r.get('status') == 'open'])} ports ouverts")
        report.append("="*70)
        
        return "\n".join(report)
    
    @staticmethod
    def generate_json_report(results: List[Dict], target: str, scan_type: str) -> str:
        """Genere un rapport au format JSON"""
        
        report = {
            "metadata": {
                "tool": "SENTRAX AI Suite",
                "version": "1.0.0",
                "date": datetime.now().isoformat(),
                "target": target,
                "scan_type": scan_type
            },
            "results": results,
            "summary": {
                "total_ports": len(results),
                "open_ports": len([r for r in results if r.get('status') == 'open']),
                "closed_ports": len([r for r in results if r.get('status') == 'closed'])
            }
        }
        
        return json.dumps(report, indent=2, ensure_ascii=False)
    
    @staticmethod
    def generate_csv_report(results: List[Dict], target: str, scan_type: str) -> str:
        """Genere un rapport au format CSV"""
        
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-tete
        writer.writerow(['Date', 'Target', 'ScanType', 'Port', 'Service', 'Status', 'Banner'])
        
        # Donnees
        for r in results:
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                target,
                scan_type,
                r.get('port', ''),
                r.get('service', ''),
                r.get('status', ''),
                r.get('banner', '')[:200]
            ])
        
        return output.getvalue()
    
    @staticmethod
    def save_report(content: str, filename: str, format_type: str = "txt"):
        """Sauvegarde un rapport dans un fichier"""
        
        # Ajoute l'extension si manquante
        if not Path(filename).suffix:
            filename = f"{filename}.{format_type}"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filename
    
    @staticmethod
    def generate_html_report(results: List[Dict], target: str, scan_type: str) -> str:
        """Genere un rapport au format HTML"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SENTRAX AI - Rapport {target}</title>
    <style>
        body {{
            background: #0a0a0a;
            color: #00ff88;
            font-family: 'Consolas', monospace;
            margin: 20px;
        }}
        h1 {{
            color: #00ff88;
            text-align: center;
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
        .open {{
            color: #00ff88;
        }}
        .summary {{
            background: #1a1a1a;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <h1>🧠 SENTRAX AI Suite - Rapport</h1>
    
    <div class="info">
        <strong>Cible:</strong> {target}<br>
        <strong>Type:</strong> {scan_type}<br>
        <strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    
    <h2>Resultats du scan</h2>
    <table>
        <tr>
            <th>Port</th>
            <th>Service</th>
            <th>Statut</th>
            <th>Banner</th>
        </tr>
"""
        
        for r in results:
            status_class = "open" if r.get('status') == 'open' else ""
            status_text = "✓ OUVERT" if r.get('status') == 'open' else "✗ FERME"
            html += f"""
        <tr>
            <td>{r.get('port', '-')}</td>
            <td>{r.get('service', '-')}</td>
            <td class="{status_class}">{status_text}</td>
            <td>{r.get('banner', '-')[:80]}</td>
        </tr>"""
        
        html += f"""
    </table>
    
    <div class="summary">
        <strong>Resume:</strong><br>
        - Total ports scannes: {len(results)}<br>
        - Ports ouverts: {len([r for r in results if r.get('status') == 'open'])}<br>
        - Ports fermes: {len([r for r in results if r.get('status') == 'closed'])}
    </div>
    
    <div class="footer">
        SENTRAX AI Suite v1.0 | Genere automatiquement
    </div>
</body>
</html>
"""
        return html