#!/usr/bin/env python3
"""Gestionnaire de rapports par email pour SENTRAX"""

import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path

class EmailReporter:
    """Envoie des rapports de scan par email"""
    
    def __init__(self, config_file=None):
        """
        Initialise le reporter email
        config_file: chemin vers fichier de configuration JSON
        """
        self.config = self.load_config(config_file)
        self.enabled = self.config.get('enabled', False)
    
    def load_config(self, config_file):
        """Charge la configuration email"""
        default_config = {
            'enabled': False,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': '',
            'password': '',
            'from_email': '',
            'to_emails': []
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            except:
                pass
        
        return default_config
    
    def save_config(self, config_file):
        """Sauvegarde la configuration"""
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def is_configured(self):
        """Vérifie si l'email est configuré"""
        return (self.enabled and 
                self.config.get('username') and 
                self.config.get('password'))
    
    def send_scan_report(self, scan_results, pdf_path=None):
        """
        Envoie un rapport de scan par email
        scan_results: dict des résultats du scan
        pdf_path: chemin vers le PDF (optionnel)
        """
        if not self.is_configured():
            print("Email non configuré. Rapport non envoyé.")
            return False
        
        to_emails = self.config.get('to_emails', [])
        if not to_emails:
            print("Aucun destinataire configuré.")
            return False
        
        subject = f"[SENTRAX] Scan Report - {scan_results.get('target', 'Unknown')}"
        
        # Construire le corps HTML
        html = self.build_html_report(scan_results)
        
        success = True
        for to_email in to_emails:
            try:
                self._send_email(to_email, subject, html, pdf_path)
                print(f"Rapport envoyé à {to_email}")
            except Exception as e:
                print(f"Erreur envoi à {to_email}: {e}")
                success = False
        
        return success
    
    def send_alert(self, vulnerability):
        """
        Envoie une alerte pour une vulnérabilité critique
        vulnerability: dict avec infos CVE
        """
        if not self.is_configured():
            return False
        
        subject = f"[ALERTE] Vulnérabilité critique - {vulnerability.get('cve_id', 'Unknown')}"
        
        html = f"""
        <html>
        <body style="font-family: monospace;">
            <h1 style="color: #ff4444;">⚠️ ALERTE DE SÉCURITÉ</h1>
            <p><strong>CVE:</strong> {vulnerability.get('cve_id', 'N/A')}</p>
            <p><strong>Nom:</strong> {vulnerability.get('name', 'N/A')}</p>
            <p><strong>Port:</strong> {vulnerability.get('port', 'N/A')}</p>
            <p><strong>Service:</strong> {vulnerability.get('service', 'N/A')}</p>
            <p><strong>Sévérité:</strong> <span style="color: #ff4444;">{vulnerability.get('severity', 'N/A')}</span></p>
            <p><strong>CVSS Score:</strong> {vulnerability.get('cvss_score', 'N/A')}</p>
            <hr>
            <p>Une action immédiate est recommandée.</p>
            <p>---</p>
            <p>SENTRAX - Cybersecurity Suite</p>
        </body>
        </html>
        """
        
        success = True
        for to_email in self.config.get('to_emails', []):
            try:
                self._send_email(to_email, subject, html)
                print(f"Alerte envoyée à {to_email}")
            except Exception as e:
                print(f"Erreur envoi alerte: {e}")
                success = False
        
        return success
    
    def send_scheduled_report(self, scans_history):
        """Envoie un rapport périodique (hebdomadaire/mensuel)"""
        if not self.is_configured():
            return False
        
        subject = f"[SENTRAX] Rapport périodique - {datetime.now().strftime('%Y-%m-%d')}"
        
        html = f"""
        <html>
        <body>
            <h1>📊 SENTRAX - Rapport périodique</h1>
            <p><strong>Période:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p><strong>Total scans:</strong> {len(scans_history)}</p>
            <h2>Résumé des scans</h2>
            <table border="1" cellpadding="5">
                <tr><th>Date</th><th>Cible</th><th>Ports ouverts</th><th>Status</th></tr>
        """
        
        for scan in scans_history[:20]:
            html += f"""
                <tr>
                    <td>{scan.get('created_at', 'N/A')}</td>
                    <td>{scan.get('target', 'N/A')}</td>
                    <td>{len(scan.get('results', {}).get('open_ports', []))}</td>
                    <td>{scan.get('status', 'N/A')}</td>
                </tr>
            """
        
        html += """
            </table>
            <p>---</p>
            <p>SENTRAX - Cybersecurity Suite</p>
        </body>
        </html>
        """
        
        success = True
        for to_email in self.config.get('to_emails', []):
            try:
                self._send_email(to_email, subject, html)
                print(f"Rapport périodique envoyé à {to_email}")
            except Exception as e:
                print(f"Erreur: {e}")
                success = False
        
        return success
    
    def build_html_report(self, scan_results):
        """Construit le rapport HTML"""
        open_ports = scan_results.get('open_ports', [])
        ip = scan_results.get('ip', 'N/A')
        os_info = scan_results.get('os', {})
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff88; }}
                .header {{ border-bottom: 2px solid #00ff88; margin-bottom: 20px; }}
                .critical {{ color: #ff4444; }}
                .high {{ color: #ff8844; }}
                .medium {{ color: #ffcc00; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #333; padding: 8px; text-align: left; }}
                th {{ background: #1a1a1a; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 SENTRAX Scan Report</h1>
                <p><strong>Cible:</strong> {scan_results.get('target', 'N/A')}</p>
                <p><strong>IP:</strong> {ip}</p>
                <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>OS détecté:</strong> {os_info.get('guess', 'N/A')}</p>
            </div>
            
            <h2>📊 Résultats</h2>
            <table>
                <tr><th>Port</th><th>Service</th><th>Statut</th><th>Méthode</th></tr>
        """
        
        for port in open_ports:
            html += f"""
                <tr>
                    <td>{port.get('port', 'N/A')}</td>
                    <td>{port.get('service', 'unknown')}</td>
                    <td style="color: #00ff88;">OUVERT</td>
                    <td>{port.get('method', 'tcp')}</td>
                </tr>
            """
        
        html += f"""
            </table>
            <p><strong>Total ports ouverts:</strong> {len(open_ports)}</p>
            <hr>
            <p><em>Généré automatiquement par SENTRAX v3.0</em></p>
            <p>© 2024 Patrick Ndaye</p>
        </body>
        </html>
        """
        
        return html
    
    def _send_email(self, to_email, subject, html_content, pdf_path=None):
        """Envoie l'email (interne)"""
        msg = MIMEMultipart()
        msg['From'] = self.config.get('from_email') or self.config['username']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_content, 'html'))
        
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                part = MIMEBase('application', 'pdf')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
                msg.attach(part)
        
        with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
            server.starttls()
            server.login(self.config['username'], self.config['password'])
            server.send_message(msg)


# Configuration helper
def setup_email_config():
    """Assistant de configuration email"""
    print("="*60)
    print("📧 Configuration Email SENTRAX")
    print("="*60)
    print("\nPour Gmail, utilisez un mot de passe d'application:")
    print("https://myaccount.google.com/apppasswords\n")
    
    smtp_server = input("Serveur SMTP [smtp.gmail.com]: ") or "smtp.gmail.com"
    smtp_port = input("Port SMTP [587]: ") or "587"
    username = input("Email (expéditeur): ")
    password = input("Mot de passe (ou mot de passe application): ")
    from_email = input("Email d'envoi (identique si vide): ") or username
    
    print("\nDestinataires (séparés par des virgules):")
    to_emails = [e.strip() for e in input("Emails: ").split(",") if e.strip()]
    
    config = {
        'enabled': True,
        'smtp_server': smtp_server,
        'smtp_port': int(smtp_port),
        'username': username,
        'password': password,
        'from_email': from_email,
        'to_emails': to_emails
    }
    
    config_dir = Path.home() / ".SENTRAX"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "email_config.json"
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration sauvegardée dans {config_file}")
    return config_file

if __name__ == "__main__":
    setup_email_config()