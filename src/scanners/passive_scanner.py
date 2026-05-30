#!/usr/bin/env python3
"""Passive Scanner - 0 paquet envoye, indetectable"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import dns.resolver
from datetime import datetime

class PassiveScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Passive Scanner - Zero Footprint")
        self.root.geometry("800x600")
        self.root.configure(bg="#0a0a0a")
        self.setup_ui()
    
    def setup_ui(self):
        title = tk.Label(self.root, text="PASSIVE SCANNER", 
                        font=("Arial", 20, "bold"), fg="#ff00ff", bg="#0a0a0a")
        title.pack(pady=20)
        
        subtitle = tk.Label(self.root, text="0 paquet envoye vers la cible | Indetectable par firewalls",
                           font=("Arial", 10), fg="#666666", bg="#0a0a0a")
        subtitle.pack()
        
        frame = tk.Frame(self.root, bg="#0a0a0a")
        frame.pack(pady=20)
        
        tk.Label(frame, text="Domaine:", fg="white", bg="#0a0a0a", 
                font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        self.target_entry = tk.Entry(frame, width=35, font=("Arial", 12), 
                                      bg="#1a1a1a", fg="#ff00ff", insertbackground="white")
        self.target_entry.pack(side=tk.LEFT, padx=5)
        self.target_entry.insert(0, "google.com")
        
        self.scan_btn = tk.Button(self.root, text="ANALYSE PASSIVE", command=self.scan,
                                  bg="#ff00ff", fg="#000000", font=("Arial", 12, "bold"), 
                                  padx=30, pady=10, cursor="hand2")
        self.scan_btn.pack(pady=20)
        
        self.result_box = tk.Text(self.root, bg="#1a1a1a", fg="#ff00ff", 
                                  font=("Consolas", 10), wrap=tk.WORD)
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(self.result_box)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_box.yview)
        
        self.status = tk.Label(self.root, text="Pret", fg="#666666", bg="#0a0a0a", font=("Arial", 9))
        self.status.pack(pady=5)
    
    def get_dns_records(self, domain):
        records = {}
        types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
        
        for record_type in types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                records[record_type] = [str(r) for r in answers]
            except:
                records[record_type] = []
        
        return records
    
    def scan(self):
        domain = self.target_entry.get().strip()
        if not domain:
            messagebox.showerror("Erreur", "Entrez un domaine")
            return
        
        self.result_box.delete(1.0, tk.END)
        self.scan_btn.config(state=tk.DISABLED, text="ANALYSE PASSIVE...")
        self.status.config(text=f"Analyse passive de {domain}...")
        
        def do_scan():
            try:
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"ANALYSE PASSIVE DE: {domain}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "MODE: 0 PAQUET ENVOYE VERS LA CIBLE\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"DATE: {datetime.now()}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*60 + "\n\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "[1] RESOLUTION DNS DIRECTE\n"))
                try:
                    ip = socket.gethostbyname(domain)
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"  IP: {ip}\n"))
                    
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                        self.root.after(0, lambda: self.result_box.insert(tk.END, f"  Reverse DNS: {hostname}\n"))
                    except:
                        pass
                except:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "  Impossible de resoudre le domaine\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n[2] ENREGISTREMENTS DNS COMPLETS\n"))
                dns_data = self.get_dns_records(domain)
                
                if dns_data['A']:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"  A (IPv4): {', '.join(dns_data['A'][:5])}\n"))
                
                if dns_data['AAAA']:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"  AAAA (IPv6): {', '.join(dns_data['AAAA'][:3])}\n"))
                
                if dns_data['MX']:
                    mx_servers = []
                    for mx in dns_data['MX'][:5]:
                        mx_servers.append(mx.split()[-1] if ' ' in mx else mx)
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"  MX (Mail): {', '.join(mx_servers)}\n"))
                
                if dns_data['NS']:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"  NS (Name servers): {', '.join(dns_data['NS'][:5])}\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n[3] RECHERCHE SOUS-DOMAINES PASSIVE\n"))
                
                common_subdomains = ['www', 'mail', 'ftp', 'admin', 'blog', 'shop', 'api', 'dev', 'test', 'vpn', 'remote', 'webmail', 'cpanel', 'ns1', 'ns2', 'mx1', 'mx2']
                
                found_subdomains = []
                for sub in common_subdomains:
                    try:
                        test_domain = f"{sub}.{domain}"
                        dns.resolver.resolve(test_domain, 'A')
                        found_subdomains.append(test_domain)
                        self.root.after(0, lambda sd=test_domain: self.result_box.insert(tk.END, f"  {sd}\n"))
                    except:
                        pass
                
                if not found_subdomains:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "  Aucun sous-domaine commun trouve\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n[4] ANALYSE SERVEURS DE MAIL\n"))
                try:
                    mx_records = dns.resolver.resolve(domain, 'MX')
                    for mx in mx_records:
                        mx_server = str(mx.exchange)
                        priority = mx.preference
                        self.root.after(0, lambda s=mx_server, p=priority: 
                                      self.result_box.insert(tk.END, f"  Serveur: {s} (priorite {p})\n"))
                        
                        try:
                            mx_ip = socket.gethostbyname(mx_server)
                            self.root.after(0, lambda ip=mx_ip: self.result_box.insert(tk.END, f"    IP: {ip}\n"))
                        except:
                            pass
                except:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "  Aucun serveur MX trouve\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n[5] RECOMMANDATIONS DE SECURITE\n"))
                
                has_spf = False
                for txt in dns_data.get('TXT', []):
                    if 'v=spf1' in txt.lower():
                        has_spf = True
                        self.root.after(0, lambda: self.result_box.insert(tk.END, "  SPF: Configure (protection anti-spoofing)\n"))
                        break
                
                if not has_spf:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "  SPF: NON configure - Risque de spoofing email\n"))
                
                has_dmarc = False
                try:
                    dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
                    has_dmarc = True
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "  DMARC: Configure (protection email)\n"))
                except:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "  DMARC: NON configure\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n" + "="*60 + "\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "RESUME ANALYSE PASSIVE\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"  Domaine: {domain}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"  Sous-domaines trouves: {len(found_subdomains)}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "  Aucun paquet envoye → Indetectable\n"))
                
                self.status.config(text="Analyse passive terminee")
                
            except Exception as e:
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Erreur: {str(e)}\n"))
                self.status.config(text="Erreur")
            finally:
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="ANALYSE PASSIVE"))
        
        threading.Thread(target=do_scan, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

def main():
    app = PassiveScanner()
    app.run()

if __name__ == "__main__":
    main()