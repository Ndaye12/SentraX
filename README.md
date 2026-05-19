# 🛡️ SENTRAX - cybersécurité professionnelle

**Version 3.1.0** | Licence MIT | Open Source

[![Site Web](https://img.shields.io/badge/Web-SentraX-blue)](https://ndaye12.github.io/SentraX/)
[![Version](https://img.shields.io/badge/version-3.1.0-green)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

![SENTRAX Dashboard](banner.png)
*Dashboard web de SENTRAX*

---

## 🎯 À propos

**10 scanners • API REST • Dashboard • Open Source**

SENTRAX est une suite de cybersécurité complète intégrant :

- 10 scanners réseau professionnels
- API REST sécurisée (JWT, 2FA, rate limiting)
- Dashboard web moderne (clair/sombre, graphiques, historique)
- EXE autonome (30 Mo, sans installation)

---

## ✨ Fonctionnalités principales

✔ 10 scanners réseau (TCP, SYN, UDP, ICMP, SNMP, DNS…)  
✔ API REST sécurisée (JWT + 2FA + rate limiting)  
✔ Dashboard web moderne (thème clair/sombre, graphiques Chart.js)  
✔ Export PDF / JSON / CSV / HTML  
✔ Système de plugins extensible  
✔ Scanner CVE (EternalBlue, BlueKeep, Heartbleed…)  
✔ Analyse SSL/TLS  
✔ Docker + CI/CD GitHub Actions  
✔ EXE autonome (Windows)

---

## 📥 Téléchargement

- **Windows EXE** : [Télécharger SENTRAX v3.1](https://drive.google.com/file/d/1Dn01CZFKGJ6BHd5LoU9qTSFieCJYBlGz/view?usp=sharing)
- **Site officiel** : [https://ndaye12.github.io/SentraX/](https://ndaye12.github.io/SentraX/)

---

## 🚀 Démarrage rapide

### Via l’EXE (Windows)

1. Télécharger `SENTRAX.exe`
2. Double-clic pour lancer
3. Accéder au dashboard : [http://localhost:5000](http://localhost:5000)

### Via Python

```bash
git clone https://github.com/Ndaye12/SentraX.git
cd SentraX
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
python web/api.py
📊 Scanners inclus
Scanner	Description
SYN scan	Scan TCP furtif
UDP scan	Détection de services UDP
OS detection	15+ signatures OS
CVE scanner	EternalBlue, BlueKeep, Heartbleed…
SSL/TLS	Certificats, expiration, émetteurs
SNMP	Détection de périphériques réseau
DNS	Énumération de sous-domaines
OSINT	Shodan, Censys, GitHub
Passive	Reconnaissance passive sans paquets actifs
Time Machine	Analyse historique + prédictions
🔒 Sécurité
Authentification JWT

2FA (double facteur)

Rate limiting anti-bruteforce

Journalisation complète

📖 Documentation complète
https://ndaye12.github.io/SentraX/docs.html

## 👤 Auteur

**Patrick Ndaye**  

- **LinkedIn** : [patrick-ndaye-b5b67a399](https://www.linkedin.com/in/patrick-ndaye-b5b67a399)  
- **GitHub** : [Ndaye12](https://github.com/Ndaye12)  
- **WhatsApp** : [Me contacter](https://wa.me/243975659129?text=Bonjour%20Patrick%2C%20je%20suis%20intéressé%20par%20SENTRAX)

📜 Licence
MIT License – voir le fichier LICENSE.
