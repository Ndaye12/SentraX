#!/usr/bin/env python3
"""Tests de sécurité pour SENTRAX"""

import unittest
import sys
import os
import socket
import jwt
import bcrypt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.network import is_admin, syn_scan_port, tcp_connect_scan

class TestSecurity(unittest.TestCase):
    """Tests de sécurité des scanners"""
    
    def test_syn_scan_fallback(self):
        """Test que SYN scan tombe correctement sur TCP scan si scapy absent"""
        result, info = syn_scan_port("8.8.8.8", 53, timeout=1)
        # Le résultat peut être True ou False, mais ne doit pas planter
        self.assertIsInstance(result, bool)
    
    def test_tcp_connect_timeout(self):
        """Test que le timeout fonctionne"""
        import time
        start = time.time()
        result, info = tcp_connect_scan("192.0.2.1", 9999, timeout=1)
        elapsed = time.time() - start
        self.assertLess(elapsed, 2)
        self.assertFalse(result)
    
    def test_is_admin_check(self):
        """Test de vérification admin (ne doit pas planter)"""
        admin = is_admin()
        self.assertIsInstance(admin, bool)

class TestInputValidation(unittest.TestCase):
    """Tests de validation des entrées"""
    
    def test_target_validation(self):
        targets = ["scanme.nmap.org", "google.com", "8.8.8.8", "192.168.1.1"]
        for target in targets:
            try:
                ip = socket.gethostbyname(target)
                self.assertIsNotNone(ip)
            except:
                self.fail(f"Failed to resolve {target}")
    
    def test_invalid_target(self):
        """Test avec cible invalide"""
        with self.assertRaises(socket.gaierror):
            socket.gethostbyname("this-domain-does-not-exist-123456.xyz")

class TestPerformance(unittest.TestCase):
    """Tests de performance"""
    
    def test_scan_speed(self):
        """Test que le scan est raisonnablement rapide"""
        import time
        ip = "8.8.8.8"
        ports = [80, 443, 53]
        
        start = time.time()
        for port in ports:
            tcp_connect_scan(ip, port, timeout=1)
        elapsed = time.time() - start
        
        # Doit prendre moins de 5 secondes
        self.assertLess(elapsed, 5)
    
    def test_concurrent_scans(self):
        """Test des scans concurrents"""
        from concurrent.futures import ThreadPoolExecutor
        
        def scan_port(port):
            return tcp_connect_scan("8.8.8.8", port, timeout=1)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(scan_port, [80, 443, 53, 22, 25]))
            self.assertEqual(len(results), 5)

class TestAuthentication(unittest.TestCase):
    """Tests d'authentification"""
    
    def test_password_hashing(self):
        """Test que les mots de passe sont bien hashés"""
        password = "test123"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.assertTrue(bcrypt.checkpw(password.encode(), hashed))
        self.assertFalse(bcrypt.checkpw("wrong".encode(), hashed))
    
    def test_jwt_token(self):
        """Test la génération de tokens JWT"""
        token = jwt.encode({'user': 'test'}, 'secret', algorithm='HS256')
        decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
        self.assertEqual(decoded['user'], 'test')
    
    def test_invalid_jwt(self):
        """Test token invalide"""
        with self.assertRaises(jwt.InvalidTokenError):
            jwt.decode('invalid', 'secret', algorithms=['HS256'])

if __name__ == '__main__':
    print("="*60)
    print("🔒 TESTS DE SECURITE - SENTRAX")
    print("="*60)
    unittest.main(verbosity=2)