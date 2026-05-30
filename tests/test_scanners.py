#!/usr/bin/env python3
"""Tests unitaires pour SENTRAX AI Suite - Version robuste"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.network import (
    resolve_host, is_valid_ip, get_common_ports, tcp_connect_scan
)
from src.core.cve_database import CVEDatabase
from src.core.export_manager import ExportManager

class TestNetwork(unittest.TestCase):
    """Tests des fonctions reseau"""
    
    def test_resolve_host(self):
        """Test resolution DNS"""
        # Test avec un domaine valide
        google_ip = resolve_host("google.com")
        self.assertIsNotNone(google_ip)
        self.assertTrue(is_valid_ip(google_ip))
        
        # Test avec un domaine invalide (peut etre redirige par certains FAI)
        invalid_result = resolve_host("ceci-est-un-domaine-invalide-tres-long-123456.xyz")
        # On accepte None ou une IP (certains FAI redirigent vers une page publicitaire)
        # On vérifie juste que la fonction ne plante pas
        self.assertTrue(invalid_result is None or isinstance(invalid_result, str))
    
    def test_is_valid_ip(self):
        """Test validation IP"""
        self.assertTrue(is_valid_ip("192.168.1.1"))
        self.assertTrue(is_valid_ip("8.8.8.8"))
        self.assertTrue(is_valid_ip("127.0.0.1"))
        self.assertFalse(is_valid_ip("256.256.256.256"))
        self.assertFalse(is_valid_ip("not-an-ip"))
        self.assertFalse(is_valid_ip(""))
    
    def test_get_common_ports(self):
        """Test liste des ports communs"""
        ports = get_common_ports()
        self.assertIn(80, ports)
        self.assertIn(443, ports)
        self.assertIn(22, ports)
        self.assertGreater(len(ports), 20)
    
    def test_tcp_connect_scan(self):
        """Test scan TCP"""
        # Test sur google.com (port 80 doit etre ouvert)
        google_ip = resolve_host("google.com")
        if google_ip:
            is_open, info = tcp_connect_scan(google_ip, 80, timeout=2)
            self.assertTrue(is_open)
            self.assertIn("open", info.lower())

class TestCVEDatabase(unittest.TestCase):
    """Tests de la base CVE"""
    
    def setUp(self):
        self.cve_db = CVEDatabase()
    
    def test_check_vulnerabilities(self):
        """Test verification vulnerabilites"""
        # Test sur le port SSH (22)
        vulns = self.cve_db.check_vulnerabilities(22)
        self.assertGreater(len(vulns), 0)
        
        for vuln in vulns:
            self.assertIn('cve_id', vuln)
            self.assertIn('severity', vuln)
            self.assertIn('name', vuln)
        
        # Test sur un port sans vulnerabilite connue
        vulns_unknown = self.cve_db.check_vulnerabilities(9999)
        self.assertEqual(len(vulns_unknown), 0)
    
    def test_get_risk_level(self):
        """Test conversion niveau de risque"""
        self.assertEqual(self.cve_db.get_risk_level('CRITICAL'), '🔴 CRITIQUE')
        self.assertEqual(self.cve_db.get_risk_level('HIGH'), '🟠 ELEVE')
        self.assertEqual(self.cve_db.get_risk_level('MEDIUM'), '🟡 MOYEN')
        self.assertEqual(self.cve_db.get_risk_level('LOW'), '🟢 FAIBLE')
        self.assertEqual(self.cve_db.get_risk_level('UNKNOWN'), '⚪ INCONNU')

class TestExportManager(unittest.TestCase):
    """Tests d'export"""
    
    def setUp(self):
        self.test_results = {
            'target': 'test.com',
            'open_ports': [
                {'port': 80, 'service': 'http', 'banner': 'Apache/2.4.41', 'status': 'open'},
                {'port': 443, 'service': 'https', 'banner': 'nginx/1.18.0', 'status': 'open'}
            ],
            'os': {'guess': 'Linux/Unix'},
            'timestamp': '2024-01-01T00:00:00'
        }
    
    def tearDown(self):
        """Nettoie les fichiers de test"""
        test_files = ['test_export.json', 'test_export.txt', 'test_export.csv', 'test_export.html']
        for f in test_files:
            if os.path.exists(f):
                os.remove(f)
    
    def test_export_json(self):
        """Test export JSON"""
        filename = ExportManager.export_json(self.test_results, 'test_export')
        self.assertTrue(os.path.exists(filename))
        self.assertTrue(filename.endswith('.json'))
        
        # Verifie le contenu
        import json
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('metadata', data)
            self.assertIn('results', data)
    
    def test_export_txt(self):
        """Test export TXT"""
        filename = ExportManager.export_txt(self.test_results, 'test_export')
        self.assertTrue(os.path.exists(filename))
        self.assertTrue(filename.endswith('.txt'))
        
        # Verifie le contenu
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('test.com', content)
            self.assertIn('80', content)
    
    def test_export_csv(self):
        """Test export CSV"""
        filename = ExportManager.export_csv(self.test_results, 'test_export')
        self.assertTrue(os.path.exists(filename))
        self.assertTrue(filename.endswith('.csv'))
    
    def test_export_html(self):
        """Test export HTML"""
        filename = ExportManager.export_html(self.test_results, 'test_export')
        self.assertTrue(os.path.exists(filename))
        self.assertTrue(filename.endswith('.html'))
        
        # Verifie le contenu
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('<!DOCTYPE html>', content)
            self.assertIn('SENTRAX AI Suite', content)

def run_tests():
    """Execute tous les tests"""
    print("="*60)
    print("🧪 EXECUTION DES TESTS UNITAIRES - SENTRAX AI SUITE")
    print("="*60)
    print()
    
    # Charger les tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestNetwork))
    suite.addTests(loader.loadTestsFromTestCase(TestCVEDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestExportManager))
    
    # Executer
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("="*60)
    print(f"📊 RESUME DES TESTS")
    print("="*60)
    print(f"  Tests executes: {result.testsRun}")
    print(f"  Reussis: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Echecs: {len(result.failures)}")
    print(f"  Erreurs: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)