#!/usr/bin/env python3
"""DNS Scanner - Enumeration DNS avancee"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import dns.resolver
from datetime import datetime

class DNSScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DNS Scanner")
        self.root.geometry("800x600")
        self.root.configure(bg="#0a0a0a")
        self.setup_ui()
    
    def setup_ui(self):
        title = tk.Label(self.root, text="DNS SCANNER", 
                        font=("Arial", 20, "bold"), fg="#ff44cc", bg="#0a0a0a")
        title.pack(pady=20)
        
        subtitle = tk.Label(self.root, text="Enumeration DNS | Transfert de zone",
                           font=("Arial", 10), fg="#666666", bg="#0a0a0a")
        subtitle.pack()
        
        frame = tk.Frame(self.root, bg="#0a0a0a")
        frame.pack(pady=20)
        
        tk.Label(frame, text="Domaine:", fg="white", bg="#0a0a0a", 
                font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        self.target_entry = tk.Entry(frame, width=35, font=("Arial", 12), 
                                      bg="#1a1a1a", fg="#ff44cc")
        self.target_entry.pack(side=tk.LEFT, padx=5)
        self.target_entry.insert(0, "example.com")
        
        self.scan_btn = tk.Button(self.root, text="SCAN DNS", command=self.scan,
                                  bg="#ff44cc", fg="#000000", font=("Arial", 12, "bold"), 
                                  padx=30, pady=10)
        self.scan_btn.pack(pady=20)
        
        self.result_box = tk.Text(self.root, bg="#1a1a1a", fg="#ff44cc", 
                                  font=("Consolas", 10), wrap=tk.WORD)
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.status = tk.Label(self.root, text="Pret", fg="#666666", bg="#0a0a0a")
        self.status.pack(pady=5)
    
    def query_dns(self, domain, record_type):
        try:
            answers = dns.resolver.resolve(domain, record_type)
            return [str(r) for r in answers]
        except:
            return []
    
    def scan(self):
        domain = self.target_entry.get().strip()
        if not domain:
            messagebox.showerror("Erreur", "Entrez un domaine")
            return
        
        self.result_box.delete(1.0, tk.END)
        self.scan_btn.config(state=tk.DISABLED, text="SCAN DNS...")
        
        def do_scan():
            self.root.after(0, lambda: self.result_box.insert(tk.END, f"Scan DNS de {domain}\n"))
            self.root.after(0, lambda: self.result_box.insert(tk.END, "="*50 + "\n\n"))
            
            types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
            
            for record_type in types:
                self.root.after(0, lambda rt=record_type: self.result_box.insert(tk.END, f"[{record_type} Records]\n"))
                records = self.query_dns(domain, record_type)
                for rec in records:
                    self.root.after(0, lambda r=rec: self.result_box.insert(tk.END, f"  {r}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n"))
            
            # Sous-domaines communs
            self.root.after(0, lambda: self.result_box.insert(tk.END, "[Common Subdomains]\n"))
            subdomains = ['www', 'mail', 'ftp', 'admin', 'blog', 'shop', 'api', 'dev']
            for sub in subdomains:
                try:
                    test = f"{sub}.{domain}"
                    dns.resolver.resolve(test, 'A')
                    self.root.after(0, lambda s=test: self.result_box.insert(tk.END, f"  {s}\n"))
                except:
                    pass
            
            self.root.after(0, lambda: self.result_box.insert(tk.END, "\nScan termine\n"))
            self.scan_btn.config(state=tk.NORMAL, text="SCAN DNS")
            self.status.config(text="Scan DNS termine")
        
        threading.Thread(target=do_scan, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

def main():
    app = DNSScanner()
    app.run()

if __name__ == "__main__":
    main()