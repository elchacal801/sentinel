"""
Port Scanner and Service Fingerprinting
Scans discovered assets for open ports and running services
"""

import asyncio
import logging
import socket
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


class PortScanner:
    """
    Asynchronous port scanner
    Scans for open ports on discovered assets
    """
    
    # Common ports to scan
    COMMON_PORTS = [
        21,    # FTP
        22,    # SSH
        23,    # Telnet
        25,    # SMTP
        53,    # DNS
        80,    # HTTP
        110,   # POP3
        143,   # IMAP
        443,   # HTTPS
        445,   # SMB
        3306,  # MySQL
        3389,  # RDP
        5432,  # PostgreSQL
        5900,  # VNC
        6379,  # Redis
        8080,  # HTTP Alt
        8443,  # HTTPS Alt
        9200,  # Elasticsearch
        27017, # MongoDB
    ]
    
    # Top 100 ports (for comprehensive scans)
    TOP_100_PORTS = COMMON_PORTS + [
        20, 139, 161, 389, 636, 1433, 1521, 2049, 2181, 3000,
        5000, 5432, 5672, 5984, 6000, 6379, 6443, 7000, 7001, 7474,
        7687, 8000, 8008, 8081, 8088, 8888, 9000, 9042, 9090, 9092,
        9200, 9300, 9443, 9999, 10000, 11211, 15672, 27017, 27018, 50000,
    ]
    
    def __init__(self, timeout: float = 2.0, max_concurrent: int = 100):
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def scan_host(
        self,
        target: str,
        ports: Optional[List[int]] = None,
        scan_type: str = "common"
    ) -> Dict[str, Any]:
        """
        Scan a host for open ports
        
        Args:
            target: IP address or hostname
            ports: Specific ports to scan (overrides scan_type)
            scan_type: 'common', 'top100', or 'full'
        
        Returns:
            Scan results with open ports and metadata
        """
        logger.info(f"Starting port scan on {target} ({scan_type})")
        
        # Determine ports to scan
        if ports:
            scan_ports = ports
        elif scan_type == "common":
            scan_ports = self.COMMON_PORTS
        elif scan_type == "top100":
            scan_ports = self.TOP_100_PORTS
        elif scan_type == "full":
            scan_ports = list(range(1, 65536))
        else:
            scan_ports = self.COMMON_PORTS
        
        # Scan all ports concurrently
        tasks = [self._scan_port(target, port) for port in scan_ports]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect open ports
        open_ports = []
        for port, is_open in zip(scan_ports, results):
            if is_open and not isinstance(is_open, Exception):
                open_ports.append(port)
        
        scan_result = {
            "target": target,
            "scan_type": scan_type,
            "open_ports": sorted(open_ports),
            "total_scanned": len(scan_ports),
            "open_count": len(open_ports),
            "scanned_at": datetime.now().isoformat(),
        }
        
        logger.info(f"Scan complete for {target}: {len(open_ports)} open ports found")
        return scan_result
    
    async def _scan_port(self, target: str, port: int) -> bool:
        """
        Scan a single port
        Returns True if port is open, False otherwise
        """
        async with self.semaphore:
            try:
                # Create connection with timeout
                conn = asyncio.open_connection(target, port)
                reader, writer = await asyncio.wait_for(conn, timeout=self.timeout)
                
                # Port is open, close connection
                writer.close()
                await writer.wait_closed()
                
                logger.debug(f"Port {port} open on {target}")
                return True
                
            except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                # Port is closed or filtered
                return False
            except Exception as e:
                logger.debug(f"Error scanning port {port} on {target}: {e}")
                return False


class ServiceFingerprinter:
    """
    Identifies services running on open ports
    Performs HTTP banner grabbing and service detection
    """
    
    # Common service signatures
    SERVICE_SIGNATURES = {
        21: "ftp",
        22: "ssh",
        23: "telnet",
        25: "smtp",
        53: "dns",
        80: "http",
        110: "pop3",
        143: "imap",
        443: "https",
        445: "smb",
        3306: "mysql",
        3389: "rdp",
        5432: "postgresql",
        5900: "vnc",
        6379: "redis",
        8080: "http",
        8443: "https",
        9200: "elasticsearch",
        27017: "mongodb",
    }
    
    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout
    
    async def fingerprint_services(
        self,
        target: str,
        open_ports: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Fingerprint services on open ports
        
        Returns:
            List of detected services with version information
        """
        logger.info(f"Fingerprinting {len(open_ports)} services on {target}")
        
        services = []
        tasks = [self._fingerprint_port(target, port) for port in open_ports]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for port, service_info in zip(open_ports, results):
            if service_info and not isinstance(service_info, Exception):
                services.append(service_info)
        
        return services
    
    async def _fingerprint_port(self, target: str, port: int) -> Optional[Dict[str, Any]]:
        """Fingerprint a single service"""
        service_info = {
            "port": port,
            "service": self.SERVICE_SIGNATURES.get(port, "unknown"),
            "protocol": "tcp",
            "banner": None,
            "version": None,
            "technologies": [],
        }
        
        # Try HTTP(S) fingerprinting
        if port in [80, 443, 8080, 8443, 8000, 8888, 3000]:
            http_info = await self._fingerprint_http(target, port)
            if http_info:
                service_info.update(http_info)
                return service_info
        
        # Try banner grabbing
        banner = await self._grab_banner(target, port)
        if banner:
            service_info["banner"] = banner
            service_info["version"] = self._extract_version(banner)
        
        return service_info
    
    async def _fingerprint_http(self, target: str, port: int) -> Optional[Dict[str, Any]]:
        """
        Fingerprint HTTP/HTTPS services
        Detects web servers, frameworks, and technologies
        """
        protocol = "https" if port in [443, 8443] else "http"
        url = f"{protocol}://{target}:{port}"
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, allow_redirects=False, ssl=False) as response:
                    headers = response.headers
                    
                    # Extract server information
                    server = headers.get("Server", "")
                    powered_by = headers.get("X-Powered-By", "")
                    
                    # Detect technologies
                    technologies = []
                    if server:
                        technologies.append(server)
                    if powered_by:
                        technologies.append(powered_by)
                    
                    # Read response body (limited)
                    try:
                        body = await response.text()
                        body = body[:1000]  # Limit to first 1000 chars
                        
                        # Detect common frameworks/CMS
                        if "WordPress" in body:
                            technologies.append("WordPress")
                        if "Joomla" in body:
                            technologies.append("Joomla")
                        if "Drupal" in body:
                            technologies.append("Drupal")
                        if "django" in body.lower():
                            technologies.append("Django")
                        if "flask" in body.lower():
                            technologies.append("Flask")
                    except:
                        pass
                    
                    return {
                        "service": "http" if protocol == "http" else "https",
                        "server": server,
                        "technologies": list(set(technologies)),
                        "status_code": response.status,
                        "headers": dict(headers),
                    }
        
        except Exception as e:
            logger.debug(f"HTTP fingerprint failed for {url}: {e}")
            return None
    
    async def _grab_banner(self, target: str, port: int) -> Optional[str]:
        """
        Grab service banner
        Connects to port and reads initial response
        """
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(target, port),
                timeout=self.timeout
            )
            
            # Read banner (first 512 bytes)
            banner_data = await asyncio.wait_for(
                reader.read(512),
                timeout=self.timeout
            )
            
            writer.close()
            await writer.wait_closed()
            
            # Decode banner
            banner = banner_data.decode("utf-8", errors="ignore").strip()
            return banner if banner else None
            
        except Exception as e:
            logger.debug(f"Banner grab failed for {target}:{port}: {e}")
            return None
    
    @staticmethod
    def _extract_version(banner: str) -> Optional[str]:
        """Extract version information from banner"""
        import re
        
        # Common version patterns
        patterns = [
            r'(\d+\.\d+\.\d+)',  # x.y.z
            r'(\d+\.\d+)',        # x.y
        ]
        
        for pattern in patterns:
            match = re.search(pattern, banner)
            if match:
                return match.group(1)
        
        return None
