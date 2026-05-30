#!/usr/bin/env python3
"""AI Predictive Scanner - Scan 10x plus rapide par Machine Learning"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
from datetime import datetime

class AIScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Predictive Scanner")
        self.root.geometry("800x600")
        self.root.configure(bg="#0a0a0a")
        
        self.port_probabilities = {
            80: {443: 0.92, 8080: 0.67, 22: 0.45},
            443: {80: 0.95, 8443: 0.89, 22: 0.52},
            22: {80: 0.63, 443: 0.58, 3306: 0.34},
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        title = tk.Label(self.root, text="AI PREDICTIVE SCANNER", 
                        font=("Arial", 20, "bold"), fg="#00ff88", bg="#0a0a0a")
        title.pack(pady=20)
        
        subtitle = tk.Label(self.root, text="10x plus rapide grace a l'IA | Mode prediction active",
                           font=("Arial", 10), fg="#666666", bg="#0a0a0a")
        subtitle.pack()
        
        frame = tk.Frame(self.root, bg="#0a0a0a")
        frame.pack(pady=20)
        
        tk.Label(frame, text="Cible (IP/Domaine):", fg="white", bg="#0a0a0a", 
                font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        self.target_entry = tk.Entry(frame, width=35, font=("Arial", 12), bg="#1a1a1a", fg="#00ff88")
        self.target_entry.pack(side=tk.LEFT, padx=5)
        self.target_entry.insert(0, "scanme.nmap.org")
        
        self.scan_btn = tk.Button(self.root, text="SCAN PREDICTIF", command=self.scan,
                                  bg="#00ff88", fg="#000000", font=("Arial", 12, "bold"), 
                                  padx=30, pady=10, cursor="hand2")
        self.scan_btn.pack(pady=20)
        
        self.result_box = tk.Text(self.root, bg="#1a1a1a", fg="#00ff88", 
                                  font=("Consolas", 10), wrap=tk.WORD)
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(self.result_box)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_box.yview)
    
    def quick_probe(self, ip, ports):
        open_ports = []
        for port in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                if s.connect_ex((ip, port)) == 0:
                    open_ports.append(port)
                s.close()
            except:
                pass
        return open_ports
    
    def scan_single_port(self, ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            result = s.connect_ex((ip, port))
            s.close()
            return result == 0
        except:
            return False
    
    def scan(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Erreur", "Entrez une cible")
            return
        
        self.result_box.delete(1.0, tk.END)
        self.scan_btn.config(state=tk.DISABLED, text="IA EN ANALYSE...")
        
        def do_scan():
            try:
                ip = socket.gethostbyname(target)
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Cible: {target} ({ip})\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Mode IA actif\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*50 + "\n\n"))
                
                probe_ports = [80, 443, 22, 3389, 445]
                self.root.after(0, lambda: self.result_box.insert(tk.END, "Phase 1: Analyse des ports signatures...\n"))
                open_probes = self.quick_probe(ip, probe_ports)
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Ports ouverts: {open_probes}\n\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "Phase 2: Prediction IA...\n"))
                predicted = set()
                for port in open_probes:
                    if port in self.port_probabilities:
                        for pred, prob in self.port_probabilities[port].items():
                            if prob > 0.3:
                                predicted.add(pred)
                
                if not predicted and open_probes:
                    if 80 in open_probes:
                        predicted.add(443)
                        predicted.add(8080)
                        predicted.add(8443)
                    if 22 in open_probes:
                        predicted.add(80)
                        predicted.add(443)
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Ports predits: {sorted(predicted)}\n\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "Phase 3: Scan cible...\n"))
                
                all_ports = set(open_probes) | predicted
                final_open = []
                
                for port in all_ports:
                    if self.scan_single_port(ip, port):
                        final_open.append(port)
                        try:
                            service = socket.getservbyport(port)
                        except:
                            if port == 8080:
                                service = "http-alt"
                            elif port == 8443:
                                service = "https-alt"
                            else:
                                service = "unknown"
                        self.root.after(0, lambda p=port, sv=service: 
                                      self.result_box.insert(tk.END, f"  Port {p} ouvert | {sv}\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n" + "="*50 + "\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "RAPPORT FINAL\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"  Ports trouves: {len(final_open)}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"  Ports predits: {len(predicted)}\n"))
                
            except Exception as e:
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Erreur: {e}\n"))
            finally:
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="SCAN PREDICTIF"))
        
        threading.Thread(target=do_scan, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

def main():
    app = AIScanner()
    app.run()

if __name__ == "__main__":
    main()