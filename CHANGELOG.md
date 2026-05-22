# Changelog - SENTRAX

Toutes les modifications notables du projet SENTRAX.

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

---

## [3.1.0] - 2026-05-20

### Ajouté

- **Authentification JWT** : Tokens sécurisés avec expiration (8h)
- **Double authentification (2FA)** : TOTP avec Google Authenticator
- **Rate limiting** : Protection anti-bruteforce (5 tentatives max)
- **Système de plugins extensible**
  - Moteur de chargement dynamique
  - Plugin HTTP Enumeration
  - Plugin SMB OS Detection
- **Analyse SSL/TLS**
  - Extraction des certificats
  - Détection d'expiration
  - Information sur l'émetteur
- **Scanner de vulnérabilités CVE**
  - CVE-2017-0144 (EternalBlue)
  - CVE-2019-0708 (BlueKeep)
  - CVE-2014-0160 (Heartbleed)
  - CVE-2020-0796 (SMBGhost)
  - CVE-2021-41773 (Apache Path Traversal)
- **Signatures OS avancées (15+ signatures)**
  - Windows 10/11 moderne
  - Windows 7/8 ancien
  - Linux 3.x/4.x
  - Linux 2.4/2.6 ancien
  - MacOS X
  - FreeBSD/OpenBSD
  - Cisco Router/IOS
  - Android/Linux mobile
- **Nouvelles probes UDP**
  - Port 500 (IKE - VPN IPSec)
  - Port 1701 (L2TP - VPN)
  - Port 1812 (RADIUS - Authentification)
  - Port 33434 (Traceroute)
- **Renommage du projet** : VULGUARD → SENTRAX
- **Réinitialisation du mot de passe** : Lien valable 1 heure
- **Création de compte utilisateur** : Inscription avec validation de mot de passe fort

### Amélioré

- Détection OS plus précise
- Scan UDP plus complet
- Cache DNS pour meilleures performances
- Monitoring mémoire
- Interface dashboard responsive (mobile-friendly)
- Sécurité des mots de passe (hachage avec Werkzeug)

### Corrigé

- Erreurs JavaScript dans le dashboard
- Problèmes de chargement des scanners
- Cache navigateur bloquant les mises à jour
- Gestion des ports occupés (auto-détection)

---

## [3.0.0] - 2026-05-15

### Ajouté

- **10 scanners réseau professionnels**
  - AI Predictive Scanner
  - OSINT Scanner (Shodan, Censys, DNS, GitHub)
  - P2P Scanner
  - Passive Scanner
  - Time Machine Scanner
  - Holographic Radar 3D
  - Expert Scanner PRO (SYN + UDP + OS detection)
  - Ultra Scanner PRO (UDP avancé + ICMP + versions)
  - SNMP Scanner
  - DNS Scanner
- **API REST complète avec JWT**
- **Dashboard web moderne** (thème clair/sombre, graphiques Chart.js)
- **Support des scans** : TCP, SYN, UDP, ICMP
- **Détection OS basique** (TTL + Window size)
- **Export PDF des rapports** (avec ReportLab)
- **Envoi de rapports par email** (template configurable)
- **Historique SQLite** (stockage local)
- **Tests unitaires** (sécurité, intégration)
- **CI/CD GitHub Actions**
- **Documentation complète** (7 fichiers)
- **EXE autonome** (Windows, PyInstaller)
- **Support Docker** (conteneur)

### Sécurité

- Authentification JWT
- Hachage des mots de passe (SHA256)
- Rate limiting basique
- Tokens blacklist

---

## [2.0.0] - 2026-04-01

### Ajouté

- Version initiale publique
- Interface Tkinter
- 5 scanners de base
- Scan TCP simple
- Export JSON

---

## 🔗 Liens utiles

- [Site officiel](https://ndaye12.github.io/SentraX/)
- [Documentation](https://ndaye12.github.io/SentraX/docs.html)
- [GitHub](https://github.com/Ndaye12/SentraX)

---

**SENTRAX - © 2026 Patrick Ndaye**