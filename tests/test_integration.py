#!/usr/bin/env python3
"""Tests d'intégration pour SENTRAX"""

import unittest
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.email_reporter import EmailReporter
from src.core.scan_database import ScanDatabase
from src.core.export_manager import ExportManager

class TestIntegration(unittest.TestCase):
    """Tests d'intégration entre modules"""
    
    def setUp(self):
        self.db = ScanDatabase()
        self.test_results = {
            'target': 'test.com',
            'open_ports': [{'port': 80, 'service': 'http'}],
            'os': {'guess': 'Linux'}
        }
    
    def test_database_and_export_integration(self):
        """Test base données + export"""
        # Sauvegarder
        self.db.save_scan('test123', 'test.com', 'expert', self.test_results, 'completed')
        
        # Récupérer
        scan = self.db.get_scan('test123')
        self.assertIsNotNone(scan)
        
        # Exporter
        filename = ExportManager.export_json(scan, 'test_integration')
        self.assertTrue(os.path.exists(filename))
        
        # Nettoyer
        os.remove(filename)
    
    def test_email_config_loading(self):
        """Test chargement configuration email"""
        config_file = Path.home() / ".SENTRAX" / "test_email_config.json"
        config_data = {
            'enabled': False,
            'smtp_server': 'test.com',
            'username': 'test'
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        reporter = EmailReporter(config_file)
        self.assertEqual(reporter.config['smtp_server'], 'test.com')
        
        os.remove(config_file)

if __name__ == '__main__':
    print("="*60)
    print("🔗 TESTS D'INTEGRATION - SENTRAX")
    print("="*60)
    unittest.main(verbosity=2)