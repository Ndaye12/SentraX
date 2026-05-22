# Contribuer à SENTRAX

Merci de vouloir contribuer à SENTRAX ! Toute contribution est la bienvenue.

---

## 📋 Table des matières

- [Code de conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Ajouter un nouveau scanner](#ajouter-un-nouveau-scanner)
- [Ajouter un plugin](#ajouter-un-plugin)
- [Règles à respecter](#règles-à-respecter)
- [Tester son scanner](#tester-son-scanner)
- [Soumettre une pull request](#soumettre-une-pull-request)
- [Signaler un bug](#signaler-un-bug)

---

## 📖 Code de conduite

Nous nous engageons à maintenir un environnement accueillant et respectueux.

- Utilisez un langage inclusif
- Respectez les points de vue différents
- Acceptez les critiques constructives

---

## 🚀 Comment contribuer

### Types de contributions acceptées

| Type | Description |
|------|-------------|
| 🐛 Bug report | Signaler une erreur |
| 🔧 Fix | Corriger un bug existant |
| ✨ Feature | Ajouter une nouvelle fonctionnalité |
| 📚 Documentation | Améliorer la documentation |
| 🔌 Plugin | Ajouter un nouveau plugin |
| 🧪 Test | Ajouter des tests unitaires |

---

## 🔌 Ajouter un nouveau scanner

### 1. Créer le fichier du scanner

```bash
touch src/scanners/mon_scanner.py
2. Structure obligatoire
python
#!/usr/bin/env python3
"""Description du scanner - SENTRAX"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading


class MonScanner:
    """Scanner personnalisé pour SENTRAX"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SENTRAX - Mon Scanner")
        self.root.geometry("800x600")
        self.root.configure(bg="#0a0a0a")
        self.setup_ui()
        self.center_window()

    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Configure l'interface graphique"""
        # Header
        header = tk.Label(self.root, text="🔍 MON SCANNER",
                          font=("Arial", 20, "bold"),
                          fg="#00ff88", bg="#0a0a0a")
        header.pack(pady=20)

        # Zone de scan
        frame = tk.Frame(self.root, bg="#1a1a1a", bd=2, relief=tk.RAISED)
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Target input
        tk.Label(frame, text="Cible (IP ou domaine):",
                 fg="#00ff88", bg="#1a1a1a").pack(pady=5)
        self.target_entry = tk.Entry(frame, width=40, bg="#0a0a0a",
                                      fg="#00ff88", insertbackground="#00ff88")
        self.target_entry.pack(pady=5)

        # Scan button
        self.scan_btn = tk.Button(frame, text="LANCER LE SCAN",
                                  command=self.start_scan,
                                  bg="#00ff88", fg="#000",
                                  font=("Arial", 10, "bold"))
        self.scan_btn.pack(pady=10)

        # Results area
        self.results_text = tk.Text(frame, height=15, bg="#0a0a0a",
                                     fg="#00ff88", wrap=tk.WORD)
        self.results_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def start_scan(self):
        """Démarre le scan dans un thread séparé"""
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Erreur", "Entrez une cible")
            return

        self.scan_btn.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Scan en cours...\n")

        thread = threading.Thread(target=self.scan, args=(target,), daemon=True)
        thread.start()

    def scan(self, target):
        """Logique du scan (exécuté dans un thread)"""
        try:
            ip = socket.gethostbyname(target)
            self.update_results(f"Cible: {target} -> {ip}\n")
            self.update_results("-" * 50 + "\n")

            open_ports = []
            ports = [21, 22, 80, 443]  # Ports à tester

            for port in ports:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    if s.connect_ex((ip, port)) == 0:
                        try:
                            service = socket.getservbyport(port)
                        except:
                            service = "unknown"
                        open_ports.append({"port": port, "service": service})
                        self.update_results(f"✅ Port {port} ouvert - {service}\n")
                    s.close()
                except:
                    pass

            if not open_ports:
                self.update_results("Aucun port ouvert trouvé\n")

        except Exception as e:
            self.update_results(f"❌ Erreur: {str(e)}\n")

        finally:
            self.root.after(0, self.enable_button)

    def update_results(self, text):
        """Met à jour l'affichage des résultats (thread-safe)"""
        self.root.after(0, lambda: self.results_text.insert(tk.END, text))

    def enable_button(self):
        """Réactive le bouton de scan"""
        self.scan_btn.config(state=tk.NORMAL)

    def run(self):
        """Lance l'application"""
        self.root.mainloop()


def main():
    """Point d'entrée du scanner"""
    app = MonScanner()
    app.run()


if __name__ == "__main__":
    main()
3. Ajouter au launcher
Dans launcher.py, ajoute dans la liste tools :

python
tools = [
    # ... scanners existants ...
    ("🔧 MON SCANNER", "Description courte\nde mon scanner", "mon_scanner", "#ffaa00"),
]
4. Ajouter à l'API
Dans web/api.py, ajoute dans SCANNERS :

python
SCANNERS = [
    # ... scanners existants ...
    {'id': 'mon_scanner', 'name': 'Mon Scanner', 'desc': 'Description courte', 'icon': '🔧'},
]
5. Ajouter au build (optionnel)
python
# build_exe.py
"--hidden-import", "src.scanners.mon_scanner",
🔌 Ajouter un plugin
Les plugins sont des modules supplémentaires qui étendent les fonctionnalités.

Structure d'un plugin
python
#!/usr/bin/env python3
"""Plugin SENTRAX - Description"""

class Plugin:
    name = "Nom du plugin"
    version = "1.0.0"
    author = "Votre nom"
    description = "Description du plugin"

    def run(self, target, options=None):
        """
        Exécute le plugin sur une cible
        Retourne un dict avec les résultats
        """
        results = {
            "status": "success",
            "data": {},
            "error": None
        }

        try:
            # Logique du plugin
            pass
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        return results

    def get_info(self):
        """Retourne les informations du plugin"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description
        }
📏 Règles à respecter
Règle	Pourquoi
Timeout de 2-3 secondes	Éviter les blocages
Threading pour les scans	Ne pas bloquer l'interface
root.after() pour les mises à jour	Thread-safe pour Tkinter
Gestion des erreurs try/except	Éviter les crashes
Fonction main() obligatoire	Compatibilité avec l'EXE
Docstring pour chaque fonction	Documentation automatique
Pas de credentials en clair	Sécurité
🧪 Tester son scanner
Test unitaire
bash
python src/scanners/mon_scanner.py
Test via le launcher
bash
python launcher.py
Test via l'API
bash
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -d '{"target":"scanme.nmap.org","scanner":"mon_scanner"}'
Tests automatisés
bash
pytest tests/test_scanners.py -v
📤 Soumettre une pull request
Fork le dépôt sur GitHub

Crée une branche :

bash
git checkout -b feature/mon-scanner
Commit tes modifications :

bash
git add .
git commit -m "feat: Ajout du scanner XXX"
Push :

bash
git push origin feature/mon-scanner
Ouvre une Pull Request sur GitHub

Format des messages de commit
Type	Description
feat:	Nouvelle fonctionnalité
fix:	Correction de bug
docs:	Documentation
style:	Formatage, typos
refactor:	Refactorisation
test:	Tests
chore:	Maintenance
🐛 Signaler un bug
Ouvre une issue sur GitHub avec :

Version de SENTRAX

Système d'exploitation

Étapes pour reproduire

Comportement attendu vs réel

Logs ou captures d'écran

📧 Contact
Pour toute question : patrickndaye919@gmail.com

🙏 Merci
Merci de contribuer à SENTRAX ! Chaque contribution compte. 💪

SENTRAX - © 2026 Patrick Ndaye