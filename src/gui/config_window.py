#!/usr/bin/env python3
"""Fenetre principale alternative pour SENTRAX AI Suite"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from pathlib import Path

class SENTRAXMainWindow:
    """Fenetre principale avec barre de menu et options avancees"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SENTRAX AI Suite - Cybersecurity Platform")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0a0a0a")
        self.root.minsize(800, 600)
        
        self.center_window()
        self.setup_menu()
        self.setup_ui()
    
    def center_window(self):
        """Centre la fenetre sur l'ecran"""
        self.root.update_idletasks()
        width = 1000
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_menu(self):
        """Configure la barre de menu"""
        
        menubar = tk.Menu(self.root, bg="#1a1a1a", fg="#00ff88")
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0, bg="#1a1a1a", fg="#00ff88")
        file_menu.add_command(label="📁 Exporter les resultats", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0, bg="#1a1a1a", fg="#00ff88")
        tools_menu.add_command(label="🔧 Configuration des APIs", command=self.open_api_config)
        tools_menu.add_separator()
        tools_menu.add_command(label="📊 Scanner IA", command=lambda: self.launch_scanner("ai_scanner"))
        tools_menu.add_command(label="🌐 Scanner OSINT", command=lambda: self.launch_scanner("osint_scanner"))
        tools_menu.add_command(label="🤝 Scanner P2P", command=lambda: self.launch_scanner("p2p_scanner"))
        tools_menu.add_command(label="👻 Scanner Passif", command=lambda: self.launch_scanner("passive_scanner"))
        tools_menu.add_command(label="⏰ Scanner Time Machine", command=lambda: self.launch_scanner("timemachine_scanner"))
        tools_menu.add_command(label="🕶️ Scanner Holographique", command=lambda: self.launch_scanner("holo_scanner"))
        menubar.add_cascade(label="Outils", menu=tools_menu)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0, bg="#1a1a1a", fg="#00ff88")
        help_menu.add_command(label="📖 Documentation", command=self.show_docs)
        help_menu.add_command(label="ℹ️ A propos", command=self.show_about)
        menubar.add_cascade(label="Aide", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def setup_ui(self):
        """Configure l'interface principale"""
        
        # Header
        header_frame = tk.Frame(self.root, bg="#0a0a0a")
        header_frame.pack(fill=tk.X, pady=20)
        
        title = tk.Label(header_frame, text="SENTRAX AI SUITE", 
                        font=("Arial", 32, "bold"), fg="#00ff88", bg="#0a0a0a")
        title.pack()
        
        subtitle = tk.Label(header_frame, 
                           text="Platforme de cybersecurite nouvelle generation | 6 scanners integres",
                           font=("Arial", 11), fg="#666666", bg="#0a0a0a")
        subtitle.pack(pady=5)
        
        # Stats
        stats_frame = tk.Frame(self.root, bg="#1a1a1a", relief=tk.RIDGE, bd=1)
        stats_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.stats_label = tk.Label(stats_frame, 
                                   text="📊 6 scanners disponibles | Configuration API optionnelle",
                                   fg="#00ff88", bg="#1a1a1a", font=("Arial", 10))
        self.stats_label.pack(pady=8)
        
        separator = tk.Frame(self.root, height=2, bg="#1a1a1a")
        separator.pack(fill=tk.X, padx=50, pady=10)
        
        # Zone des outils
        tools_frame = tk.Frame(self.root, bg="#0a0a0a")
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)
        
        tools = [
            ("🤖 AI PREDICTIVE SCANNER", "Scan 10x plus rapide\nMachine Learning", "ai_scanner", "#00ff88"),
            ("🌐 OSINT SCANNER", "Shodan + Censys + DNS\nReconnaissance avancee", "osint_scanner", "#00aaff"),
            ("🤝 P2P SCANNER", "Reseau mondial\nDetection de censure", "p2p_scanner", "#ffaa00"),
            ("👻 PASSIVE SCANNER", "0 paquet envoye\nIndetectable", "passive_scanner", "#ff00ff"),
            ("⏰ TIME MACHINE", "Analyse historique\nPredictions futures", "timemachine_scanner", "#ff6600"),
            ("🕶️ HOLO RADAR 3D", "Visualisation immersive\nTemps reel", "holo_scanner", "#00ffff"),
        ]
        
        # Grille 2x3
        for i, (name, desc, module, color) in enumerate(tools):
            row = i // 3
            col = i % 3
            self.create_tool_card(tools_frame, name, desc, module, color, row, col)
        
        # Footer
        footer = tk.Label(self.root, text="SENTRAX AI Suite v1.0 | Developpe par Pat's Ndaye | Tous droits reserves",
                         font=("Arial", 9), fg="#444444", bg="#0a0a0a")
        footer.pack(pady=10)
    
    def create_tool_card(self, parent, name, desc, module, color, row, col):
        """Cree une carte pour chaque outil"""
        
        card = tk.Frame(parent, bg="#1a1a1a", relief=tk.RAISED, bd=1, width=280, height=180)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)
        
        # Titre
        title = tk.Label(card, text=name, font=("Arial", 11, "bold"),
                        fg=color, bg="#1a1a1a", wraplength=250)
        title.pack(pady=(15, 5))
        
        # Description
        description = tk.Label(card, text=desc, font=("Arial", 9),
                              fg="#888888", bg="#1a1a1a", justify=tk.CENTER)
        description.pack(pady=5)
        
        # Bouton
        btn = tk.Button(card, text="LANCER", 
                       command=lambda m=module: self.launch_scanner(m),
                       bg=color, fg="#000000", font=("Arial", 10, "bold"),
                       padx=20, pady=5, cursor="hand2")
        btn.pack(pady=(15, 10))
        
        # Effet hover
        def on_enter(e): btn.configure(bg="#ffffff")
        def on_leave(e): btn.configure(bg=color)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    def launch_scanner(self, module_name):
        """Lance un scanner specifique"""
        
        script_path = Path(__file__).parent.parent / "scanners" / f"{module_name}.py"
        
        if not script_path.exists():
            messagebox.showerror("Erreur", f"Scanner non trouve: {module_name}.py\n\nChemin: {script_path}")
            return
        
        try:
            if sys.platform == "win32":
                subprocess.Popen([sys.executable, str(script_path)], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, str(script_path)])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer le scanner:\n{str(e)}")
    
    def open_api_config(self):
        """Ouvre la fenetre de configuration des APIs"""
        try:
            from src.gui.config_window import ConfigWindow
            ConfigWindow(self.root)
        except ImportError as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir la configuration:\n{str(e)}")
    
    def export_results(self):
        """Exporte les resultats (a implementer)"""
        messagebox.showinfo("Export", "Fonctionnalite a venir\n\n"
                            "Chaque scanner peut exporter ses resultats individuellement")
    
    def show_docs(self):
        """Affiche la documentation"""
        docs = """
📖 DOCUMENTATION SENTRAX AI SUITE

🔍 SCANNERS DISPONIBLES:

1. AI Predictive Scanner
   - Utilise l'IA pour predire les ports ouverts
   - Jusqu'a 10x plus rapide

2. OSINT Scanner
   - Reconnaissance passive via Shodan, Censys, DNS
   - Configurez vos cles API pour plus de donnees

3. P2P Scanner
   - Scan distribue depuis plusieurs pays
   - Detecte la censure et les blocages

4. Passive Scanner
   - 0 paquet envoye vers la cible
   - Utilise uniquement des sources publiques

5. Time Machine Scanner
   - Analyse l'historique des scans
   - Predis les changements futurs

6. Holographic Radar 3D
   - Visualisation en temps reel
   - Interface holographique

🔧 CONFIGURATION:

- Cliquez sur "Outils > Configuration des APIs"
- Ajoutez vos cles Shodan, Censys, etc.
- Tous les champs sont optionnels

📁 RAPPORTS:

- Chaque scanner peut exporter ses resultats
- Formats: TXT, JSON, CSV, HTML
        """
        messagebox.showinfo("Documentation", docs)
    
    def show_about(self):
        """Affiche les informations"""
        about = """
🧠 SENTRAX AI SUITE v1.0

Platforme de cybersecurite nouvelle generation
Developpee par Pat's Ndaye

Fonctionnalites:
- 6 scanners integres
- IA, OSINT, P2P, Passif, Time Machine, 3D
- Configuration API optionnelle
- Rapports multi-formats

© 2024 - Tous droits reserves
        """
        messagebox.showinfo("A propos", about)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SENTRAXMainWindow()
    app.run()