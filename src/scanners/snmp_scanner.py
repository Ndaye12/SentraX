#!/usr/bin/env python3
"""SNMP Scanner - Detection de peripheriques reseau"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import struct
from datetime import datetime

class SNMPScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SNMP Scanner")
        self.root.geometry("800x600")
        self.root.configure(bg="#0a0a0a")
        self.setup_ui()
    
    def setup_ui(self):
        title = tk.Label(self.root, text="SNMP SCANNER", 
                        font=("Arial", 20, "bold"), fg="#ff8800", bg="#0a0a0a")
        title.pack(pady=20)
        
        subtitle = tk.Label(self.root, text="Detection de peripheriques SNMP | Community strings",
                           font=("Arial", 10), fg="#666666", bg="#0a0a0a")
        subtitle.pack()
        
        frame = tk.Frame(self.root, bg="#0a0a0a")
        frame.pack(pady=20)
        
        tk.Label(frame, text="Cible:", fg="white", bg="#0a0a0a", 
                font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        self.target_entry = tk.Entry(frame, width=35, font=("Arial", 12), 
                                      bg="#1a1a1a", fg="#ff8800")
        self.target_entry.pack(side=tk.LEFT, padx=5)
        self.target_entry.insert(0, "192.168.1.1")
        
        self.scan_btn = tk.Button(self.root, text="SCAN SNMP", command=self.scan,
                                  bg="#ff8800", fg="#000000", font=("Arial", 12, "bold"), 
                                  padx=30, pady=10)
        self.scan_btn.pack(pady=20)
        
        self.result_box = tk.Text(self.root, bg="#1a1a1a", fg="#ff8800", 
                                  font=("Consolas", 10), wrap=tk.WORD)
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.status = tk.Label(self.root, text="Pret", fg="#666666", bg="#0a0a0a")
        self.status.pack(pady=5)
    
    def snmp_get(self, ip, community='public', oid='1.3.6.1.2.1.1.1.0'):
        """Requete SNMP simple"""
        # Simulation (en vrai, utiliser pysnmp)
        return f"SNMP response from {ip}"
    
    def scan(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Erreur", "Entrez une cible")
            return
        
        self.result_box.delete(1.0, tk.END)
        self.scan_btn.config(state=tk.DISABLED, text="SCAN SNMP...")
        
        def do_scan():
            self.root.after(0, lambda: self.result_box.insert(tk.END, f"Scan SNMP de {target}\n"))
            self.root.after(0, lambda: self.result_box.insert(tk.END, "="*50 + "\n\n"))
            
            communities = ['public', 'private', 'public2', 'admin', 'snmp']
            
            for community in communities:
                self.root.after(0, lambda c=community: self.result_box.insert(tk.END, f"Test community: {c}... "))
                result = self.snmp_get(target, community)
                self.root.after(0, lambda: self.result_box.insert(tk.END, "OK (simule)\n"))
            
            self.root.after(0, lambda: self.result_box.insert(tk.END, "\nScan termine\n"))
            self.scan_btn.config(state=tk.NORMAL, text="SCAN SNMP")
            self.status.config(text="Scan SNMP termine")
        
        threading.Thread(target=do_scan, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

def main():
    app = SNMPScanner()
    app.run()

if __name__ == "__main__":
    main()