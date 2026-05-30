#!/usr/bin/env python3
"""Utilitaires reseau pour les scanners - Version Expert avec ICMP, UDP avance et OS detection amelioree"""

import socket
import ipaddress
import subprocess
import platform
import re
import os
from typing import Tuple, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

# ==================== SIGNATURES OS AVANCEES ====================

OS_SIGNATURES = {
    # Linux
    (64, 8192): "Linux 2.4/2.6 (ancien)",
    (64, 16384): "Linux 3.x/4.x",
    (64, 65535): "Linux (ancienne version)",
    (64, 5840): "Linux (embedded)",
    (64, 8760): "Android/Linux mobile",
    
    # Windows
    (128, 8192): "Windows 7/8/10 (ancien)",
    (128, 16384): "Windows 10/11 (moderne)",
    (128, 65535): "Windows (ancienne version)",
    (128, 8760): "Windows Server",
    
    # Unix/BSD
    (64, 16384): "FreeBSD/OpenBSD",
    (64, 65535): "FreeBSD (ancien)",
    (64, 5840): "MacOS X",
    (64, 8192): "Solaris",
    
    # Routeurs/Embarqués
    (255, 8192): "Cisco Router/IOS",
    (255, 16384): "Cisco Switch",
    (64, 8760): "Android",
    (64, 8192): "IoT Device",
}

def resolve_host(host: str) -> Optional[str]:
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None

def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_domain(domain: str) -> bool:
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))

def get_hostname(ip: str) -> Optional[str]:
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return None

def get_common_ports() -> List[int]:
    return [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
        993, 995, 1723, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017, 27018
    ]

def is_admin() -> bool:
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        try:
            return os.geteuid() == 0
        except:
            return False

# ==================== SCAN TCP ====================

def tcp_connect_scan(ip: str, port: int, timeout: float = 2.0) -> Tuple[bool, str]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            return True, "open"
        return False, "closed"
    except:
        return False, "error"

# ==================== SCAN SYN ====================

def syn_scan_port(ip: str, port: int, timeout: float = 2.0) -> Tuple[bool, str]:
    try:
        from scapy.all import IP, TCP, sr1, conf
        conf.verb = 0
        
        pkt = IP(dst=ip)/TCP(dport=port, flags="S")
        reply = sr1(pkt, timeout=timeout, verbose=0)
        
        if reply and reply.haslayer(TCP):
            flags = reply.getlayer(TCP).flags
            if flags == 0x12:
                rst = IP(dst=ip)/TCP(dport=port, flags="R")
                sr1(rst, timeout=1, verbose=0)
                return True, "open (SYN)"
            elif flags == 0x14:
                return False, "closed"
            else:
                return False, "filtered"
        return False, "filtered/no-response"
    except ImportError:
        return tcp_connect_scan(ip, port, timeout)
    except Exception:
        return tcp_connect_scan(ip, port, timeout)

# ==================== SCAN UDP ====================

def udp_scan_port(ip: str, port: int, timeout: float = 2) -> Tuple[bool, str]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        sock.sendto(b'', (ip, port))
        try:
            data, addr = sock.recvfrom(1024)
            sock.close()
            if data:
                return True, "open (UDP)"
        except socket.timeout:
            sock.close()
            return True, "open|filtered (UDP)"
        except ConnectionRefusedError:
            sock.close()
            return False, "closed"
    except Exception:
        return False, "error"
    return False, "unknown"

# ==================== SCAN UDP AVANCE ====================

def scan_udp_advanced(ip: str, ports: List[int], timeout: float = 2, max_threads: int = 50) -> List[dict]:
    results = []
    
    udp_probes = {
        53: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        67: b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        69: b'\x00\x01test\x00netascii\x00',
        123: b'\x1b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        137: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        161: b'\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        500: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        514: b'Hello\0',
        520: b'\x00\x00\x00\x00\x00\x00\x00\x00',
        1701: b'\x00\x00\x00\x00\x00\x00\x00\x00',
        1812: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        1900: b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 1\r\nST: ssdp:all\r\n\r\n',
        5353: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        33434: b'\x00\x00\x00\x00\x00\x00\x00\x00',
    }
    
    def scan_single(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            if port in udp_probes:
                sock.sendto(udp_probes[port], (ip, port))
            else:
                sock.sendto(b'\x00', (ip, port))
            
            try:
                data, addr = sock.recvfrom(1024)
                sock.close()
                if data:
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = "unknown"
                    
                    try:
                        banner = data[:200].decode('utf-8', errors='ignore')
                    except:
                        banner = str(data[:100])
                    
                    return {
                        'port': port, 
                        'service': service, 
                        'protocol': 'UDP', 
                        'status': 'open',
                        'banner': banner
                    }
            except socket.timeout:
                sock.close()
                return None
            except:
                sock.close()
                return None
        except:
            return None
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(scan_single, port): port for port in ports}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    
    return results

# ==================== SCAN ICMP ====================

def icmp_ping(ip: str, timeout: float = 2) -> bool:
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-w', str(int(timeout * 1000)), ip]
    
    try:
        result = subprocess.run(command, capture_output=True, timeout=timeout + 1)
        return result.returncode == 0
    except:
        return False

def icmp_ping_advanced(ip: str, timeout: float = 2) -> dict:
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-w', str(int(timeout * 1000)), ip]
    
    try:
        result = subprocess.run(command, capture_output=True, timeout=timeout + 1)
        output = result.stdout.decode('utf-8', errors='ignore')
        
        response_time = None
        patterns = [r'time[=<](\d+)[ms]', r'temps[=<](\d+)[ms]', r'(\d+)ms']
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                response_time = int(match.group(1))
                break
        
        return {
            'alive': result.returncode == 0,
            'response_time': response_time,
            'output': output[:200]
        }
    except:
        return {'alive': False, 'response_time': None, 'output': ''}

def discover_network(network: str, timeout: float = 1) -> List[str]:
    try:
        active_hosts = []
        network_obj = ipaddress.ip_network(network, strict=False)
        
        def scan_host(ip):
            if icmp_ping(str(ip), timeout):
                return str(ip)
            return None
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(scan_host, ip): ip for ip in network_obj.hosts()}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    active_hosts.append(result)
        
        return active_hosts
    except:
        return []

def discover_network_advanced(network: str, timeout: float = 1) -> List[dict]:
    import ipaddress
    active_hosts = []
    network_obj = ipaddress.ip_network(network, strict=False)
    
    def scan_host(ip):
        result = icmp_ping_advanced(str(ip), timeout)
        if result['alive']:
            return {'ip': str(ip), 'response_time': result['response_time']}
        return None
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(scan_host, ip): ip for ip in network_obj.hosts()}
        for future in as_completed(futures):
            result = future.result()
            if result:
                active_hosts.append(result)
    
    return active_hosts

def quick_discover(ip_range: str) -> List[str]:
    active_hosts = []
    try:
        if '/' in ip_range:
            active_hosts = discover_network(ip_range)
        elif '-' in ip_range:
            parts = ip_range.split('.')
            if len(parts) == 4:
                last_part = parts[3].split('-')
                if len(last_part) == 2:
                    start = int(last_part[0])
                    end = int(last_part[1])
                    base_ip = '.'.join(parts[:3])
                    
                    def scan_ip(i):
                        ip = f"{base_ip}.{i}"
                        if icmp_ping(ip, 1):
                            return ip
                        return None
                    
                    with ThreadPoolExecutor(max_workers=50) as executor:
                        futures = {executor.submit(scan_ip, i): i for i in range(start, end + 1)}
                        for future in as_completed(futures):
                            result = future.result()
                            if result:
                                active_hosts.append(result)
    except:
        pass
    return active_hosts

# ==================== BANNER GRABBING ====================

def grab_banner_advanced(ip: str, port: int, timeout: float = 2) -> dict:
    probes = {
        21: b"USER anonymous\r\n",
        22: b"SSH-2.0-SENTRAX\r\n",
        25: b"EHLO test.com\r\n",
        80: b"HEAD / HTTP/1.0\r\nHost: example.com\r\n\r\n",
        110: b"USER test\r\n",
        143: b"A001 CAPABILITY\r\n",
        443: b"HEAD / HTTP/1.0\r\nHost: example.com\r\n\r\n",
        3306: b"\x00\x00\x00\x0a\x85\xa2\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        5432: b"\x00\x00\x00\x08\x04\xd2\x16\x2f",
        6379: b"INFO\r\n",
        27017: b"\x48\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\xd4\x07\x00\x00\x00\x01\x00\x00\x00",
    }
    
    result = {'port': port, 'banner': None, 'service': None, 'version': None, 'os': None}
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        
        if port in probes:
            sock.send(probes[port])
        
        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        sock.close()
        
        result['banner'] = banner[:200]
        
        try:
            result['service'] = socket.getservbyport(port)
        except:
            result['service'] = "unknown"
        
        ssh_match = re.search(r'SSH-([0-9.]+)', banner)
        if ssh_match:
            result['version'] = f"SSH {ssh_match.group(1)}"
        
        openssh_match = re.search(r'OpenSSH[_\s]([0-9.]+)', banner)
        if openssh_match:
            result['version'] = f"OpenSSH {openssh_match.group(1)}"
        
        if 'Linux' in banner:
            result['os'] = "Linux"
        elif 'Windows' in banner:
            result['os'] = "Windows"
        
    except Exception:
        pass
    
    return result

# ==================== DETECTION OS AMELIOREE ====================

def detect_os_by_tcp_window(ip: str, port: int = 80) -> dict:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))
        
        ttl = sock.getsockopt(socket.IPPROTO_IP, socket.IP_TTL)
        window_size = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        sock.close()
        
        os_guess = OS_SIGNATURES.get((ttl, window_size), "Unknown")
        confidence = 'high' if (ttl, window_size) in OS_SIGNATURES else 'low'
        
        return {'os': os_guess, 'ttl': ttl, 'window_size': window_size, 'confidence': confidence}
    except:
        return {'os': 'Unknown', 'ttl': None, 'window_size': None, 'confidence': 'low'}

def detect_os_by_banner(ip: str, port: int = 22) -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))
        sock.send(b"SSH-2.0-SENTRAX\r\n")
        banner = sock.recv(256).decode('utf-8', errors='ignore')
        sock.close()
        
        if 'Ubuntu' in banner:
            return 'Ubuntu Linux'
        elif 'Debian' in banner:
            return 'Debian Linux'
        elif 'CentOS' in banner or 'Red Hat' in banner:
            return 'Red Hat/CentOS Linux'
        elif 'FreeBSD' in banner:
            return 'FreeBSD'
        elif 'OpenBSD' in banner:
            return 'OpenBSD'
        elif 'Windows' in banner:
            return 'Windows (OpenSSH)'
        else:
            return 'Linux/Unix (generic)'
    except:
        return 'Unknown'

def detect_os_by_ttl(ip: str) -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.connect((ip, 33434))
        ttl = sock.getsockopt(socket.IPPROTO_IP, socket.IP_TTL)
        sock.close()
        
        if ttl <= 64:
            return "Linux/Unix"
        elif ttl <= 128:
            return "Windows"
        elif ttl <= 255:
            return "Router/Cisco"
        else:
            return f"Unknown (TTL={ttl})"
    except:
        return "Unable to determine"

def detect_os_by_window_size(ip: str, port: int = 80) -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((ip, port))
        window_size = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        sock.close()
        
        if window_size == 8192:
            return "Windows 10/11"
        elif window_size == 16384:
            return "Linux (moderne)"
        elif window_size == 8760:
            return "Windows 7/8"
        elif window_size == 5840:
            return "MacOS / BSD"
        elif window_size == 65535:
            return "Linux (ancien)"
        else:
            return f"Window={window_size}"
    except:
        return "Unknown"

def detect_os_advanced(ip: str) -> dict:
    ttl_result = detect_os_by_ttl(ip)
    window_result = detect_os_by_window_size(ip)
    
    if "Windows" in window_result:
        os_guess = window_result
    elif "Linux" in ttl_result:
        os_guess = ttl_result
    else:
        os_guess = f"{ttl_result} / {window_result}"
    
    return {'guess': os_guess, 'ttl': ttl_result, 'window': window_result}

def detect_os_enhanced(ip: str) -> dict:
    result = {
        'primary_guess': 'Unknown',
        'confidence': 'low',
        'details': {}
    }
    
    tcp_result = detect_os_by_tcp_window(ip)
    result['details']['tcp_analysis'] = tcp_result
    
    ssh_os = detect_os_by_banner(ip)
    result['details']['ssh_banner'] = ssh_os
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, 80))
        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        response = sock.recv(512).decode('utf-8', errors='ignore')
        sock.close()
        
        if 'Server: ' in response:
            server_line = [l for l in response.split('\n') if 'Server:' in l]
            if server_line:
                result['details']['http_server'] = server_line[0].strip()
    except:
        pass
    
    if tcp_result.get('confidence') == 'high':
        result['primary_guess'] = tcp_result['os']
        result['confidence'] = 'high'
    elif ssh_os != 'Unknown':
        result['primary_guess'] = ssh_os
        result['confidence'] = 'medium'
    else:
        result['primary_guess'] = tcp_result.get('os', 'Unknown')
        result['confidence'] = 'low'
    
    return result

# ==================== SCAN AVANCE MULTI-THREAD ====================

def scan_ports_advanced(ip: str, ports: List[int], scan_type: str = "tcp", 
                        timeout: float = 1, max_threads: int = 100) -> List[dict]:
    results = []
    use_syn = (scan_type == "syn" and is_admin())
    
    def scan_single(port):
        if use_syn:
            is_open, info = syn_scan_port(ip, port, timeout)
        else:
            is_open, info = tcp_connect_scan(ip, port, timeout)
        
        if is_open:
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"
            return {'port': port, 'service': service, 'status': 'open', 'method': info}
        return None
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(scan_single, port): port for port in ports}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    
    return results

def scan_udp_ports(ip: str, ports: List[int], timeout: float = 2, max_threads: int = 50) -> List[dict]:
    results = []
    
    def scan_single(port):
        is_open, info = udp_scan_port(ip, port, timeout)
        if is_open:
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"
            return {'port': port, 'service': service, 'status': 'open', 'protocol': 'UDP', 'info': info}
        return None
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(scan_single, port): port for port in ports}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    
    return results

def get_local_ip() -> Optional[str]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

def ping_host(ip: str) -> bool:
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip]
    try:
        result = subprocess.run(command, capture_output=True, timeout=3)
        return result.returncode == 0
    except:
        return False

def detect_service_version(ip: str, port: int, service: str, timeout: float = 3) -> dict:
    result = {'port': port, 'service': service, 'banner': None, 'version': None, 'os': None, 'details': {}}
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        
        if service.lower() == 'http':
            sock.send(b'HEAD / HTTP/1.0\r\nHost: example.com\r\n\r\n')
        elif service.lower() == 'ssh':
            sock.send(b'SSH-2.0-SENTRAX\r\n')
        else:
            sock.send(b'\r\n')
        
        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        sock.close()
        
        result['banner'] = banner[:200]
        
        ssh_match = re.search(r'SSH-([0-9.]+)', banner)
        if ssh_match:
            result['version'] = f"SSH {ssh_match.group(1)}"
        
        openssh_match = re.search(r'OpenSSH[_\s]([0-9.]+)', banner)
        if openssh_match:
            result['version'] = f"OpenSSH {openssh_match.group(1)}"
        
        if 'Linux' in banner:
            result['os'] = 'Linux'
        elif 'Windows' in banner:
            result['os'] = 'Windows'
        
    except Exception:
        pass
    
    return result

# ==================== CACHE DNS ====================

@lru_cache(maxsize=100)
def resolve_host_cached(host: str):
    """Resolution DNS avec cache pour meilleures performances"""
    try:
        return socket.gethostbyname(host)
    except:
        return None

def clear_dns_cache():
    """Vide le cache DNS"""
    resolve_host_cached.cache_clear()
    print("[DNS] Cache cleared")