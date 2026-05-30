#!/usr/bin/env python3
"""Plugin de détection OS via SMB"""

import socket
from .base_plugin import BasePlugin

class SMBOSPlugin(BasePlugin):
    """Détecte l'OS via les informations SMB"""
    
    def __init__(self):
        super().__init__()
        self.name = "SMB OS Detection"
        self.version = "1.0"
        self.author = "Patrick Ndaye"
        self.description = "Detection OS via SMB"
        self.applicable_ports = [139, 445]
        self.applicable_services = ['netbios-ssn', 'microsoft-ds']
    
    def run(self, target, port, banner=None):
        results = {'plugin': self.name, 'os_guess': None, 'details': {}}
        
        try:
            # Tentative de connexion SMB simple
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((target, port))
            
            # Envoi d'une requête SMB simple
            # (simplifié - en vrai utiliser impacket ou pysmb)
            sock.send(b'\x00\x00\x00\x00\x00\x00\x00\x00')
            data = sock.recv(256)
            sock.close()
            
            if b'Windows' in data:
                results['os_guess'] = 'Windows'
            elif b'Linux' in data:
                results['os_guess'] = 'Linux'
            elif b'Samba' in data:
                results['os_guess'] = 'Linux (Samba)'
            
            results['details']['banner'] = data[:100].decode('utf-8', errors='ignore')
            
        except Exception as e:
            results['error'] = str(e)
        
        return results