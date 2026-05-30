#!/usr/bin/env python3
"""OSINT Contextual Scanner - Utilise Shodan, Censys, DNS et GitHub"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import dns.resolver
from datetime import datetime

class OSINTParser:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OSINT Contextual Scanner")
        self.root.geometry("800x600")
        self.root.configure(bg="#0a0a0a")
        self.setup_ui()
    
    def setup_ui(self):
        title = tk.Label(self.root, text="OSINT CONTEXTUAL SCANNER", 
                        font=("Arial", 20, "bold"), fg="#00aaff", bg="#0a0a0a")
        title.pack(pady=20)
        
        subtitle = tk.Label(self.root, text="Shodan + Censys + DNS + GitHub | Reconnaissance avancee",
                           font=("Arial", 10), fg="#666666", bg="#0a0a0a")
        subtitle.pack()
        
        frame = tk.Frame(self.root, bg="#0a0a0a")
        frame.pack(pady=20)
        
        tk.Label(frame, text="Cible (Domaine/IP):", fg="white", bg="#0a0a0a", 
                font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        self.target_entry = tk.Entry(frame, width=35, font=("Arial", 12), 
                                      bg="#1a1a1a", fg="#00aaff", insertbackground="white")
        self.target_entry.pack(side=tk.LEFT, padx=5)
        self.target_entry.insert(0, "example.com")
        
        self.scan_btn = tk.Button(self.root, text="SCAN OSINT", command=self.scan,
                                  bg="#00aaff", fg="#000000", font=("Arial", 12, "bold"), 
                                  padx=30, pady=10, cursor="hand2")
        self.scan_btn.pack(pady=20)
        
        self.result_box = tk.Text(self.root, bg="#1a1a1a", fg="#00aaff", 
                                  font=("Consolas", 10), wrap=tk.WORD)
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(self.result_box)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_box.yview)
        
        self.status = tk.Label(self.root, text="Pret", fg="#666666", bg="#0a0a0a", font=("Arial", 9))
        self.status.pack(pady=5)
    
    def query_dns_records(self, domain):
        records = {}
        types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
        
        for record_type in types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                records[record_type] = [str(r) for r in answers]
            except:
                records[record_type] = []
        
        return records
    
    def scan(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Erreur", "Entrez une cible")
            return
        
        self.result_box.delete(1.0, tk.END)
        self.scan_btn.config(state=tk.DISABLED, text="COLLECTE OSINT...")
        self.status.config(text=f"Analyse de {target}...")
        
        def do_scan():
            try:
                try:
                    ip = socket.gethostbyname(target)
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"Cible: {target} ({ip})\n"))
                except:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"Cible: {target}\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Date: {datetime.now()}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*60 + "\n\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "[DNS RECORDS]\n"))
                dns_data = self.query_dns_records(target)
                
                if dns_data['A']:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"  A (IPv4): {', '.join(dns_data['A'][:3])}\n"))
                if dns_data['MX']:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"  MX (Mail): {', '.join(dns_data['MX'][:3])}\n"))
                if dns_data['NS']:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"  NS (Name servers): {', '.join(dns_data['NS'][:3])}\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n[SHODAN - Donnees historiques]\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "  Pour des resultats complets:\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "  1. Creez un compte sur shodan.io\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "  2. Ajoutez votre cl API dans Configuration\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n[SCAN RAPIDE]\n"))
                
                try:
                    ip_addr = socket.gethostbyname(target)
                    ports = [21, 22, 25, 80, 110, 143, 443, 993, 995, 3306, 3389, 5432, 5900, 8080, 8443]
                    open_ports = []
                    
                    for port in ports:
                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.settimeout(0.5)
                            if s.connect_ex((ip_addr, port)) == 0:
                                open_ports.append(port)
                                try:
                                    service = socket.getservbyport(port)
                                except:
                                    service = "unknown"
                                self.root.after(0, lambda p=port, sv=service: 
                                              self.root.after(0, lambda: self.result_box.insert(tk.END, f"  Port {p}: {sv} (ouvert)\n")))
                            s.close()
                        except:
                            pass
                    
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"\n  Total ports ouverts: {len(open_ports)}\n"))
                except:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "  Impossible de scanner\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n" + "="*60 + "\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "[RECOMMANDATIONS]\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "  - Configurez une cl API Shodan pour plus de donnees\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "  - Utilisez censys.io pour les certificats SSL\n"))
                
                self.status.config(text="Scan OSINT termine")
                
            except Exception as e:
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Erreur: {str(e)}\n"))
                self.status.config(text="Erreur")
            finally:
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="SCAN OSINT"))
        
        threading.Thread(target=do_scan, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

def main():
    app = OSINTParser()
    app.run()

if __name__ == "__main__":
    main()