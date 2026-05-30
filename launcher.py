#!/usr/bin/env python3
"""
SENTRAX - Launcher principal
Developpe par Patrick Ndaye
Interface unifiee pour les 10 scanners
Version 3.1.0 - Professionnelle FINALE
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import platform
from pathlib import Path
import os
import webbrowser
import threading
import time

class SentraXLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SENTRAX - Cybersecurity Scanner")
        self.root.geometry("1000x800")
        self.root.configure(bg="#0a0a0a")
        
        self.show_legal_disclaimer()
        self.center_window()
        self.setup_ui()
    
    def show_legal_disclaimer(self):
        """Affiche l'avertissement legal au premier lancement"""
        config_dir = Path.home() / ".sentrax"
        config_dir.mkdir(exist_ok=True)
        flag_file = config_dir / "disclaimer_accepted.txt"
        
        if not flag_file.exists():
            response = messagebox.askyesno(
                "LEGAL WARNING",
                "SENTRAX - CYBERSECURITY TOOL\n\n"
                "AUTHORIZED USE:\n"
                "   - Authorized penetration testing (with written contract)\n"
                "   - Internal security audits\n"
                "   - Training and education\n"
                "   - Your own infrastructure\n\n"
                "PROHIBITED USE:\n"
                "   - Scanning without authorization\n"
                "   - Malicious activities\n\n"
                "User is SOLELY RESPONSIBLE for the use.\n\n"
                "Do you accept these conditions?"
            )
            
            if response:
                with open(flag_file, 'w') as f:
                    f.write("accepted")
            else:
                sys.exit(0)
    
    def show_privacy_policy(self):
        privacy_text = """
PRIVACY POLICY - SENTRAX

1. DATA COLLECTED
   SENTRAX does NOT collect any personal data.
   No information is sent over the Internet.

2. LOCAL DATA
   The software only stores:
   - Disclaimer acceptance file
   - Scan history (scan_history.db) - ONLY for Time Machine Scanner
   
   These files stay on your machine.

3. EXTERNAL APIS (OPTIONAL)
   If you configure API keys (Shodan, Censys):
   - Requests are sent directly to these services
   - No data goes through our servers

4. NO TRACKING
   - No cookies
   - No statistics
   - No telemetry

5. YOUR RIGHTS
   You can at any time:
   - Delete config files in %USERPROFILE%\\.sentrax\\
   - Delete scan history (scan_history.db)

6. CONTACT
   For any questions: patrickndaye919@gmail.com

========================================
2026 Patrick Ndaye - SENTRAX
"""
        messagebox.showinfo("Privacy Policy", privacy_text)
    
    def show_terms_of_use(self):
        terms_text = """
TERMS OF USE - SENTRAX

1. AUTHORIZED USE
   - Authorized penetration testing (with written contract)
   - Internal security audits of your own infrastructure
   - Cybersecurity training and education
   - Vulnerability detection on your own servers
   - Personal or professional local network analysis

2. PROHIBITED USE
   - Scanning systems without prior written authorization
   - Use for hacking, extortion, or malicious activities
   - Denial of Service (DoS/DDoS) attacks
   - Exploitation of found vulnerabilities without permission
   - Scanning without permission
   - Use against critical infrastructure

3. LIABILITY
   The user is SOLELY RESPONSIBLE for the use of this software.
   The author disclaims any liability for illegal or unauthorized use.

========================================
2026 Patrick Ndaye - SENTRAX
"""
        messagebox.showinfo("Terms of Use", terms_text)
    
    def show_about(self):
        about_text = """
SENTRAX - Cybersecurity Scanner
Version 3.1.0

Developed by Patrick Ndaye

10 scanners included:
- AI Predictive Scanner
- OSINT Scanner
- P2P Scanner
- Passive Scanner
- Time Machine Scanner
- Holographic Radar 3D
- Expert Scanner PRO
- Ultra Scanner PRO
- SNMP Scanner
- DNS Scanner

Contact: patrickndaye919@gmail.com

Open Source | Professional Use
2026 Patrick Ndaye
"""
        messagebox.showinfo("About SENTRAX", about_text)
    
    def launch_dashboard(self):
        """Lance Flask directement dans un thread"""
        
        self.status_label.config(text="🚀 Démarrage du serveur...")
        
        def run_flask():
            try:
                import sys
                import os
                
                if getattr(sys, 'frozen', False):
                    base_path = sys._MEIPASS
                else:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                
                if base_path not in sys.path:
                    sys.path.insert(0, base_path)
                
                from web.api import app, setup_flask_port
                
                port = setup_flask_port()
                
                self.root.after(0, lambda: self.status_label.config(text=f"✅ Serveur sur port {port}"))
                
                time.sleep(1.5)
                webbrowser.open(f"http://127.0.0.1:{port}/dashboard")
                
                app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)
                
            except Exception as e:
                print(f"Erreur Flask: {e}")
                self.root.after(0, lambda err=e: self.status_label.config(text=f"❌ Erreur: {err}"))
        
        threading.Thread(target=run_flask, daemon=True).start()
    
    def center_window(self):
        self.root.update_idletasks()
        width = 1000
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        menubar = tk.Menu(self.root, bg="#0a0a0a", fg="#00ff88")
        
        file_menu = tk.Menu(menubar, tearoff=0, bg="#1a1a1a", fg="#00ff88")
        file_menu.add_command(label="Privacy Policy", command=self.show_privacy_policy)
        file_menu.add_command(label="Terms of Use", command=self.show_terms_of_use)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg="#1a1a1a", fg="#00ff88")
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Dashboard", command=self.launch_dashboard)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        header_frame = tk.Frame(self.root, bg="#0a0a0a")
        header_frame.pack(fill=tk.X, pady=15)
        
        title = tk.Label(header_frame, text="SENTRAX", 
                        font=("Arial", 32, "bold"), fg="#00ff88", bg="#0a0a0a")
        title.pack()
        
        subtitle = tk.Label(header_frame, text="Cybersecurity Scanner | 10 professional tools",
                           font=("Arial", 10), fg="#666666", bg="#0a0a0a")
        subtitle.pack(pady=5)
        
        separator = tk.Frame(self.root, height=2, bg="#1a1a1a")
        separator.pack(fill=tk.X, padx=40, pady=8)
        
        canvas_frame = tk.Frame(self.root, bg="#0a0a0a")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg="#0a0a0a", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0a0a0a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        
        self.status_label = tk.Label(self.root, text="✅ Prêt", fg="#00ff88", bg="#0a0a0a", font=("Arial", 9))
        self.status_label.pack(pady=5)
        
        self.port_label = tk.Label(self.root, text="", fg="#00aaff", bg="#0a0a0a", font=("Arial", 8))
        self.port_label.pack(pady=2)
        
        tools = [
            ("🤖 AI PREDICTIVE", "AI Scan\n10x faster", "ai_scanner", "#00ff88"),
            ("🌐 OSINT", "Shodan + Censys\nDNS + GitHub", "osint_scanner", "#00aaff"),
            ("🤝 P2P", "Distributed scan\nWorldwide", "p2p_scanner", "#ffaa00"),
            ("👻 PASSIVE", "Zero packet sent\nUndetectable", "passive_scanner", "#ff00ff"),
            ("⏰ TIME MACHINE", "History analysis\nPredictions", "timemachine_scanner", "#ff6600"),
            ("🕶️ HOLO RADAR", "3D visualization\nReal time", "holo_scanner", "#00ffff"),
            ("👑 EXPERT PRO", "SYN + UDP\n65535 ports", "expert_scanner", "#ff4444"),
            ("🔥 ULTRA PRO", "UDP + ICMP\nVersion Detection", "ultra_scanner", "#ff6600"),
            ("🔌 SNMP", "SNMP detection\nCommunity strings", "snmp_scanner", "#ff8800"),
            ("📡 DNS", "DNS enumeration\nZone transfer", "dns_scanner", "#ff44cc"),
        ]
        
        for i, (name, desc, module, color) in enumerate(tools):
            row = i // 2
            col = i % 2
            self.create_tool_card(scrollable_frame, name, desc, module, color, row, col)
        
        footer = tk.Label(self.root, text="SENTRAX v3.1 | Developed by Patrick Ndaye | Contact: patrickndaye919@gmail.com | 10 scanners | Open Source",
                         font=("Arial", 8), fg="#444444", bg="#0a0a0a")
        footer.pack(pady=8)
    
    def create_tool_card(self, parent, name, desc, module, color, row, col):
        card = tk.Frame(parent, bg="#1a1a1a", relief=tk.RAISED, bd=1, width=420, height=130)
        card.grid(row=row, column=col, padx=10, pady=8, sticky="nsew")
        card.grid_propagate(False)
        
        inner = tk.Frame(card, bg="#1a1a1a")
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        title = tk.Label(inner, text=name, font=("Arial", 12, "bold"),
                        fg=color, bg="#1a1a1a")
        title.pack(anchor=tk.W)
        
        description = tk.Label(inner, text=desc, font=("Arial", 9),
                              fg="#888888", bg="#1a1a1a", justify=tk.LEFT)
        description.pack(anchor=tk.W, pady=(5,8))
        
        btn = tk.Button(inner, text="LAUNCH", 
                       command=lambda m=module: self.launch_tool(m),
                       bg=color, fg="#000000", font=("Arial", 9, "bold"),
                       padx=20, pady=4, cursor="hand2")
        btn.pack(anchor=tk.E)
        
        def on_enter(e): btn.configure(bg="#ffffff")
        def on_leave(e): btn.configure(bg=color)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    def launch_tool(self, module_name):
        """Lance un scanner avec gestion des chemins EXE"""
        import importlib
        import threading
        import sys
        import os

        try:
            # Ajouter le chemin correct pour l'EXE
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            if base_path not in sys.path:
                sys.path.insert(0, base_path)
            
            # Importer le module
            module = importlib.import_module(f"src.scanners.{module_name}")

            if hasattr(module, "main"):
                thread = threading.Thread(target=module.main, daemon=True)
                thread.start()
            else:
                messagebox.showerror("Erreur", f"{module_name} n'a pas de fonction main()")

        except ImportError as e:
            messagebox.showerror("Erreur d'import", 
                f"Module manquant pour {module_name}\n\n{str(e)}\n\n"
                "Vérifiez les dépendances: pip install dnspython shodan censys")
        except Exception as e:
            messagebox.showerror("Erreur", f"Cannot launch {module_name}\n\n{str(e)}")

if __name__ == "__main__":
    app = SentraXLauncher()
    app.root.mainloop()