#!/usr/bin/env python3
"""Moteur de chargement et d'exécution des plugins"""

import os
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any

class PluginEngine:
    """Moteur de gestion des plugins"""
    
    def __init__(self):
        self.plugins_dir = Path(__file__).parent
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self):
        """Charge tous les plugins du dossier"""
        for file in self.plugins_dir.glob("*.py"):
            if file.name in ['__init__.py', 'base_plugin.py', 'plugin_engine.py']:
                continue
            
            module_name = f"src.plugins.{file.stem}"
            try:
                module = importlib.import_module(module_name)
                
                # Chercher les classes qui héritent de BasePlugin
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    from .base_plugin import BasePlugin
                    if issubclass(obj, BasePlugin) and obj != BasePlugin:
                        plugin = obj()
                        self.plugins[plugin.name] = plugin
                        print(f"[PLUGIN] Chargé: {plugin.name}")
            except Exception as e:
                print(f"[PLUGIN] Erreur chargement {file.name}: {e}")
    
    def list_plugins(self) -> List[Dict]:
        """Liste tous les plugins disponibles"""
        return [p.get_info() for p in self.plugins.values()]
    
    def run_plugin(self, plugin_name: str, target: str, port: int, banner: str = None) -> Dict:
        """Exécute un plugin spécifique"""
        if plugin_name not in self.plugins:
            return {'error': f'Plugin {plugin_name} not found'}
        
        try:
            return self.plugins[plugin_name].run(target, port, banner)
        except Exception as e:
            return {'error': str(e), 'plugin': plugin_name}
    
    def run_all_plugins(self, target: str, port: int, service: str, banner: str = None) -> List[Dict]:
        """Exécute tous les plugins applicables"""
        results = []
        for name, plugin in self.plugins.items():
            # Vérifier si le plugin correspond au service
            if hasattr(plugin, 'applicable_ports'):
                if port not in getattr(plugin, 'applicable_ports', []):
                    continue
            if hasattr(plugin, 'applicable_services'):
                if service.lower() not in [s.lower() for s in getattr(plugin, 'applicable_services', [])]:
                    continue
            
            result = self.run_plugin(name, target, port, banner)
            if result and not result.get('error'):
                results.append(result)
        
        return results