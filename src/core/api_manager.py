#!/usr/bin/env python3
"""Gestionnaire de cles API pour Shodan, Censys, etc."""

import os
import json
from pathlib import Path

class APIManager:
    """Gestionnaire centralise des cles API"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".SENTRAX"
        self.config_file = self.config_dir / "api_keys.json"
        self.keys = self.load_keys()
    
    def load_keys(self):
        """Charge les cles depuis le fichier de configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return self.get_default_config()
    
    def get_default_config(self):
        """Configuration par defaut avec instructions"""
        return {
            "shodan": {
                "key": "",
                "instructions": "Obtenez une cle sur https://account.shodan.io/register",
                "status": "optional",
                "rate_limit": "200 requetes/mois"
            },
            "censys": {
                "api_id": "",
                "api_secret": "",
                "instructions": "https://search.censys.io/account/api",
                "status": "optional",
                "rate_limit": "250 requetes/mois"
            },
            "securitytrails": {
                "key": "",
                "instructions": "https://securitytrails.com/",
                "status": "optional"
            },
            "github": {
                "token": "",
                "instructions": "https://github.com/settings/tokens",
                "status": "optional",
                "rate_limit": "60 requetes/heure"
            },
            "virustotal": {
                "key": "",
                "instructions": "https://www.virustotal.com/gui/join-us",
                "status": "optional"
            }
        }
    
    def save_keys(self):
        """Sauvegarde les cles dans le fichier de configuration"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.keys, f, indent=2)
        # Securite : restreindre les permissions
        os.chmod(self.config_file, 0o600)
    
    def get(self, service, key_name="key", default=None):
        """Recupere une cle API"""
        if service in self.keys:
            return self.keys[service].get(key_name, default)
        return default
    
    def set(self, service, value, key_name="key"):
        """Definit une cle API"""
        if service not in self.keys:
            self.keys[service] = {}
        self.keys[service][key_name] = value
        self.save_keys()
    
    def is_configured(self, service):
        """Verifie si une API est configuree"""
        if service == "censys":
            return bool(self.get(service, "api_id")) and bool(self.get(service, "api_secret"))
        return bool(self.get(service))
    
    def get_status(self):
        """Retourne le statut de toutes les APIs"""
        status = {}
        for service in self.keys:
            status[service] = {
                "configured": self.is_configured(service),
                "instructions": self.keys[service].get("instructions", ""),
                "rate_limit": self.keys[service].get("rate_limit", "N/A")
            }
        return status
    
    def setup_wizard_cli(self):
        """Assistant de configuration en ligne de commande"""
        print("\n" + "="*60)
        print("CONFIGURATION DES APIS SENTRAX AI")
        print("="*60)
        print("\nToutes les cles sont OPTIONNELLES")
        print("L'outil fonctionne sans, mais avec moins de fonctionnalites\n")
        
        for service, config in self.keys.items():
            print(f"\n[{service.upper()}]")
            print(f"  → {config.get('instructions', '')}")
            print(f"  → Limite: {config.get('rate_limit', 'N/A')}")
            
            if service == "censys":
                value = input("  API ID (laisser vide pour ignorer): ").strip()
                if value:
                    config["api_id"] = value
                    secret = input("  API Secret: ").strip()
                    config["api_secret"] = secret
            else:
                value = input(f"  Cle {service} (laisser vide pour ignorer): ").strip()
                if value:
                    config["key"] = value
        
        self.save_keys()
        print("\n✅ Configuration sauvegardee dans", self.config_file)
        print("🔒 Fichier securise (lecture uniquement pour vous)")
    
    def get_shodan_api(self):
        """Retourne l'objet Shodan si configure"""
        if self.is_configured("shodan"):
            try:
                import shodan
                return shodan.Shodan(self.get("shodan"))
            except ImportError:
                print("Module shodan non installe: pip install shodan")
        return None
    
    def get_censys_api(self):
        """Retourne l'objet Censys si configure"""
        if self.is_configured("censys"):
            try:
                from censys.search import CensysHosts
                return CensysHosts(
                    api_id=self.get("censys", "api_id"),
                    api_secret=self.get("censys", "api_secret")
                )
            except ImportError:
                print("Module censys non installe: pip install censys")
        return None

# Point d'entree pour l'assistant CLI
if __name__ == "__main__":
    manager = APIManager()
    manager.setup_wizard_cli()