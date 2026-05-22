# 🛡️ SENTRAX - Suite de cybersécurité professionnelle

**Version 3.1.0** | Licence MIT | Open Source

[![Site Web](https://img.shields.io/badge/Web-SentraX-blue)](https://ndaye12.github.io/SentraX/)
[![Version](https://img.shields.io/badge/version-3.1.0-green)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)

---

## 🎯 À propos

**10 scanners • API REST • Dashboard • Open Source**

SENTRAX est une suite de cybersécurité complète intégrant :

- ✅ **10 scanners réseau** professionnels
- ✅ **API REST sécurisée** (JWT, 2FA, rate limiting)
- ✅ **Dashboard web moderne** (clair/sombre, graphiques, historique)
- ✅ **EXE autonome** (Windows) et **version source** (Linux/Mac)

---

## ✨ Fonctionnalités principales

| Catégorie | Fonctionnalités |
|-----------|-----------------|
| **Scanners** | TCP, SYN, UDP, ICMP, SNMP, DNS, OSINT, Passif, Time Machine, CVE |
| **Sécurité** | JWT, 2FA (TOTP), rate limiting (5 tentatives), logs d'audit |
| **Interface** | Dashboard web (Chart.js), thème clair/sombre, historique |
| **Export** | PDF, JSON, CSV, HTML |
| **Extensible** | Système de plugins, Docker, CI/CD |

---

## 📋 Scanners inclus (10)

| Scanner | Description |
|---------|-------------|
| 🔍 SYN scan | Scan TCP furtif |
| 📡 UDP scan | Détection de services UDP |
| 🖥️ OS detection | 15+ signatures OS |
| 🛡️ CVE scanner | EternalBlue, BlueKeep, Heartbleed |
| 🔐 SSL/TLS | Certificats, expiration, émetteurs |
| 🔌 SNMP | Détection de périphériques réseau |
| 📡 DNS | Énumération de sous-domaines |
| 🌐 OSINT | Shodan, Censys, GitHub |
| 👻 Passive | Reconnaissance passive (0 paquet) |
| ⏰ Time Machine | Analyse historique + prédictions |

---

## 🔐 Identifiants par défaut

| Champ | Valeur |
|-------|--------|
| **Nom d'utilisateur** | `admin` |
| **Mot de passe** | `Admin123!` |

⚠️ **Changez le mot de passe dès la première utilisation !**

---

## 📥 Téléchargement

- **Windows EXE** : [Télécharger SENTRAX v3.1](https://github.com/Ndaye12/SentraX/releases/download/v3.1.0/SENTRAX.exe)
- **Site officiel** : [https://ndaye12.github.io/SentraX/](https://ndaye12.github.io/SentraX/)
- **GitHub** : [https://github.com/Ndaye12/SentraX](https://github.com/Ndaye12/SentraX)

---

## 🚀 Démarrage rapide

### 🪟 Windows (EXE)

1. Télécharger `SENTRAX.exe`
2. Double-clic pour lancer
3. Menu → **Help → Dashboard**
4. Dashboard : [http://localhost:5000/dashboard](http://localhost:5000/dashboard)

### 🐧 Linux / 🍎 macOS (source)

```bash
git clone https://github.com/Ndaye12/SentraX.git
cd SentraX
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python web/api.py
🐳 Docker (tous OS)
bash
docker build -t sentrax:3.1.0 .
docker run -p 5000:5000 sentrax:3.1.0
🔒 Sécurité
Fonctionnalité	Description
JWT	Tokens sécurisés avec expiration 8h
2FA	Double authentification TOTP (Google Authenticator)
Rate limiting	5 tentatives max, blocage 5 minutes
Journalisation	Logs complets des connexions et actions
Mots de passe	Hashés avec Werkzeug (bcrypt)
📖 Documentation complète
Site officiel

Documentation

API REST

Sécurité

👤 Auteur
Patrick Ndaye - Développeur cybersécurité

🔗 LinkedIn

🐙 GitHub

💬 WhatsApp

📧 patrickndaye919@gmail.com

📜 Licence
MIT License – Open Source

© 2026 Patrick Ndaye - SENTRAX | Designed for cybersecurity professionals
