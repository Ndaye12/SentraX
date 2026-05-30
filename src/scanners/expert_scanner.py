#!/usr/bin/env python3
"""Expert Scanner - SYN scan + UDP + OS detection + Banner grabbing"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.network import scan_ports_advanced, scan_udp_ports, is_admin, detect_os_advanced, grab_banner_advanced

class ExpertScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Expert Scanner - SENTRAX Pro")
        self.root.geometry("950x750")
        self.root.configure(bg="#0a0a0a")
        
        self.setup_ui()
        self.check_admin()
    
    def check_admin(self):
        if not is_admin():
            self.status_label.config(text="Mode administrateur requis pour SYN scan - Utilisation TCP scan", fg="#ffaa00")
    
    def setup_ui(self):
        title = tk.Label(self.root, text="EXPERT SCANNER PRO", 
                        font=("Arial", 22, "bold"), fg="#ff4444", bg="#0a0a0a")
        title.pack(pady=15)
        
        subtitle = tk.Label(self.root, text="SYN Scan | UDP Scan | OS Detection | Banner Grabbing | Multi-threading",
                           font=("Arial", 10), fg="#666666", bg="#0a0a0a")
        subtitle.pack()
        
        main_frame = tk.Frame(self.root, bg="#0a0a0a")
        main_frame.pack(pady=20, padx=20, fill=tk.X)
        
        tk.Label(main_frame, text="Cible:", fg="white", bg="#0a0a0a", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.target_entry = tk.Entry(main_frame, width=40, font=("Arial", 11), bg="#1a1a1a", fg="#ff4444")
        self.target_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=3, sticky=tk.W)
        self.target_entry.insert(0, "scanme.nmap.org")
        
        tk.Label(main_frame, text="Scan TCP:", fg="white", bg="#0a0a0a", font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.scan_type = tk.StringVar(value="tcp")
        tk.Radiobutton(main_frame, text="SYN Scan (furtif)", variable=self.scan_type, value="syn", bg="#0a0a0a", fg="#00ff88", selectcolor="#0a0a0a").grid(row=1, column=1, sticky=tk.W)
        tk.Radiobutton(main_frame, text="TCP Scan (standard)", variable=self.scan_type, value="tcp", bg="#0a0a0a", fg="#00ff88", selectcolor="#0a0a0a").grid(row=1, column=2, sticky=tk.W)
        
        self.udp_var = tk.BooleanVar()
        tk.Checkbutton(main_frame, text="Scan UDP (lent - recommande uniquement pour petits ranges)", variable=self.udp_var, bg="#0a0a0a", fg="#ffaa00", selectcolor="#0a0a0a").grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky=tk.W)
        
        tk.Label(main_frame, text="Ports:", fg="white", bg="#0a0a0a", font=("Arial", 11)).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_port = tk.Entry(main_frame, width=6, font=("Arial", 11), bg="#1a1a1a", fg="#ff4444")
        self.start_port.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.start_port.insert(0, "1")
        tk.Label(main_frame, text="-", fg="white", bg="#0a0a0a", font=("Arial", 11)).grid(row=3, column=2)
        self.end_port = tk.Entry(main_frame, width=6, font=("Arial", 11), bg="#1a1a1a", fg="#ff4444")
        self.end_port.grid(row=3, column=3, padx=5, pady=5, sticky=tk.W)
        self.end_port.insert(0, "1000")
        
        tk.Label(main_frame, text="Threads:", fg="white", bg="#0a0a0a", font=("Arial", 11)).grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.threads_entry = tk.Entry(main_frame, width=6, font=("Arial", 11), bg="#1a1a1a", fg="#ff4444")
        self.threads_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        self.threads_entry.insert(0, "100")
        tk.Label(main_frame, text="(100-200 recommande)", fg="#666666", bg="#0a0a0a", font=("Arial", 9)).grid(row=4, column=2, columnspan=2, sticky=tk.W)
        
        self.scan_btn = tk.Button(self.root, text="LANCER LE SCAN EXPERT", command=self.scan,
                                  bg="#ff4444", fg="#ffffff", font=("Arial", 12, "bold"), 
                                  padx=40, pady=12, cursor="hand2")
        self.scan_btn.pack(pady=20)
        
        self.result_box = tk.Text(self.root, bg="#1a1a1a", fg="#ff4444", font=("Consolas", 10), wrap=tk.WORD)
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(self.result_box)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_box.yview)
        
        self.status_label = tk.Label(self.root, text="Pret - Mode TCP actif", fg="#666666", bg="#0a0a0a", font=("Arial", 9))
        self.status_label.pack(pady=5)
    
    def scan(self):
        target = self.target_entry.get().strip()
        try:
            start = int(self.start_port.get())
            end = int(self.end_port.get())
            threads = int(self.threads_entry.get())
            if start < 1 or end > 65535 or start > end:
                raise ValueError
        except:
            messagebox.showerror("Erreur", "Ports invalides (1-65535)")
            return
        
        if not target:
            messagebox.showerror("Erreur", "Entrez une cible")
            return
        
        self.result_box.delete(1.0, tk.END)
        self.scan_btn.config(state=tk.DISABLED, text="SCAN EN COURS...")
        self.status_label.config(text=f"Scan de {target}...")
        
        def do_scan():
            try:
                ip = socket.gethostbyname(target)
                ports = list(range(start, end + 1))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*70 + "\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "EXPERT SCAN - SENTRAX PRO\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*70 + "\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Cible: {target} ({ip})\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Ports: {start}-{end} ({len(ports)} ports)\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Threads: {threads}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Mode TCP: {self.scan_type.get().upper()}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Mode UDP: {'ACTIF' if self.udp_var.get() else 'INACTIF'}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*70 + "\n\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "[SCAN TCP EN COURS]\n"))
                results_tcp = scan_ports_advanced(ip, ports, self.scan_type.get(), 1, threads)
                
                for r in results_tcp:
                    self.root.after(0, lambda p=r['port'], s=r['service'], m=r['method']: 
                                  self.result_box.insert(tk.END, f"  TCP Port {p}: {s} | {m}\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"\nTCP: {len(results_tcp)} ports ouverts\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n[DETECTION OS]\n"))
                os_info = detect_os_advanced(ip)
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"  OS estime: {os_info['guess']}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"  TTL: {os_info['ttl']}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"  Window: {os_info['window']}\n"))
                
                if results_tcp:
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "\n[BANNER GRABBING]\n"))
                    for r in results_tcp[:5]:
                        banner_info = grab_banner_advanced(ip, r['port'])
                        if banner_info['banner']:
                            self.root.after(0, lambda p=r['port'], b=banner_info['banner'][:80]: 
                                          self.result_box.insert(tk.END, f"  Port {p}: {b}\n"))
                            if banner_info.get('version'):
                                self.root.after(0, lambda p=r['port'], v=banner_info['version']: 
                                              self.result_box.insert(tk.END, f"    Version: {v}\n"))
                
                if self.udp_var.get():
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "\n[SCAN UDP EN COURS]\n"))
                    self.root.after(0, lambda: self.result_box.insert(tk.END, " Le scan UDP peut prendre plusieurs minutes...\n"))
                    
                    udp_ports = [53, 67, 68, 123, 137, 138, 161, 162, 500, 514, 520, 631]
                    results_udp = scan_udp_ports(ip, udp_ports, 2, 20)
                    
                    for r in results_udp:
                        self.root.after(0, lambda p=r['port'], s=r['service']: 
                                      self.result_box.insert(tk.END, f"  UDP Port {p}: {s}\n"))
                    
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"\nUDP: {len(results_udp)} ports ouverts\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "\n" + "="*70 + "\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "RESUME FINAL\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"  Ports TCP ouverts: {len(results_tcp)}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"  OS detecte: {os_info['guess']}\n"))
                if self.udp_var.get():
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"  Ports UDP ouverts: {len(results_udp)}\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*70 + "\n"))
                
                self.status_label.config(text=f"Scan termine - {len(results_tcp)} ports TCP | OS: {os_info['guess'][:30]}")
                
            except Exception as e:
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Erreur: {str(e)}\n"))
                self.status_label.config(text="Erreur")
            finally:
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="LANCER LE SCAN EXPERT"))
        
        threading.Thread(target=do_scan, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

def main():
    app = ExpertScanner()
    app.run()

if __name__ == "__main__":
    main()