# API REST SENTRAX

## Base URL
http://localhost:5000/api

text

## 🔐 Authentification

L'API utilise **JWT (JSON Web Tokens)** pour l'authentification.

### Login

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'
Réponse :

json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "admin"
}
Utilisation du token
bash
curl -X GET http://localhost:5000/api/scanners \
  -H "Authorization: Bearer VOTRE_TOKEN"
Création de compte
bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"monuser","password":"MonPassword123!","email":"user@example.com"}'
Mot de passe oublié
bash
curl -X POST http://localhost:5000/api/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"username":"monuser"}'
Réinitialisation du mot de passe
bash
curl -X POST http://localhost:5000/api/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token":"TOKEN_RECU","new_password":"NouveauPassword123!"}'
Changement de mot de passe (authentifié)
bash
curl -X POST http://localhost:5000/api/change-password \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"AncienPassword123!","new_password":"NouveauPassword123!"}'
📡 Endpoints
GET /health
Vérifier l'état du service.

bash
curl http://localhost:5000/api/health
Réponse :

json
{
  "status": "healthy",
  "version": "3.1.0",
  "timestamp": "2026-05-20T12:00:00.000000",
  "scanners_count": 10
}
GET /scanners
Lister les 10 scanners disponibles (authentifié).

bash
curl -X GET http://localhost:5000/api/scanners \
  -H "Authorization: Bearer VOTRE_TOKEN"
Réponse :

json
[
  {
    "id": "ai",
    "name": "AI Predictive Scanner",
    "desc": "Scan utilisant l'intelligence artificielle",
    "icon": "🤖"
  },
  {
    "id": "osint",
    "name": "OSINT Scanner",
    "desc": "Reconnaissance via Shodan, Censys, DNS",
    "icon": "🌐"
  },
  ...
]
POST /scan
Lancer un scan asynchrone (authentifié).

bash
curl -X POST http://localhost:5000/api/scan \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org","scanner":"expert"}'
Paramètres :

Champ	Type	Description	Obligatoire
target	string	IP ou domaine	✅ Oui
scanner	string	Type de scanner	❌ Non (défaut: expert)
Scanners disponibles :

ID	Nom
ai	AI Predictive Scanner
osint	OSINT Scanner
p2p	P2P Scanner
passive	Passive Scanner
timemachine	Time Machine Scanner
holo	Holographic Radar
expert	Expert Scanner PRO
ultra	Ultra Scanner PRO
snmp	SNMP Scanner
dns	DNS Scanner
Réponse :

json
{
  "scan_id": "abc12345",
  "status": "started"
}
GET /scan/{scan_id}
Récupérer les résultats d'un scan (authentifié).

bash
curl -X GET http://localhost:5000/api/scan/abc12345 \
  -H "Authorization: Bearer VOTRE_TOKEN"
Réponse (en cours) :

json
{
  "id": "abc12345",
  "target": "scanme.nmap.org",
  "scanner": "expert",
  "status": "running",
  "started_at": "2026-05-20T12:00:00.000000"
}
Réponse (terminé) :

json
{
  "id": "abc12345",
  "target": "scanme.nmap.org",
  "scanner": "expert",
  "status": "completed",
  "results": {
    "target": "scanme.nmap.org",
    "ip": "45.33.32.156",
    "open_ports": [
      {"port": 22, "service": "ssh"},
      {"port": 80, "service": "http"}
    ],
    "timestamp": "2026-05-20T12:00:05.000000"
  }
}
GET /export/pdf/{scan_id}
Exporter les résultats en PDF (authentifié).

bash
curl -X GET http://localhost:5000/api/export/pdf/abc12345 \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  --output rapport.pdf
POST /logout
Déconnexion (authentifié).

bash
curl -X POST http://localhost:5000/api/logout \
  -H "Authorization: Bearer VOTRE_TOKEN"
GET /verify
Vérifier la validité du token (authentifié).

bash
curl -X GET http://localhost:5000/api/verify \
  -H "Authorization: Bearer VOTRE_TOKEN"
Réponse :

json
{
  "valid": true,
  "username": "admin"
}
🔒 2FA (Double authentification)
Configurer 2FA (authentifié)
bash
curl -X POST http://localhost:5000/api/2fa/setup \
  -H "Authorization: Bearer VOTRE_TOKEN"
Réponse :

json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgo..."
}
Vérifier et activer 2FA (authentifié)
bash
curl -X POST http://localhost:5000/api/2fa/verify \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"secret":"JBSWY3DPEHPK3PXP","code":"123456"}'
Désactiver 2FA (authentifié)
bash
curl -X POST http://localhost:5000/api/2fa/disable \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"123456"}'
📊 Codes d'erreur
Code	Signification
200	Succès
400	Requête invalide
401	Non authentifié / Token invalide
404	Scan non trouvé
409	Utilisateur existe déjà
429	Trop de tentatives (rate limiting)
500	Erreur serveur
Exemple d'erreur 401 :

json
{
  "error": "Token manquant"
}
🐍 Exemple complet Python
python
import requests
import time

# Configuration
BASE_URL = "http://localhost:5000/api"
USERNAME = "admin"
PASSWORD = "Admin123!"

# 1. Login
response = requests.post(f"{BASE_URL}/login", 
                         json={"username": USERNAME, "password": PASSWORD})
token = response.json()["token"]
print(f"Token obtenu: {token[:50]}...")

headers = {"Authorization": f"Bearer {token}"}

# 2. Lister les scanners
response = requests.get(f"{BASE_URL}/scanners", headers=headers)
scanners = response.json()
print(f"Scanners disponibles: {len(scanners)}")

# 3. Lancer un scan
response = requests.post(f"{BASE_URL}/scan",
                         headers=headers,
                         json={"target": "scanme.nmap.org", "scanner": "expert"})
scan_id = response.json()["scan_id"]
print(f"Scan lancé: {scan_id}")

# 4. Attendre les résultats
time.sleep(5)

# 5. Récupérer les résultats
response = requests.get(f"{BASE_URL}/scan/{scan_id}", headers=headers)
results = response.json()
print(f"Statut: {results['status']}")

if results["status"] == "completed":
    open_ports = results["results"]["open_ports"]
    print(f"Ports ouverts: {[p['port'] for p in open_ports]}")

# 6. Exporter en PDF
response = requests.get(f"{BASE_URL}/export/pdf/{scan_id}", headers=headers)
with open(f"rapport_{scan_id}.pdf", "wb") as f:
    f.write(response.content)
print(f"PDF exporté: rapport_{scan_id}.pdf")

# 7. Déconnexion
requests.post(f"{BASE_URL}/logout", headers=headers)
print("Déconnecté")
🌐 Dashboard web
Accédez au dashboard web interactif :

text
http://localhost:5000/dashboard
📚 Documentation interactive
Si Swagger/OpenAPI est configuré :

text
http://localhost:5000/api/docs
🔐 Règles des mots de passe
Règle	Exigence
Longueur	Au moins 8 caractères
Majuscule	Au moins une lettre majuscule
Minuscule	Au moins une lettre minuscule
Chiffre	Au moins un chiffre
Caractère spécial	Au moins un parmi !@#$%^&*(),.?":{}|<>
⚠️ Rate limiting
5 tentatives de connexion avant blocage

Durée du blocage : 5 minutes

SENTRAX v3.1.0 - © 2026 Patrick Ndaye