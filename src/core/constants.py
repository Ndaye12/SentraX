#!/usr/bin/env python3
"""Constantes globales pour SENTRAX"""

# ==================== PORTS ====================
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
                993, 995, 1723, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017, 27018]

FAST_SCAN_PORTS = [22, 80, 443, 8080, 8443, 3306, 3389]

UDP_COMMON_PORTS = [53, 67, 68, 123, 137, 138, 161, 162, 500, 514, 520, 631, 1900, 5353]

# ==================== TIMEOUTS ====================
TCP_TIMEOUT = 2.0
UDP_TIMEOUT = 2.0
SYN_TIMEOUT = 2.0
ICMP_TIMEOUT = 2.0
DNS_TIMEOUT = 3.0

# ==================== THREADS ====================
MAX_THREADS_TCP = 100
MAX_THREADS_UDP = 50
MAX_THREADS_DISCOVER = 100
MAX_THREADS_QUICK = 50

# ==================== API ====================
JWT_EXPIRATION_HOURS = 8
RATE_LIMIT_PER_HOUR = 50
RATE_LIMIT_PER_DAY = 200
API_VERSION = "3.1.0"

# ==================== SCANNERS ====================
SCANNERS_COUNT = 10
SCANNERS_LIST = ['ai', 'osint', 'p2p', 'passive', 'timemachine', 
                 'holo', 'expert', 'ultra', 'snmp', 'dns']

SCANNERS_NAMES = {
    'ai': 'AI Predictive Scanner',
    'osint': 'OSINT Scanner',
    'p2p': 'P2P Scanner',
    'passive': 'Passive Scanner',
    'timemachine': 'Time Machine Scanner',
    'holo': 'Holographic Radar',
    'expert': 'Expert Scanner PRO',
    'ultra': 'Ultra Scanner PRO',
    'snmp': 'SNMP Scanner',
    'dns': 'DNS Scanner'
}

# ==================== CHEMINS ====================
DATA_DIR = "data"
LOGS_DIR = "logs"
ASSETS_DIR = "assets"
ICONS_DIR = "assets/icons"

# ==================== COULEURS ====================
COLORS = {
    'primary': '#00ff88',
    'secondary': '#00aaff',
    'warning': '#ffaa00',
    'danger': '#ff4444',
    'info': '#00ffff',
    'dark': '#0a0a0a',
    'light': '#f0f0f0',
    'card': '#1a1a1a'
}