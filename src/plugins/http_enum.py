#!/usr/bin/env python3
"""Plugin d'énumération HTTP"""

import socket
from .base_plugin import BasePlugin

class HttpEnumPlugin(BasePlugin):
    """Énumère les chemins HTTP courants"""
    
    def __init__(self):
        super().__init__()
        self.name = "HTTP Enumeration"
        self.version = "1.0"
        self.author = "Patrick Ndaye"
        self.description = "Enumeration des chemins HTTP courants"
        self.applicable_ports = [80, 443, 8080, 8443]
        self.applicable_services = ['http', 'https']
        
        # Chemins courants à tester
        self.paths = [
            '/', '/admin', '/login', '/wp-admin', '/phpmyadmin',
            '/api', '/v1', '/docs', '/swagger', '/graphql'
        ]
    
    def run(self, target, port, banner=None):
        import requests
        protocol = 'https' if port in [443, 8443] else 'http'
        results = {'plugin': self.name, 'findings': []}
        
        for path in self.paths:
            try:
                url = f"{protocol}://{target}:{port}{path}"
                response = requests.get(url, timeout=3, verify=False)
                if response.status_code == 200:
                    results['findings'].append({
                        'url': url,
                        'status': response.status_code,
                        'title': self.extract_title(response.text)
                    })
            except:
                pass
        
        return results
    
    def extract_title(self, html):
        import re
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        return match.group(1)[:50] if match else 'No title'