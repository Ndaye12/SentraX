#!/usr/bin/env python3
"""Moteur de scripts personnalisables"""

import os
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Any, List

class ScriptEngine:
    """Moteur d'execution de scripts personnalises"""
    
    def __init__(self):
        self.scripts_dir = Path(__file__).parent.parent.parent / "scripts" / "custom"
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        self.scripts = {}
        self.load_scripts()
    
    def load_scripts(self):
        """Charge tous les scripts du dossier"""
        for script_file in self.scripts_dir.glob("*.py"):
            if script_file.name != "__init__.py":
                self.load_script(script_file)
    
    def load_script(self, script_path: Path):
        """Charge un script specifique"""
        try:
            spec = importlib.util.spec_from_file_location(
                script_path.stem, script_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Cherche la fonction main ou scan
            if hasattr(module, 'scan'):
                self.scripts[script_path.stem] = {
                    'name': script_path.stem,
                    'function': module.scan,
                    'description': module.__doc__ or "No description",
                    'path': script_path
                }
            elif hasattr(module, 'main'):
                self.scripts[script_path.stem] = {
                    'name': script_path.stem,
                    'function': module.main,
                    'description': module.__doc__ or "No description",
                    'path': script_path
                }
        except Exception as e:
            print(f"Error loading script {script_path}: {e}")
    
    def create_template_script(self, name: str) -> str:
        """Cree un template de script"""
        template = f'''#!/usr/bin/env python3
"""
{name} - Script personnalise pour SENTRAX AI Suite

Ce script est execute par le moteur de scripts.
La fonction main(ip, ports, results) est appelee avec les resultats du scan.
"""

def scan(ip: str, ports: list, results: dict) -> dict:
    """
    Fonction principale du script
    
    Args:
        ip: Adresse IP cible
        ports: Liste des ports scannes
        results: Resultats du scan {{
            'open_ports': [...],
            'os_guess': '...',
            'banners': [...]
        }}
    
    Returns:
        dict: Resultats du script
    """
    print(f"Execution du script {name} sur {ip}")
    
    # Ajoutez votre logique ici
    custom_results = {{
        'script_name': '{name}',
        'target': ip,
        'analysis': []
    }}
    
    # Exemple: Analyse des ports ouverts
    for port_info in results.get('open_ports', []):
        port = port_info['port']
        service = port_info['service']
        
        # Ajoutez votre analyse
        custom_results['analysis'].append({{
            'port': port,
            'service': service,
            'finding': f"Analyse du port {port} ({service})"
        }})
    
    return custom_results

if __name__ == "__main__":
    # Test du script
    test_results = scan("127.0.0.1", [80, 443], {{'open_ports': []}})
    print(test_results)
'''
        
        script_path = self.scripts_dir / f"{name}.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return str(script_path)
    
    def execute_script(self, script_name: str, ip: str, ports: List[int], scan_results: Dict) -> Dict:
        """Execute un script et retourne les resultats"""
        if script_name not in self.scripts:
            return {'error': f"Script {script_name} not found"}
        
        try:
            script = self.scripts[script_name]
            result = script['function'](ip, ports, scan_results)
            return result
        except Exception as e:
            return {'error': str(e), 'script': script_name}
    
    def list_scripts(self) -> List[Dict]:
        """Liste tous les scripts disponibles"""
        return [
            {
                'name': name,
                'description': info['description'],
                'path': str(info['path'])
            }
            for name, info in self.scripts.items()
        ]
    
    def delete_script(self, script_name: str) -> bool:
        """Supprime un script"""
        if script_name in self.scripts:
            script_path = self.scripts[script_name]['path']
            try:
                os.remove(script_path)
                del self.scripts[script_name]
                return True
            except:
                pass
        return False

# Exemple de script integre
SCRIPT_EXAMPLE = '''
def scan(ip, ports, results):
    """Detection de faiblesses courantes"""
    findings = []
    
    for port_info in results.get('open_ports', []):
        port = port_info['port']
        
        if port == 22:
            findings.append("SSH ouvert - Verifier l'utilisation de cles fortes")
        elif port == 80:
            findings.append("HTTP ouvert - Verifier la configuration HTTPS")
        elif port == 3389:
            findings.append("RDP ouvert - Risque eleve, verifier les ACLs")
        elif port == 3306:
            findings.append("MySQL ouvert - Verifier l'absence de mots de passe par defaut")
    
    return {
        'script_name': 'security_check',
        'findings': findings,
        'risk_level': 'HIGH' if len(findings) > 2 else 'MEDIUM'
    }
'''

# Singleton
script_engine = ScriptEngine()