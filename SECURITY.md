# Politique de Sécurité - SENTRAX

## 🔒 Signaler une vulnérabilité

Si vous découvrez une vulnérabilité de sécurité dans SENTRAX, merci de nous contacter **directement** plutôt que d'ouvrir une issue publique.

### Contact

| Méthode | Information |
|---------|-------------|
| **Email** | `patrickndaye919@gmail.com` |
| **PGP Key** | Sur demande |

---

## 📋 Processus

1. **Signalement** : Envoyez un email détaillant la vulnérabilité
2. **Accusé de réception** : Sous 48h ouvrées
3. **Analyse** : Nous évaluons l'impact et la criticité
4. **Correctif** : Publication dans les meilleurs délais
5. **Divulgation** : Annonce publique après correction

### Délais estimés

| Criticité | Délai de correction |
|-----------|---------------------|
| Critique | 7 jours |
| Élevée | 14 jours |
| Moyenne | 30 jours |
| Faible | 60 jours |

---

## 🎯 Portée

| Composant | Versions supportées | Statut |
|-----------|---------------------|--------|
| SENTRAX Core | v3.1+ | ✅ Supportée |
| API REST | v3.1+ | ✅ Supportée |
| Dashboard Web | v3.1+ | ✅ Supportée |
| Scanners (10) | v3.1+ | ✅ Supportée |
| Interface Tkinter | v3.1+ | ✅ Supportée |
| SENTRAX Core | v3.0 | ⚠️ Sécurité uniquement |
| SENTRAX Core | < v3.0 | ❌ Non supportée |

---

## 📝 Divulgation responsable

Nous demandons aux chercheurs de sécurité de :

- ✅ **Ne pas exploiter** la vulnérabilité
- ✅ **Ne pas divulguer** publiquement avant correction
- ✅ **Fournir des détails** suffisants pour reproduire
- ✅ **Respecter** les délais de divulgation

### Reconnaissance

Les chercheurs qui signalent des vulnérabilités seront :

- Mentionnés dans le `CHANGELOG.md`
- Crédités dans les notes de release (si souhaité)

---

## 🔐 Bonnes pratiques de sécurité

### Pour les utilisateurs

| Recommandation | Importance |
|----------------|------------|
| Changer le mot de passe par défaut (`admin`/`Admin123!`) | 🔴 Critique |
| Activer la double authentification (2FA) | 🟠 Élevée |
| Utiliser HTTPS en production | 🟠 Élevée |
| Mettre à jour vers la dernière version | 🟡 Moyenne |
| Sauvegarder la base de données (`sentrax.db`) | 🟡 Moyenne |
| Ne pas partager les tokens JWT | 🔴 Critique |

### Pour les déployements

```bash
# Générer une clé SECRET_KEY sécurisée
python -c "import secrets; print(secrets.token_hex(64))"

# Configurer un mot de passe admin fort
export ADMIN_PASSWORD="VotreMotDePasseTresFort123!"

# Désactiver le debug en production
export FLASK_ENV=production
📊 Criticité des vulnérabilités
Niveau	Description
🔴 Critique	Accès non autorisé, exécution de code à distance
🟠 Élevée	Fuite de données sensibles, élévation de privilèges
🟡 Moyenne	Cross-site scripting (XSS), CSRF
🟢 Faible	Information disclosure, best practices
📜 Historique des sécurités
Version	Correctifs de sécurité
v3.1.0	Mots de passe forts, rate limiting, 2FA, JWT
v3.0.0	Authentification de base, hash SHA256
v2.0.0	Pas d'authentification
🔗 Liens utiles
Documentation

Rapport de vulnérabilité

Page des releases

Merci de contribuer à la sécurité de SENTRAX !

Dernière mise à jour : Mai 2026

SENTRAX v3.1.0 - © 2026 Patrick Ndaye