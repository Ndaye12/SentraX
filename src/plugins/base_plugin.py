#!/usr/bin/env python3
"""Classe de base pour tous les plugins"""

from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """Classe abstraite pour les plugins"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0"
        self.author = "Unknown"
        self.description = "No description"
    
    @abstractmethod
    def run(self, target, port, banner=None):
        """
        Exécute le plugin sur une cible
        
        Args:
            target: IP ou domaine
            port: Port cible
            banner: Bannière du service (optionnel)
        
        Returns:
            dict: Résultats du plugin
        """
        pass
    
    def get_info(self):
        """Retourne les informations du plugin"""
        return {
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'description': self.description
        }