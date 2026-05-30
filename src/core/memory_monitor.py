#!/usr/bin/env python3
"""Moniteur de memoire pour SENTRAX"""

import tracemalloc
import threading
import time
from datetime import datetime

class MemoryMonitor:
    """Surveille la consommation memoire des scans"""
    
    def __init__(self):
        self.enabled = False
        self.peak = 0
        self.start_time = None
    
    def start(self):
        """Demarre le monitoring memoire"""
        tracemalloc.start()
        self.enabled = True
        self.start_time = datetime.now()
        print(f"[MEMORY] Monitoring started at {self.start_time}")
    
    def stop(self):
        """Arrete le monitoring memoire"""
        if self.enabled:
            tracemalloc.stop()
            self.enabled = False
            print(f"[MEMORY] Monitoring stopped")
    
    def get_usage(self):
        """Retourne l'utilisation memoire actuelle"""
        if not self.enabled:
            return None
        current, peak = tracemalloc.get_traced_memory()
        return {
            'current': current / 1024 / 1024,
            'peak': peak / 1024 / 1024
        }
    
    def log_usage(self):
        """Affiche l'utilisation memoire"""
        usage = self.get_usage()
        if usage:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            print(f"[MEMORY] Elapsed: {elapsed:.1f}s - Current: {usage['current']:.2f} MB, Peak: {usage['peak']:.2f} MB")
    
    def get_report(self):
        """Retourne un rapport complet"""
        usage = self.get_usage()
        if not usage:
            return "Memory monitor not active"
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return {
            'elapsed_seconds': elapsed,
            'current_mb': usage['current'],
            'peak_mb': usage['peak'],
            'timestamp': datetime.now().isoformat()
        }

# Instance globale
memory_monitor = MemoryMonitor()