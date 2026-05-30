#!/usr/bin/env python3
"""Ultra Scanner Pro - Version ultra-avancee"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.network import (
    scan_ports_advanced, scan_udp_advanced, icmp_ping_advanced, 
    discover_network_advanced, detect_service_version
)

class UltraScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ultra Scanner Pro - SENTRAX")
        self.root.geometry("1050x800")
        self.root.configure(bg="#0a0a0a")
        self.setup_ui()
    
    def setup_ui(self):
        # Titre
        title = tk.Label(self.root, text="ULTRA SCANNER PRO", 
                        font=("Arial", 24, "bold"), fg="#ff00ff", bg="#0a0a0a")
        title.pack(pady=15)
        
        subtitle = tk.Label(self.root, text="UDP + ICMP + Version Detection + CVE Correlation",
                           font=("Arial", 10), fg="#666666", bg="#0a0a0a")
        subtitle.pack()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#0a0a0a")
        main_frame.pack(pady=20, padx=20, fill=tk.X)
        
        # Ligne 1: Cible
        tk.Label(main_frame, text="Target:", fg="white", bg="#0a0a0a", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.target_entry = tk.Entry(main_frame, width=40, font=("Arial", 11), bg="#1a1a1a", fg="#ff00ff")
        self.target_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=3, sticky=tk.W)
        self.target_entry.insert(0, "scanme.nmap.org")
        
        # Ligne 2: Options
        tk.Label(main_frame, text="Scan type:", fg="white", bg="#0a0a0a", font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.tcp_var = tk.BooleanVar(value=True)
        self.udp_var = tk.BooleanVar(value=False)
        self.icmp_var = tk.BooleanVar(value=False)
        
        tk.Checkbutton(main_frame, text="TCP Scan", variable=self.tcp_var, bg="#0a0a0a", fg="#00ff88", selectcolor="#0a0a0a").grid(row=1, column=1, sticky=tk.W)
        tk.Checkbutton(main_frame, text="UDP Scan", variable=self.udp_var, bg="#0a0a0a", fg="#ffaa00", selectcolor="#0a0a0a").grid(row=1, column=2, sticky=tk.W)
        tk.Checkbutton(main_frame, text="ICMP Ping", variable=self.icmp_var, bg="#0a0a0a", fg="#00ffff", selectcolor="#0a0a0a").grid(row=1, column=3, sticky=tk.W)
        
        # Ligne 3: Version detection
        self.version_var = tk.BooleanVar(value=True)
        tk.Checkbutton(main_frame, text="Version detection (banner grabbing)", variable=self.version_var, bg="#0a0a0a", fg="#ff6600", selectcolor="#0a0a0a").grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky=tk.W)
        
        # Ligne 4: Port range
        tk.Label(main_frame, text="Ports:", fg="white", bg="#0a0a0a", font=("Arial", 11)).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_port = tk.Entry(main_frame, width=6, font=("Arial", 11), bg="#1a1a1a", fg="#ff00ff")
        self.start_port.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.start_port.insert(0, "1")
        tk.Label(main_frame, text="-", fg="white", bg="#0a0a0a", font=("Arial", 11)).grid(row=3, column=2)
        self.end_port = tk.Entry(main_frame, width=6, font=("Arial", 11), bg="#1a1a1a", fg="#ff00ff")
        self.end_port.grid(row=3, column=3, padx=5, pady=5, sticky=tk.W)
        self.end_port.insert(0, "1000")
        
        # Ligne 5: Network discovery
        tk.Label(main_frame, text="Network:", fg="white", bg="#0a0a0a", font=("Arial", 11)).grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.network_entry = tk.Entry(main_frame, width=30, font=("Arial", 11), bg="#1a1a1a", fg="#ff00ff")
        self.network_entry.grid(row=4, column=1, padx=5, pady=5, columnspan=2, sticky=tk.W)
        self.network_entry.insert(0, "192.168.1.0/24")
        self.discover_btn = tk.Button(main_frame, text="Discover Network", command=self.discover_network,
                                      bg="#00ffff", fg="#000000", font=("Arial", 9, "bold"))
        self.discover_btn.grid(row=4, column=3, padx=5, pady=5)
        
        # Bouton principal
        self.scan_btn = tk.Button(self.root, text="LAUNCH ULTRA SCAN", command=self.scan,
                                  bg="#ff00ff", fg="#ffffff", font=("Arial", 14, "bold"), 
                                  padx=50, pady=15, cursor="hand2")
        self.scan_btn.pack(pady=20)
        
        # Resultats
        self.result_box = tk.Text(self.root, bg="#1a1a1a", fg="#ff00ff", font=("Consolas", 10), wrap=tk.WORD)
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(self.result_box)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_box.yview)
        
        self.status_label = tk.Label(self.root, text="Ready", fg="#666666", bg="#0a0a0a", font=("Arial", 9))
        self.status_label.pack(pady=5)
    
    def discover_network(self):
        network = self.network_entry.get().strip()
        if not network:
            messagebox.showerror("Error", "Enter network CIDR (ex: 192.168.1.0/24)")
            return
        
        self.result_box.delete(1.0, tk.END)
        self.discover_btn.config(state=tk.DISABLED, text="Scanning...")
        
        def do_discover():
            self.root.after(0, lambda: self.result_box.insert(tk.END, f"Discovering network: {network}\n"))
            self.root.after(0, lambda: self.result_box.insert(tk.END, "="*60 + "\n\n"))
            
            hosts = discover_network_advanced(network)
            
            for host in hosts:
                self.root.after(0, lambda h=host: self.result_box.insert(tk.END, f"  [ALIVE] {h['ip']} ({h['response_time']}ms)\n"))
            
            self.root.after(0, lambda: self.result_box.insert(tk.END, f"\nFound {len(hosts)} active hosts\n"))
            self.discover_btn.config(state=tk.NORMAL, text="Discover Network")
        
        threading.Thread(target=do_discover, daemon=True).start()
    
    def scan(self):
        target = self.target_entry.get().strip()
        try:
            start = int(self.start_port.get())
            end = int(self.end_port.get())
            if start < 1 or end > 65535 or start > end:
                raise ValueError
        except:
            messagebox.showerror("Error", "Invalid ports (1-65535)")
            return
        
        if not target:
            messagebox.showerror("Error", "Enter a target")
            return
        
        self.result_box.delete(1.0, tk.END)
        self.scan_btn.config(state=tk.DISABLED, text="SCANNING...")
        
        def do_scan():
            try:
                ip = socket.gethostbyname(target)
                ports = list(range(start, end + 1))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*70 + "\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "ULTRA SCAN PRO - SENTRAX\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*70 + "\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Target: {target} ({ip})\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Ports: {start}-{end} ({len(ports)} ports)\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*70 + "\n\n"))
                
                # ICMP Ping
                if self.icmp_var.get():
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "[ICMP PING]\n"))
                    ping_result = icmp_ping_advanced(ip)
                    if ping_result['alive']:
                        self.root.after(0, lambda: self.result_box.insert(tk.END, f"  Host is alive ({ping_result['response_time']}ms)\n\n"))
                    else:
                        self.root.after(0, lambda: self.result_box.insert(tk.END, "  Host is down or not responding\n\n"))
                
                # TCP Scan
                if self.tcp_var.get():
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "[TCP SCAN]\n"))
                    results_tcp = scan_ports_advanced(ip, ports, "tcp", 1, 100)
                    
                    for r in results_tcp:
                        self.root.after(0, lambda p=r['port'], s=r['service']: 
                                      self.result_box.insert(tk.END, f"  TCP Port {p}: {s} [OPEN]\n"))
                        
                        # Version detection
                        if self.version_var.get():
                            version_info = detect_service_version(ip, r['port'], r['service'])
                            if version_info.get('version'):
                                self.root.after(0, lambda v=version_info['version']: 
                                              self.result_box.insert(tk.END, f"    Version: {v}\n"))
                            if version_info.get('os'):
                                self.root.after(0, lambda o=version_info['os']: 
                                              self.result_box.insert(tk.END, f"    OS: {o}\n"))
                    
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"\nTCP: {len(results_tcp)} ports open\n\n"))
                
                # UDP Scan
                if self.udp_var.get():
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "[UDP SCAN]\n"))
                    self.root.after(0, lambda: self.result_box.insert(tk.END, "  Scanning UDP ports (may take time)...\n"))
                    
                    udp_ports = [53, 67, 68, 123, 137, 138, 161, 162, 500, 514, 520, 631, 1900, 5353]
                    results_udp = scan_udp_advanced(ip, udp_ports, 2, 20)
                    
                    for r in results_udp:
                        self.root.after(0, lambda p=r['port'], s=r['service']: 
                                      self.root.after(0, lambda: self.result_box.insert(tk.END, f"  UDP Port {p}: {s} [OPEN]\n")))
                        if r.get('banner'):
                            self.root.after(0, lambda b=r['banner'][:80]: 
                                          self.root.after(0, lambda: self.result_box.insert(tk.END, f"    Banner: {b}\n")))
                    
                    self.root.after(0, lambda: self.result_box.insert(tk.END, f"\nUDP: {len(results_udp)} ports open\n\n"))
                
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*70 + "\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "SCAN COMPLETE\n"))
                self.root.after(0, lambda: self.result_box.insert(tk.END, "="*70 + "\n"))
                
                self.status_label.config(text="Scan complete")
                
            except Exception as e:
                self.root.after(0, lambda: self.result_box.insert(tk.END, f"Error: {str(e)}\n"))
                self.status_label.config(text="Error")
            finally:
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="LAUNCH ULTRA SCAN"))
        
        threading.Thread(target=do_scan, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

def main():
    app = UltraScanner()
    app.run()

if __name__ == "__main__":
    main()