# Architecture de SENTRAX

## Vue d'ensemble

SENTRAX est une suite de cybersécurité complète intégrant :

- **10 scanners réseau** professionnels
- **API REST** sécurisée (JWT + 2FA)
- **Dashboard web** moderne (thème clair/sombre)
- **Interface graphique** Tkinter
- **Système de plugins** extensible

---

## Structure du projet
SENTRAX/
├── launcher.py # Interface graphique Tkinter
├── build_exe.py # Script de build pour EXE
├── requirements.txt # Dépendances Python
├── README.md # Documentation principale
├── LICENSE # Licence MIT
├── DISCLAIMER.txt # Avertissement légal
├── CONFIDENTIALITE.txt # Politique de confidentialité
├── SECURITY.md # Signalement vulnérabilités
├── CHANGELOG.md # Historique des versions
├── ROADMAP.md # Feuille de route
├── .env # Variables d'environnement
├── Dockerfile # Conteneurisation
├── docker-compose.yml # Orchestration Docker
├── setup.py # Packaging Python
├── pyproject.toml # Configuration moderne
│
├── src/
│ ├── scanners/ # 10 scanners indépendants
│ │ ├── ai_scanner.py
│ │ ├── osint_scanner.py
│ │ ├── p2p_scanner.py
│ │ ├── passive_scanner.py
│ │ ├── timemachine_scanner.py
│ │ ├── holo_scanner.py
│ │ ├── expert_scanner.py
│ │ ├── ultra_scanner.py
│ │ ├── snmp_scanner.py
│ │ └── dns_scanner.py
│ │
│ ├── plugins/ # Système de plugins
│ │ ├── init.py
│ │ ├── base_plugin.py
│ │ ├── plugin_engine.py
│ │ ├── http_enum.py
│ │ └── smb_os.py
│ │
│ ├── core/ # Modules centraux
│ │ ├── network.py # TCP, UDP, ICMP, SYN scan
│ │ ├── cve_database.py # Base de vulnérabilités CVE
│ │ ├── cve_scanner.py # Scanner CVE
│ │ ├── ssl_analyzer.py # Analyse certificats SSL/TLS
│ │ ├── export_manager.py # Export JSON/CSV/HTML/TXT/PDF
│ │ ├── scan_database.py # Historique SQLite
│ │ ├── email_reporter.py # Rapports par email
│ │ ├── memory_monitor.py # Monitoring mémoire
│ │ └── constants.py # Constantes globales
│ │
│ └── gui/ # Composants GUI (optionnel)
│
├── web/
│ ├── api.py # API REST Flask (complète)
│ └── templates/ # Templates HTML (dashboard)
│
├── tests/ # Tests unitaires
│ ├── test_scanners.py
│ ├── test_security.py
│ └── test_integration.py
│
├── docs/ # Documentation
├── assets/
│ └── icons/
│ └── shield.ico # Icône de l'EXE
│
└── dist/ # EXE autonome (~32 MB)

text

---

## Composants principaux

### Backend (`src/core/network.py`)

| Fonctionnalité | Description |
|----------------|-------------|
| Scan TCP connect | Connexion TCP standard |
| Scan SYN (half-open) | Scan furtif avec Scapy (nécessite admin) |
| Scan UDP avancé | 15+ probes (DNS, SNMP, IKE, L2TP, RADIUS) |
| Scan ICMP | Découverte réseau |
| Détection OS avancée | 15+ signatures (Windows 10/11, Linux, MacOS, Cisco) |
| Banner grabbing | Récupération des bannières services |
| Version detection | Détection des versions logicielles |

### Authentification et sécurité

| Module | Description |
|--------|-------------|
| `generate_token()` | Création token JWT (expiration 8h) |
| `verify_token()` | Validation token |
| `@token_required` | Décorateur pour routes protégées |
| `rate_limit()` | Protection anti-bruteforce (5 tentatives) |
| `validate_password_strength()` | Validation mot de passe fort (8+, maj, min, chiffre, spécial) |

### Système de plugins (`src/plugins/`)

```python
# BasePlugin - Tous les plugins héritent de cette classe
class BasePlugin:
    name = "Plugin de base"
    version = "1.0.0"
    applicable_ports = []

    def run(self, target, port, banner=None):
        raise NotImplementedError
Plugins inclus :

Plugin	Description
HTTP Enumeration	Énumération des chemins web courants
SMB OS Detection	Détection OS via SMB
Analyse SSL/TLS (src/core/ssl_analyzer.py)
Extraction des certificats

Détection d'expiration

Information sur l'émetteur

Analyse des protocoles supportés

Scanner CVE (src/core/cve_scanner.py)
CVE	Nom	Port
CVE-2017-0144	EternalBlue	445
CVE-2019-0708	BlueKeep	3389
CVE-2014-0160	Heartbleed	443
CVE-2020-0796	SMBGhost	445
CVE-2021-41773	Apache Path Traversal	80/443
Base de données
Type : SQLite (sentrax.db)

Tables : users, reset_tokens, security_logs

Historique : Stockage local des résultats en JSON

API REST (web/api.py)
Route	Méthode	Protection	Description
/api/login	POST	Rate limit	Authentification
/api/register	POST	-	Création compte
/api/forgot-password	POST	-	Demande reset
/api/reset-password	POST	-	Reset mot de passe
/api/change-password	POST	JWT	Changer mot de passe
/api/2fa/setup	POST	JWT	Activer 2FA
/api/2fa/verify	POST	JWT	Vérifier 2FA
/api/2fa/disable	POST	JWT	Désactiver 2FA
/api/scan	POST	JWT	Lancer un scan
/api/scan/<id>	GET	JWT	Résultat scan
/api/scanners	GET	JWT	Liste scanners
/api/export/pdf/<id>	GET	JWT	Export PDF
/api/logout	POST	JWT	Déconnexion
/api/verify	GET	JWT	Vérifier token
Dashboard Web
Page	Contenu
Dashboard	Formulaire de scan, résultats, graphiques, historique
Scanners	Liste des 10 scanners disponibles
Sécurité	Changement mot de passe, activation/désactivation 2FA
Aide	Documentation et support
Scanners disponibles
ID	Nom	Icône	Description
ai	AI Predictive Scanner	🤖	Scan optimisé par IA
osint	OSINT Scanner	🌐	Reconnaissance passive
p2p	P2P Scanner	🤝	Scan distribué
passive	Passive Scanner	👻	0 paquet envoyé
timemachine	Time Machine Scanner	⏰	Analyse historique
holo	Holographic Radar	🕶️	Visualisation 3D
expert	Expert Scanner PRO	👑	SYN + UDP + OS
ultra	Ultra Scanner PRO	🔥	UDP avancé + ICMP
snmp	SNMP Scanner	🔌	Détection SNMP
dns	DNS Scanner	📡	Énumération DNS
Technologies
Technologie	Version	Utilisation
Python	3.8+	Langage principal
Flask	2.2+	API REST
Tkinter	-	Interface graphique
Socket	-	Scans réseau
SQLite	3	Historique
PyJWT	2.8+	Authentification
PyOTP	2.8+	2FA TOTP
QRCode	7.4+	Génération QR codes
ReportLab	4.0+	Export PDF
Werkzeug	2.2+	Hachage mots de passe
PyInstaller	5.0+	Packaging EXE
Docker	20+	Conteneurisation
Communication entre modules
text
┌─────────────────┐     ┌─────────────────┐
│   launcher.py   │     │   web/api.py    │
│   (Tkinter)     │     │     (Flask)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│           src/scanners/                 │
│         (10 scanners)                   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│            src/core/network.py          │
│         (TCP, UDP, ICMP, SYN)           │
└────────────────────┬────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
┌─────────────┐ ┌───────────┐ ┌─────────────────┐
│ src/plugins/│ │ src/core/ │ │ src/core/       │
│             │ │cve_scanner│ │ssl_analyzer     │
└─────────────┘ └───────────┘ └─────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│       src/core/scan_database.py         │
│            (SQLite)                     │
└─────────────────────────────────────────┘
Sécurité
Niveau	Mesure
Authentification	JWT avec expiration 8h
Double authentification	TOTP (Google Authenticator)
Protection	Rate limiting (5 tentatives)
Blacklist	Tokens déconnectés
Logs	Traçabilité des connexions
Validation	Mots de passe forts (8+, maj, min, chiffre, spécial)
Environnement	Variables d'environnement (.env)
Cache	DNS cache pour performances
Tests
Type	Fichier	Description
Unitaires	tests/test_scanners.py	Tests des scanners
Sécurité	tests/test_security.py	Tests JWT, 2FA, rate limiting
Intégration	tests/test_integration.py	Tests API complètes
Exécution des tests
bash
# Tous les tests
pytest tests/

# Tests spécifiques
pytest tests/test_security.py -v

# Avec couverture
pytest --cov=src tests/
Build et distribution
bash
# Build EXE autonome
python build_exe.py
# ou
pyinstaller --onefile --name SENTRAX --add-data "web;web" --add-data "src;src" launcher.py

# Lancer l'API
python web/api.py

# Lancer l'interface graphique
python launcher.py

# Lancer les tests
pytest tests/
Plugin System - Guide d'ajout
Structure d'un plugin
python
from src.plugins.base_plugin import BasePlugin

class MonPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "Mon Plugin"
        self.version = "1.0"
        self.author = "Votre Nom"
        self.description = "Description du plugin"
        self.applicable_ports = [80, 443, 8080]

    def run(self, target, port, banner=None):
        """
        Exécute le plugin sur une cible

        Args:
            target (str): IP ou domaine
            port (int): Port à analyser
            banner (str, optional): Banner récupéré

        Returns:
            dict: Résultats du plugin
        """
        results = {
            "plugin": self.name,
            "target": target,
            "port": port,
            "data": {}
        }

        # Logique du plugin
        # ...

        return results
Installation automatique
Les plugins sont automatiquement chargés depuis src/plugins/ grâce au plugin_engine.py.

Auteur
Patrick Ndaye - Développeur cybersécurité

Email : patrickndaye919@gmail.com

GitHub : github.com/Ndaye12

LinkedIn : patrick-ndaye

Licence
MIT License - Open Source

© 2026 Patrick Ndaye - SENTRAX | Professional Cybersecurity Tool