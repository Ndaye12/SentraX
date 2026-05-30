#!/usr/bin/env python3
"""Tests unitaires avances pour SENTRAX"""

import unittest
import sys
import os
import socket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.network import (
    resolve_host, is_valid_ip, tcp_connect_scan,
    detect_os_enhanced, scan_ports_advanced
)
from src.core.cve_database import CVEDatabase
from src.core.export_manager import ExportManager

class TestAdvancedNetwork(unittest.TestCase):
    """Tests reseau avances"""
    
    def test_resolve_host(self):
        self.assertIsNotNone(resolve_host("google.com"))
        self.assertIsInstance(resolve_host("google.com"), str)
    
    def test_is_valid_ip(self):
        self.assertTrue(is_valid_ip("192.168.1.1"))
        self.assertTrue(is_valid_ip("8.8.8.8"))
        self.assertFalse(is_valid_ip("256.256.256.256"))
        self.assertFalse(is_valid_ip("not-an-ip"))
    
    def test_tcp_connect_scan(self):
        google_ip = resolve_host("google.com")
        if google_ip:
            is_open, info = tcp_connect_scan(google_ip, 80, timeout=2)
            self.assertTrue(is_open)
            self.assertIn("open", info.lower())
    
    def test_detect_os_enhanced(self):
        google_ip = resolve_host("google.com")
        if google_ip:
            os_info = detect_os_enhanced(google_ip)
            self.assertIn('primary_guess', os_info)
            self.assertIn('confidence', os_info)
            print(f"OS detection test: {os_info}")

class TestCVEDatabaseAdvanced(unittest.TestCase):
    """Tests CVE avances"""
    
    def setUp(self):
        self.cve_db = CVEDatabase()
    
    def test_check_vulnerabilities_ssh(self):
        vulns = self.cve_db.check_vulnerabilities(22)
        self.assertGreater(len(vulns), 0)
        for vuln in vulns:
            self.assertIn('cve_id', vuln)
            self.assertIn('severity', vuln)
    
    def test_check_vulnerabilities_http(self):
        vulns = self.cve_db.check_vulnerabilities(80)
        self.assertGreater(len(vulns), 0)
    
    def test_get_risk_level(self):
        self.assertEqual(self.cve_db.get_risk_level('CRITICAL'), '🔴 CRITIQUE')
        self.assertEqual(self.cve_db.get_risk_level('HIGH'), '🟠 ELEVE')
        self.assertEqual(self.cve_db.get_risk_level('MEDIUM'), '🟡 MOYEN')
        self.assertEqual(self.cve_db.get_risk_level('LOW'), '🟢 FAIBLE')

class TestExportManagerAdvanced(unittest.TestCase):
    """Tests export avances"""
    
    def setUp(self):
        self.test_results = {
            'target': 'test.com',
            'open_ports': [
                {'port': 80, 'service': 'http', 'banner': 'Apache/2.4.41'},
                {'port': 443, 'service': 'https', 'banner': 'nginx/1.18.0'}
            ],
            'os': {'guess': 'Linux/Unix'},
            'timestamp': '2024-01-01T00:00:00'
        }
    
    def tearDown(self):
        test_files = ['test_export.json', 'test_export.txt', 'test_export.csv', 'test_export.html']
        for f in test_files:
            if os.path.exists(f):
                os.remove(f)
    
    def test_export_json(self):
        filename = ExportManager.export_json(self.test_results, 'test_export')
        self.assertTrue(os.path.exists(filename))
        self.assertTrue(filename.endswith('.json'))
    
    def test_export_csv(self):
        filename = ExportManager.export_csv(self.test_results, 'test_export')
        self.assertTrue(os.path.exists(filename))
    
    def test_export_html(self):
        filename = ExportManager.export_html(self.test_results, 'test_export')
        self.assertTrue(os.path.exists(filename))
        self.assertTrue(filename.endswith('.html'))

def run_all_tests():
    print("="*60)
    print("🧪 SENTRAX - TESTS AUTOMATISES AVANCES")
    print("="*60)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedNetwork))
    suite.addTests(loader.loadTestsFromTestCase(TestCVEDatabaseAdvanced))
    suite.addTests(loader.loadTestsFromTestCase(TestExportManagerAdvanced))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print(f"📊 RESUME: {result.testsRun} tests, {len(result.failures)} echecs, {len(result.errors)} erreurs")
    print("="*60)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)