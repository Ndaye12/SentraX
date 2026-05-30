#!/usr/bin/env python3
"""Holographic Radar 3D - Visualisation immersive"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import math
from datetime import datetime

class HoloScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Holographic Radar 3D")
        self.root.geometry("900x700")
        self.root.configure(bg="#000000")
        
        self.scanning = False
        self.rotation_angle = 0
        self.rotation_id = None
        self.detected_ports = []
        
        self.setup_ui()
        self.setup_canvas()
    
    def setup_ui(self):
        title = tk.Label(self.root, text="HOLOGRAPHIC RADAR 3D", 
                        font=("Arial", 18, "bold"), fg="#00ffff", bg="#000000")
        title.pack(pady=10)
        
        subtitle = tk.Label(self.root, text="Visualisation temps reel | Detection holographique",
                           font=("Arial", 9), fg="#666666", bg="#000000")
        subtitle.pack()
        
        control_frame = tk.Frame(self.root, bg="#000000")
        control_frame.pack(pady=10)
        
        tk.Label(control_frame, text="Cible:", fg="#00ffff", bg="#000000",
                font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        
        self.target_entry = tk.Entry(control_frame, width=30, bg="#1a1a1a", 
                                      fg="#00ffff", insertbackground="#00ffff",
                                      font=("Arial", 11))
        self.target_entry.pack(side=tk.LEFT, padx=5)
        self.target_entry.insert(0, "scanme.nmap.org")
        
        self.scan_btn = tk.Button(control_frame, text="SCAN", command=self.start_scan,
                                  bg="#00ffff", fg="#000000", font=("Arial", 10, "bold"),
                                  padx=15, cursor="hand2")
        self.scan_btn.pack(side=tk.LEFT, padx=10)
        
        self.clear_btn = tk.Button(control_frame, text="EFFACER", command=self.clear_radar,
                                   bg="#333333", fg="#00ffff", font=("Arial", 10, "bold"),
                                   padx=15, cursor="hand2")
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(self.root, text="PRET", fg="#00ffff", bg="#000000",
                                     font=("Consolas", 10))
        self.status_label.pack()
        
        self.stats_label = tk.Label(self.root, text="Ports detectes: 0", fg="#666666", bg="#000000",
                                    font=("Arial", 9))
        self.stats_label.pack()
    
    def setup_canvas(self):
        self.canvas = tk.Canvas(self.root, width=800, height=500, bg="#000000", 
                                highlightthickness=0)
        self.canvas.pack(pady=20)
        self.draw_radar_base()
    
    def draw_radar_base(self):
        center_x, center_y = 400, 250
        radius = 200
        
        for r in [50, 100, 150, 200]:
            self.canvas.create_oval(center_x - r, center_y - r, 
                                    center_x + r, center_y + r,
                                    outline="#00ffff", width=1, tags="radar")
        
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            self.canvas.create_line(center_x, center_y, x, y, 
                                    fill="#00ffff", width=1, tags="radar")
        
        self.canvas.create_oval(center_x - 5, center_y - 5, 
                                center_x + 5, center_y + 5,
                                fill="#00ffff", tags="radar")
        
        directions = [("N", 0), ("NE", 45), ("E", 90), ("SE", 135), 
                      ("S", 180), ("SW", 225), ("W", 270), ("NW", 315)]
        
        for name, angle in directions:
            rad = math.radians(angle)
            x = center_x + (radius + 20) * math.cos(rad)
            y = center_y + (radius + 20) * math.sin(rad)
            self.canvas.create_text(x, y, text=name, fill="#00ffff", 
                                    font=("Arial", 10, "bold"), tags="radar")
        
        self.canvas.create_text(center_x, center_y - 230, 
                                text="HOLOGRAPHIC RADAR DISPLAY",
                                fill="#00ffff", font=("Arial", 12, "bold"), tags="radar")
        
        self.canvas.create_text(40, 30, text="Port critique", 
                                fill="#ff0000", anchor=tk.W, tags="radar")
        self.canvas.create_text(40, 50, text="Port important", 
                                fill="#ffff00", anchor=tk.W, tags="radar")
        self.canvas.create_text(40, 70, text="Port standard", 
                                fill="#00ff00", anchor=tk.W, tags="radar")
        self.canvas.create_text(40, 90, text="Ligne de scan", 
                                fill="#ff00ff", anchor=tk.W, tags="radar")
    
    def draw_scan_line(self):
        if not self.scanning:
            return
        
        center_x, center_y = 400, 250
        radius = 200
        
        self.canvas.delete("scan_line")
        
        rad = math.radians(self.rotation_angle)
        x = center_x + radius * math.cos(rad)
        y = center_y + radius * math.sin(rad)
        
        self.canvas.create_line(center_x, center_y, x, y, 
                                fill="#ff00ff", width=2, tags="scan_line")
        
        self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4,
                                fill="#ff00ff", outline="#ffffff", tags="scan_line")
        
        self.rotation_angle = (self.rotation_angle + 5) % 360
        
        self.rotation_id = self.root.after(30, self.draw_scan_line)
    
    def add_port_node(self, port, service, color):
        center_x, center_y = 400, 250
        
        angle = (port * 17) % 360
        rad = math.radians(angle)
        distance = 100 + (port % 100)
        
        x = center_x + distance * math.cos(rad)
        y = center_y + distance * math.sin(rad)
        
        for i in range(3):
            self.canvas.create_oval(x - (8 + i*2), y - (8 + i*2), 
                                    x + (8 + i*2), y + (8 + i*2),
                                    outline=color, width=1, 
                                    tags=f"pulse_{port}_{i}")
            self.root.after(200 * i, lambda i=i, p=port: 
                          self.canvas.delete(f"pulse_{p}_{i}"))
        
        self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, 
                                fill=color, outline="#ffffff", 
                                width=2, tags=f"port_{port}")
        
        self.canvas.create_text(x, y - 12, text=str(port), 
                                fill=color, font=("Arial", 8, "bold"),
                                tags=f"label_{port}")
        
        if service and service != "unknown":
            short_service = service[:8] if len(service) > 8 else service
            self.canvas.create_text(x, y + 12, text=short_service, 
                                    fill=color, font=("Arial", 6),
                                    tags=f"service_{port}")
        
        for i in range(5):
            glow = self.canvas.create_oval(x - 12 - i*2, y - 12 - i*2,
                                           x + 12 + i*2, y + 12 + i*2,
                                           outline=color, width=1, 
                                           tags=f"glow_{port}_{i}")
            self.root.after(100 + i*50, lambda g=glow: self.canvas.delete(g))
    
    def animate_ping(self, x, y):
        for r in range(10, 60, 10):
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    outline="#00ffff", width=1,
                                    tags=f"ping_{r}")
            self.root.after(r * 5, lambda r=r: self.canvas.delete(f"ping_{r}"))
    
    def clear_radar(self):
        self.scanning = False
        if self.rotation_id:
            self.root.after_cancel(self.rotation_id)
        
        for item in self.canvas.find_all():
            if "port_" in str(item) or "label_" in str(item) or "service_" in str(item):
                self.canvas.delete(item)
            if "pulse_" in str(item):
                self.canvas.delete(item)
            if "glow_" in str(item):
                self.canvas.delete(item)
        
        self.detected_ports.clear()
        self.stats_label.config(text="Ports detectes: 0")
        self.status_label.config(text="RADAR EFFACE")
        self.draw_radar_base()
    
    def start_scan(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Erreur", "Entrez une cible")
            return
        
        self.clear_radar()
        
        self.status_label.config(text="RESOLUTION DNS...")
        self.scan_btn.config(state=tk.DISABLED, text="SCAN...")
        
        def scan_thread():
            try:
                ip = socket.gethostbyname(target)
                self.root.after(0, lambda: self.status_label.config(
                    text=f"{target} ({ip}) - SCAN EN COURS"))
                
                ports = [22, 80, 443, 8080, 8443, 3306, 3389, 21, 25, 110, 143, 993, 995, 445]
                
                self.scanning = True
                self.rotation_angle = 0
                self.draw_scan_line()
                
                open_ports = []
                total = len(ports)
                
                for i, port in enumerate(ports):
                    if not self.scanning:
                        break
                    
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(3.0)
                        result = sock.connect_ex((ip, port))
                        
                        if result == 0:
                            open_ports.append(port)
                            self.detected_ports.append(port)
                            
                            try:
                                service = socket.getservbyport(port)
                            except:
                                if port == 8080:
                                    service = "http-alt"
                                elif port == 8443:
                                    service = "https-alt"
                                else:
                                    service = "unknown"
                            
                            if port in [21, 22, 23, 3389, 445]:
                                color = "#ff0000"
                            elif port in [80, 443, 8080, 8443]:
                                color = "#ffff00"
                            else:
                                color = "#00ff88"
                            
                            self.root.after(0, lambda p=port, s=service, c=color: 
                                          self.add_port_node(p, s, c))
                            self.root.after(0, lambda: self.animate_ping(400, 250))
                            self.root.after(0, lambda p=port: 
                                          self.status_label.config(text=f"PORT {p} DETECTE - {service}"))
                            self.root.after(0, lambda: self.stats_label.config(
                                          text=f"Ports detectes: {len(self.detected_ports)}"))
                            
                            self.root.after(100)
                        
                        sock.close()
                    except:
                        pass
                    
                    percent = (i + 1) / total * 100
                    self.root.after(0, lambda p=percent: self.status_label.config(
                                  text=f"SCAN... {p:.0f}% - {len(open_ports)} ports trouves"))
                
                self.scanning = False
                self.root.after(0, lambda: self.status_label.config(
                    text=f"SCAN TERMINE - {len(open_ports)} PORTS OUVERTS"))
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="SCAN"))
                self.root.after(0, lambda: self.animate_ping(400, 250))
                
            except Exception as e:
                self.scanning = False
                self.root.after(0, lambda: self.status_label.config(text=f"ERREUR: {str(e)[:40]}"))
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="SCAN"))
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

def main():
    app = HoloScanner()
    app.run()

if __name__ == "__main__":
    main()