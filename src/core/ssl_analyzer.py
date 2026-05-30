#!/usr/bin/env python3
"""Analyseur de certificats SSL/TLS"""

import socket
import ssl
from datetime import datetime

def analyze_certificate(host, port=443, timeout=5):
    """Analyse un certificat SSL et retourne les informations"""
    
    result = {
        'host': host,
        'port': port,
        'has_ssl': False,
        'error': None
    }
    
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                result['has_ssl'] = True
                
                # Extraire les informations
                result['subject'] = dict(cert.get('subject', []))
                result['issuer'] = dict(cert.get('issuer', []))
                result['version'] = cert.get('version')
                result['serial_number'] = cert.get('serialNumber')
                result['not_before'] = cert.get('notBefore')
                result['not_after'] = cert.get('notAfter')
                result['subject_alt_names'] = cert.get('subjectAltName', [])
                
                # Calculer expiration
                if result['not_after']:
                    expire_date = datetime.strptime(result['not_after'], '%b %d %H:%M:%S %Y %Z')
                    result['expires_in_days'] = (expire_date - datetime.now()).days
                    result['is_expired'] = result['expires_in_days'] < 0
                
                result['cipher'] = ssock.cipher()
                result['protocol'] = ssock.version()
                
    except socket.timeout:
        result['error'] = 'Connection timeout'
    except ssl.SSLError as e:
        result['error'] = f'SSL Error: {str(e)[:50]}'
    except Exception as e:
        result['error'] = str(e)[:100]
    
    return result

def get_certificate_summary(host, port=443):
    """Retourne un résumé du certificat"""
    cert = analyze_certificate(host, port)
    
    if not cert.get('has_ssl'):
        return "No SSL/TLS certificate found"
    
    summary = []
    
    # Nom commun
    subject = cert.get('subject', {})
    common_name = subject.get('commonName', ['Unknown'])[0]
    summary.append(f"Common Name: {common_name}")
    
    # Émetteur
    issuer = cert.get('issuer', {})
    issuer_name = issuer.get('organizationName', ['Unknown'])[0]
    summary.append(f"Issuer: {issuer_name}")
    
    # Expiration
    if 'expires_in_days' in cert:
        days = cert['expires_in_days']
        if days < 0:
            summary.append(f"Status: EXPIRED (expired {abs(days)} days ago)")
        elif days < 30:
            summary.append(f"Status: EXPIRES SOON in {days} days")
        else:
            summary.append(f"Status: Valid (expires in {days} days)")
    
    # SANs
    sans = cert.get('subject_alt_names', [])
    if sans:
        san_names = [name for _, name in sans[:5]]
        summary.append(f"Subject Alt Names: {', '.join(san_names)}")
    
    return '\n'.join(summary)