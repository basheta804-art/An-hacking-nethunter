#!/data/data/com.termux/files/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AN Hacking Toolkit - NetHunter Rootless Edition
Compatible with: Termux, Kali NetHunter Rootless, Android
Version: 2.0-nethunter

Features optimized for non-root Android:
- TCP Connect scans (no SYN scan, needs root)
- Python-based tools (no compilation needed)
- Lightweight operations (memory efficient)
- Offline capable modules
"""

import subprocess
import sys
import os
import json
import socket
import ssl
import urllib.request
import urllib.error
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
import threading
import time

# Color codes for terminal output
COLORS = {
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'MAGENTA': '\033[95m',
    'END': '\033[0m',
    'BOLD': '\033[1m'
}

def print_color(text: str, color: str = 'GREEN'):
    """Print colored text"""
    print(f"{COLORS.get(color, '')}{text}{COLORS['END']}")

class NetHunterEnvironment:
    """Detect and manage NetHunter/Termux environment"""
    
    def __init__(self):
        self.is_termux = self._check_termux()
        self.is_nethunter = self._check_nethunter()
        self.has_root = self._check_root()
        self.arch = self._get_arch()
        self.storage_path = self._get_storage_path()
        
    def _check_termux(self) -> bool:
        return os.path.exists("/data/data/com.termux")
    
    def _check_nethunter(self) -> bool:
        try:
            result = subprocess.run(["which", "nethunter"], 
                                capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_root(self) -> bool:
        try:
            result = subprocess.run(["id", "-u"], 
                                capture_output=True, text=True)
            return result.stdout.strip() == "0"
        except:
            return False
    
    def _get_arch(self) -> str:
        try:
            result = subprocess.run(["uname", "-m"], 
                                capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_storage_path(self) -> str:
        if self.is_termux:
            return "/data/data/com.termux/files/home"
        return os.path.expanduser("~")
    
    def print_info(self):
        """Print environment information"""
        print_color("\n[*] Environment Detection:", "CYAN")
        print_color(f"    Termux: {'Yes' if self.is_termux else 'No'}")
        print_color(f"    NetHunter: {'Yes' if self.is_nethunter else 'No'}")
        print_color(f"    Root Access: {'Yes' if self.has_root else 'No (Rootless)'}")
        print_color(f"    Architecture: {self.arch}")
        print_color(f"    Storage: {self.storage_path}\n")

class NetworkScanner:
    """Network scanner optimized for NetHunter Rootless"""
    
    def __init__(self, env: NetHunterEnvironment):
        self.env = env
        self.results = []
        
    def tcp_connect_scan(self, target: str, ports: List[int]) -> List[Dict]:
        """
        TCP Connect scan - works without root
        Alternative to SYN scan which requires root
        """
        open_ports = []
        
        def check_port(port: int) -> Optional[Dict]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((target, port))
                if result == 0:
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = "unknown"
                    return {"port": port, "service": service, "state": "open"}
                sock.close()
            except:
                pass
            return None
        
        print_color(f"[*] Starting TCP Connect scan on {target}", "CYAN")
        print_color(f"[*] Scanning {len(ports)} ports...")
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(check_port, port): port for port in ports}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    open_ports.append(result)
                    print_color(f"[+] Port {result['port']}/{result['service']} - OPEN", "GREEN")
        
        return sorted(open_ports, key=lambda x: x['port'])
    
    def nmap_scan(self, target: str, args: str = "-sT -sV --top-ports 100") -> str:
        """
        Run nmap with safe arguments for rootless
        -sT: TCP Connect scan (no root needed)
        -sV: Service version detection
        """
        cmd = ["nmap"] + args.split() + [target]
        try:
            result = subprocess.run(cmd, capture_output=True, 
                                  text=True, timeout=300)
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"
    
    def ping_sweep(self, network: str) -> List[str]:
        """Ping sweep to find live hosts"""
        live_hosts = []
        base = ".".join(network.split(".")[:3])
        
        def ping_host(ip: int) -> Optional[str]:
            host = f"{base}.{ip}"
            try:
                result = subprocess.run(["ping", "-c", "1", "-W", "1", host],
                                      capture_output=True, timeout=3)
                if result.returncode == 0:
                    return host
            except:
                pass
            return None
        
        print_color(f"[*] Pinging {network}.0/24...", "CYAN")
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(ping_host, i) for i in range(1, 255)]
            for future in as_completed(futures):
                host = future.result()
                if host:
                    live_hosts.append(host)
                    print_color(f"[+] Host alive: {host}", "GREEN")
        
        return live_hosts

class WebScanner:
    """Web vulnerability scanner for NetHunter"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.0'
        }
        self.vulnerabilities = []
    
    def check_headers(self, url: str) -> Dict:
        """Analyze security headers"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                headers = dict(response.headers)
                
                security_headers = {
                    'X-Frame-Options': headers.get('X-Frame-Options', 'Missing'),
                    'X-XSS-Protection': headers.get('X-XSS-Protection', 'Missing'),
                    'X-Content-Type-Options': headers.get('X-Content-Type-Options', 'Missing'),
                    'Strict-Transport-Security': headers.get('Strict-Transport-Security', 'Missing'),
                    'Content-Security-Policy': headers.get('Content-Security-Policy', 'Missing'),
                    'Server': headers.get('Server', 'Not disclosed')
                }
                return security_headers
        except Exception as e:
            return {"error": str(e)}
    
    def nikto_scan(self, url: str) -> str:
        """Run nikto scan"""
        cmd = ["nikto", "-h", url, "-C", "all"]
        try:
            result = subprocess.run(cmd, capture_output=True, 
                                  text=True, timeout=300)
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"
    
    def whatweb_scan(self, url: str) -> str:
        """Technology fingerprinting"""
        cmd = ["whatweb", "-a", "3", url]
        try:
            result = subprocess.run(cmd, capture_output=True, 
                                  text=True, timeout=60)
            return result.stdout
        except:
            return "whatweb not available"
    
    def directory_brute(self, url: str, wordlist: List[str]) -> List[str]:
        """Lightweight directory brute force"""
        found = []
        
        def check_path(path: str) -> Optional[str]:
            try:
                full_url = f"{url.rstrip('/')}/{path}"
                req = urllib.request.Request(full_url, method='HEAD', 
                                           headers=self.headers)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status in [200, 301, 302, 401, 403]:
                        return f"{full_url} - {resp.status}"
            except:
                pass
            return None
        
        print_color(f"[*] Brute forcing directories on {url}", "CYAN")
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(check_path, path) for path in wordlist]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    found.append(result)
                    print_color(f"[+] Found: {result}", "GREEN")
        
        return found

class OSINTModule:
    """OSINT gathering - fully compatible with NetHunter"""
    
    def __init__(self):
        self.results = {}
    
    def dns_enum(self, domain: str) -> Dict:
        """DNS enumeration"""
        records = {}
        
        for rtype in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA']:
            try:
                cmd = ["dig", "+short", domain, rtype]
                result = subprocess.run(cmd, capture_output=True, 
                                      text=True, timeout=10)
                if result.stdout.strip():
                    records[rtype] = result.stdout.strip().split('\n')
            except:
                pass
        
        return records
    
    def whois_lookup(self, domain: str) -> str:
        """WHOIS lookup"""
        try:
            cmd = ["whois", domain]
            result = subprocess.run(cmd, capture_output=True, 
                                  text=True, timeout=15)
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"
    
    def subdomain_enum(self, domain: str, wordlist: List[str]) -> List[str]:
        """Subdomain enumeration"""
        subdomains = []
        
        def check_subdomain(sub: str) -> Optional[str]:
            host = f"{sub}.{domain}"
            try:
                socket.gethostbyname(host)
                return host
            except:
                return None
        
        print_color(f"[*] Enumerating subdomains for {domain}", "CYAN")
        
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(check_subdomain, sub) for sub in wordlist]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    subdomains.append(result)
                    print_color(f"[+] Found: {result}", "GREEN")
        
        return subdomains
    
    def reverse_ip_lookup(self, ip: str) -> List[str]:
        """Reverse IP lookup"""
        try:
            hostname = socket.gethostbyaddr(ip)
            return [hostname[0]]
        except:
            return []

class SSLChecker:
    """SSL/TLS certificate analysis"""
    
    def check_certificate(self, hostname: str, port: int = 443) -> Dict:
        """Analyze SSL certificate"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    return {
                        "subject": cert.get("subject"),
                        "issuer": cert.get("issuer"),
                        "not_after": cert.get("notAfter"),
                        "not_before": cert.get("notBefore"),
                        "serial_number": cert.get("serialNumber"),
                        "tls_version": version,
                        "cipher": cipher[0],
                        "bits": cipher[2]
                    }
        except Exception as e:
            return {"error": str(e)}
    
    def testssl_scan(self, target: str) -> str:
        """Run testssl.sh if available"""
        cmd = ["testssl.sh", "--fast", target]
        try:
            result = subprocess.run(cmd, capture_output=True, 
                                  text=True, timeout=120)
            return result.stdout
        except:
            return "testssl.sh not installed"

class ReportGenerator:
    """Generate scan reports"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_json(self, data: Dict, filename: str):
        """Save results as JSON"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print_color(f"[+] JSON report saved: {filepath}", "GREEN")
    
    def save_txt(self, content: str, filename: str):
        """Save results as text"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print_color(f"[+] Text report saved: {filepath}", "GREEN")

def print_banner():
    banner = """
    █████╗ ███╗   ██╗    ██████╗  █████╗  ██████╗██╗  ██╗██╗███╗   ██╗ ██████╗ 
   ██╔══██╗████╗  ██║    ██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██║████╗  ██║██╔════╝ 
   ███████║██╔██╗ ██║    ██████╔╝███████║██║     █████╔╝ ██║██╔██╗ ██║██║  ███╗
   ██╔══██║██║╚██╗██║    ██╔══██╗██╔══██║██║     ██╔═██╗ ██║██║╚██╗██║██║   ██║
   ██║  ██║██║ ╚████║    ██║  ██║██║  ██║╚██████╗██║  ██╗██║██║ ╚████║╚██████╔╝
   ╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
   ╔═══════════════════════════════════════════════════════════════════════════╗
   ║     NetHunter Rootless Edition | Android Compatible | No Root Needed      ║
   ╚═══════════════════════════════════════════════════════════════════════════╝
    """
    print_color(banner, "CYAN")

def main_menu():
    """Interactive main menu"""
    print_banner()
    
    env = NetHunterEnvironment()
    env.print_info()
    
    scanner = NetworkScanner(env)
    web_scanner = WebScanner()
    osint = OSINTModule()
    ssl_checker = SSLChecker()
    reporter = ReportGenerator()
    
    while True:
        print_color("\n=== AN Hacking Menu ===", "MAGENTA")
        print_color("1. Network Scan (TCP Connect)")
        print_color("2. Web Vulnerability Scan")
        print_color("3. OSINT / Reconnaissance")
        print_color("4. SSL/TLS Analysis")
        print_color("5. Ping Sweep")
        print_color("6. Full Scan (All modules)")
        print_color("0. Exit")
        
        choice = input("\n[?] Select option: ")
        
        if choice == "1":
            target = input("[*] Enter target IP: ")
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 
                    3306, 3389, 5432, 5900, 8080, 8443]
            results = scanner.tcp_connect_scan(target, ports)
            reporter.save_json({"target": target, "ports": results}, 
                             f"scan_{target}.json")
            
        elif choice == "2":
            url = input("[*] Enter URL (https://example.com): ")
            headers = web_scanner.check_headers(url)
            reporter.save_json({"url": url, "headers": headers}, 
                             f"web_{url.replace('://', '_')}.json")
            
        elif choice == "3":
            domain = input("[*] Enter domain: ")
            dns = osint.dns_enum(domain)
            whois = osint.whois_lookup(domain)
            reporter.save_json({"domain": domain, "dns": dns}, 
                             f"osint_{domain}.json")
            reporter.save_txt(whois, f"whois_{domain}.txt")
            
        elif choice == "4":
            host = input("[*] Enter hostname: ")
            cert = ssl_checker.check_certificate(host)
            reporter.save_json(cert, f"ssl_{host}.json")
            
        elif choice == "5":
            network = input("[*] Enter network (e.g., 192.168.1): ")
            live = scanner.ping_sweep(network)
            reporter.save_json({"network": network, "hosts": live}, 
                             f"ping_{network}.json")
            
        elif choice == "0":
            print_color("\n[*] Exiting...", "YELLOW")
            break

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print_color("\n\n[*] Interrupted by user", "YELLOW")
        sys.exit(0)