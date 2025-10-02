"""
Asset Discovery Service
Performs subdomain enumeration and asset discovery
"""

import asyncio
import logging
import re
import dns.resolver
import dns.asyncresolver
from typing import List, Set, Dict, Any
from datetime import datetime
import aiohttp
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class AssetDiscovery:
    """
    Discovers internet-facing assets through multiple techniques:
    - Subdomain enumeration (passive and active)
    - DNS resolution
    - Certificate transparency logs
    - Common subdomain brute-forcing
    """
    
    # Common subdomains to check
    COMMON_SUBDOMAINS = [
        "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "ns2",
        "webdisk", "ns", "cpanel", "whm", "autodiscover", "autoconfig", "m", "imap",
        "test", "ns3", "blog", "pop3", "dev", "www2", "admin", "forum", "news", "vpn",
        "ns4", "mail2", "new", "mysql", "old", "lists", "support", "mobile", "mx",
        "static", "docs", "beta", "shop", "sql", "secure", "demo", "cp", "calendar",
        "wiki", "web", "media", "email", "images", "img", "www1", "intranet", "portal",
        "video", "sip", "dns2", "api", "cdn", "stats", "dns1", "ns5", "ns6", "smtp2",
        "secure2", "proxy", "dns", "wap", "app", "stage", "staging", "uat", "prod",
        "production", "assets", "downloads", "internal", "private",
    ]
    
    def __init__(self):
        self.resolver = dns.asyncresolver.Resolver()
        self.resolver.timeout = 2
        self.resolver.lifetime = 2
    
    async def discover_subdomains(
        self,
        domain: str,
        method: str = "passive"
    ) -> List[Dict[str, Any]]:
        """
        Discover subdomains for a given domain
        
        Args:
            domain: Root domain to enumerate
            method: Discovery method - 'passive', 'active', or 'comprehensive'
        
        Returns:
            List of discovered assets with metadata
        """
        logger.info(f"Starting subdomain discovery for {domain} using {method} method")
        
        discovered_assets = []
        subdomains = set()
        
        # Passive discovery - Certificate Transparency logs
        if method in ["passive", "comprehensive"]:
            ct_subdomains = await self._discover_from_ct_logs(domain)
            subdomains.update(ct_subdomains)
            logger.info(f"Found {len(ct_subdomains)} subdomains from CT logs")
        
        # Active discovery - DNS brute force
        if method in ["active", "comprehensive"]:
            bruteforce_subdomains = await self._bruteforce_subdomains(domain)
            subdomains.update(bruteforce_subdomains)
            logger.info(f"Found {len(bruteforce_subdomains)} subdomains from brute force")
        
        # Resolve all discovered subdomains to IPs
        for subdomain in subdomains:
            try:
                ips = await self._resolve_dns(subdomain)
                if ips:
                    discovered_assets.append({
                        "type": "subdomain",
                        "value": subdomain,
                        "parent_domain": domain,
                        "ip_addresses": ips,
                        "discovered_at": datetime.now().isoformat(),
                        "discovery_method": method,
                    })
            except Exception as e:
                logger.debug(f"Failed to resolve {subdomain}: {e}")
        
        logger.info(f"Discovered {len(discovered_assets)} total assets for {domain}")
        return discovered_assets
    
    async def _discover_from_ct_logs(self, domain: str) -> Set[str]:
        """
        Query Certificate Transparency logs for subdomains
        Uses crt.sh public API
        """
        subdomains = set()
        
        try:
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for entry in data:
                            name_value = entry.get("name_value", "")
                            # Split by newlines (crt.sh returns multiple names)
                            names = name_value.split("\n")
                            
                            for name in names:
                                name = name.strip().lower()
                                # Remove wildcards
                                name = name.replace("*.", "")
                                
                                # Only include if it's a subdomain of our target
                                if name.endswith(domain) and name != domain:
                                    # Validate it's a proper subdomain
                                    if self._is_valid_subdomain(name):
                                        subdomains.add(name)
        
        except Exception as e:
            logger.error(f"Error querying CT logs for {domain}: {e}")
        
        return subdomains
    
    async def _bruteforce_subdomains(self, domain: str) -> Set[str]:
        """
        Brute force common subdomains using DNS resolution
        """
        subdomains = set()
        
        # Create tasks for concurrent DNS resolution
        tasks = []
        for sub in self.COMMON_SUBDOMAINS:
            subdomain = f"{sub}.{domain}"
            tasks.append(self._check_subdomain_exists(subdomain))
        
        # Run all checks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful resolutions
        for subdomain, exists in zip(
            [f"{sub}.{domain}" for sub in self.COMMON_SUBDOMAINS],
            results
        ):
            if exists and not isinstance(exists, Exception):
                subdomains.add(subdomain)
        
        return subdomains
    
    async def _check_subdomain_exists(self, subdomain: str) -> bool:
        """Check if a subdomain resolves"""
        try:
            await self.resolver.resolve(subdomain, "A")
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            return False
        except Exception as e:
            logger.debug(f"Error checking {subdomain}: {e}")
            return False
    
    async def _resolve_dns(self, hostname: str) -> List[str]:
        """Resolve hostname to IP addresses"""
        ips = []
        
        try:
            # Try A records
            answers = await self.resolver.resolve(hostname, "A")
            ips.extend([str(rdata) for rdata in answers])
        except Exception:
            pass
        
        try:
            # Try AAAA records (IPv6)
            answers = await self.resolver.resolve(hostname, "AAAA")
            ips.extend([str(rdata) for rdata in answers])
        except Exception:
            pass
        
        return list(set(ips))  # Remove duplicates
    
    @staticmethod
    def _is_valid_subdomain(subdomain: str) -> bool:
        """Validate subdomain format"""
        # Basic validation
        if not subdomain or len(subdomain) > 253:
            return False
        
        # Check for valid characters
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, subdomain))
    
    async def discover_domain_info(self, domain: str) -> Dict[str, Any]:
        """
        Gather comprehensive information about a domain
        """
        info = {
            "domain": domain,
            "discovered_at": datetime.now().isoformat(),
            "ip_addresses": [],
            "nameservers": [],
            "mx_records": [],
            "txt_records": [],
        }
        
        try:
            # A records
            info["ip_addresses"] = await self._resolve_dns(domain)
            
            # NS records
            try:
                ns_answers = await self.resolver.resolve(domain, "NS")
                info["nameservers"] = [str(rdata) for rdata in ns_answers]
            except Exception:
                pass
            
            # MX records
            try:
                mx_answers = await self.resolver.resolve(domain, "MX")
                info["mx_records"] = [
                    {"priority": rdata.preference, "server": str(rdata.exchange)}
                    for rdata in mx_answers
                ]
            except Exception:
                pass
            
            # TXT records
            try:
                txt_answers = await self.resolver.resolve(domain, "TXT")
                info["txt_records"] = [str(rdata) for rdata in txt_answers]
            except Exception:
                pass
        
        except Exception as e:
            logger.error(f"Error gathering domain info for {domain}: {e}")
        
        return info
