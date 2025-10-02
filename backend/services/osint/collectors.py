"""
OSINT Intelligence Collectors
Collects intelligence from various open source channels
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import re

logger = logging.getLogger(__name__)


class CTLogCollector:
    """
    Certificate Transparency Log Collector
    Monitors CT logs for newly issued certificates
    """
    
    def __init__(self):
        self.base_url = "https://crt.sh"
    
    async def collect_certificates(
        self,
        domain: str,
        include_expired: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Collect certificates from CT logs for a domain
        
        Args:
            domain: Domain to search for
            include_expired: Include expired certificates
        
        Returns:
            List of certificate records
        """
        logger.info(f"Collecting CT logs for {domain}")
        
        certificates = []
        
        try:
            # Query crt.sh API
            url = f"{self.base_url}/?q=%.{domain}&output=json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for entry in data:
                            cert = self._parse_certificate(entry, domain)
                            
                            # Filter expired if requested
                            if not include_expired and cert.get("is_expired"):
                                continue
                            
                            certificates.append(cert)
        
        except Exception as e:
            logger.error(f"Error collecting CT logs for {domain}: {e}")
        
        logger.info(f"Collected {len(certificates)} certificates for {domain}")
        return certificates
    
    def _parse_certificate(self, entry: Dict, domain: str) -> Dict[str, Any]:
        """Parse certificate entry from crt.sh"""
        
        # Parse dates
        not_before = entry.get("not_before")
        not_after = entry.get("not_after")
        
        # Determine if expired
        is_expired = False
        if not_after:
            try:
                expiry_date = datetime.fromisoformat(not_after.replace("Z", "+00:00"))
                is_expired = expiry_date < datetime.now(expiry_date.tzinfo)
            except:
                pass
        
        # Extract domains from name_value
        name_value = entry.get("name_value", "")
        domains = [d.strip() for d in name_value.split("\n") if d.strip()]
        
        # Clean wildcards
        clean_domains = []
        for d in domains:
            d = d.replace("*.", "").strip().lower()
            if d and d.endswith(domain):
                clean_domains.append(d)
        
        return {
            "id": str(entry.get("id")),
            "issuer_ca_id": entry.get("issuer_ca_id"),
            "issuer_name": entry.get("issuer_name"),
            "common_name": entry.get("common_name"),
            "name_value": name_value,
            "domains": list(set(clean_domains)),
            "not_before": not_before,
            "not_after": not_after,
            "is_expired": is_expired,
            "serial_number": entry.get("serial_number"),
            "entry_timestamp": entry.get("entry_timestamp"),
            "collected_at": datetime.now().isoformat(),
            "source": "crt.sh",
        }
    
    async def monitor_new_certificates(
        self,
        domain: str,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Monitor for newly issued certificates since a given time
        
        Args:
            domain: Domain to monitor
            since: Only return certificates issued after this time
        
        Returns:
            List of new certificates
        """
        if since is None:
            since = datetime.now() - timedelta(days=1)  # Default: last 24 hours
        
        all_certs = await self.collect_certificates(domain, include_expired=False)
        
        # Filter by timestamp
        new_certs = []
        for cert in all_certs:
            try:
                entry_time = cert.get("entry_timestamp")
                if entry_time:
                    cert_time = datetime.fromisoformat(entry_time.replace("Z", "+00:00"))
                    if cert_time > since:
                        new_certs.append(cert)
            except:
                # Include if we can't parse time (better safe than sorry)
                new_certs.append(cert)
        
        logger.info(f"Found {len(new_certs)} new certificates for {domain} since {since}")
        return new_certs


class GitHubAdvisoryCollector:
    """
    GitHub Security Advisory Collector
    Collects vulnerability advisories from GitHub
    """
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.base_url = "https://api.github.com"
    
    async def collect_advisories(
        self,
        ecosystem: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Collect security advisories from GitHub
        
        Args:
            ecosystem: Filter by ecosystem (npm, pip, maven, etc.)
            severity: Filter by severity (low, moderate, high, critical)
            limit: Maximum number of advisories to return
        
        Returns:
            List of security advisories
        """
        logger.info(f"Collecting GitHub advisories (ecosystem={ecosystem}, severity={severity})")
        
        advisories = []
        
        try:
            # Build query parameters
            params = {
                "per_page": min(limit, 100),
                "sort": "published",
                "direction": "desc",
            }
            
            if ecosystem:
                params["ecosystem"] = ecosystem
            if severity:
                params["severity"] = severity
            
            # GitHub Security Advisories API
            url = f"{self.base_url}/advisories"
            
            headers = {
                "Accept": "application/vnd.github+json",
            }
            if self.github_token:
                headers["Authorization"] = f"Bearer {self.github_token}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for entry in data[:limit]:
                            advisory = self._parse_advisory(entry)
                            advisories.append(advisory)
                    elif response.status == 403:
                        logger.warning("GitHub API rate limit exceeded")
                    else:
                        logger.error(f"GitHub API returned status {response.status}")
        
        except Exception as e:
            logger.error(f"Error collecting GitHub advisories: {e}")
        
        logger.info(f"Collected {len(advisories)} GitHub advisories")
        return advisories
    
    def _parse_advisory(self, entry: Dict) -> Dict[str, Any]:
        """Parse GitHub advisory entry"""
        
        # Extract CVE IDs
        cve_ids = []
        identifiers = entry.get("identifiers", [])
        for identifier in identifiers:
            if identifier.get("type") == "CVE":
                cve_ids.append(identifier.get("value"))
        
        # Extract CWE IDs
        cwe_ids = []
        cwes = entry.get("cwes", [])
        for cwe in cwes:
            cwe_id = cwe.get("cwe_id")
            if cwe_id:
                cwe_ids.append(cwe_id)
        
        # Extract affected packages
        affected_packages = []
        vulnerabilities = entry.get("vulnerabilities", [])
        for vuln in vulnerabilities:
            package = vuln.get("package", {})
            if package:
                affected_packages.append({
                    "ecosystem": package.get("ecosystem"),
                    "name": package.get("name"),
                })
        
        return {
            "id": entry.get("ghsa_id"),
            "cve_ids": cve_ids,
            "cwe_ids": cwe_ids,
            "summary": entry.get("summary"),
            "description": entry.get("description"),
            "severity": entry.get("severity"),
            "cvss_score": entry.get("cvss", {}).get("score"),
            "cvss_vector": entry.get("cvss", {}).get("vector_string"),
            "affected_packages": affected_packages,
            "published_at": entry.get("published_at"),
            "updated_at": entry.get("updated_at"),
            "withdrawn_at": entry.get("withdrawn_at"),
            "url": entry.get("html_url"),
            "source": "github_advisory",
            "collected_at": datetime.now().isoformat(),
        }
    
    async def search_advisories_by_package(
        self,
        package_name: str,
        ecosystem: str
    ) -> List[Dict[str, Any]]:
        """
        Search for advisories affecting a specific package
        
        Args:
            package_name: Name of the package
            ecosystem: Package ecosystem (npm, pip, etc.)
        
        Returns:
            List of relevant advisories
        """
        logger.info(f"Searching advisories for {ecosystem}:{package_name}")
        
        # Collect all advisories for the ecosystem
        all_advisories = await self.collect_advisories(ecosystem=ecosystem, limit=1000)
        
        # Filter by package name
        relevant = []
        for advisory in all_advisories:
            for pkg in advisory.get("affected_packages", []):
                if pkg.get("name", "").lower() == package_name.lower():
                    relevant.append(advisory)
                    break
        
        logger.info(f"Found {len(relevant)} advisories for {package_name}")
        return relevant


class ThreatFeedCollector:
    """
    Threat Intelligence Feed Collector
    Collects IOCs and threat data from public feeds
    """
    
    # Public threat feeds (examples - many require API keys)
    PUBLIC_FEEDS = {
        "abuse_ch_urlhaus": "https://urlhaus.abuse.ch/downloads/json_recent/",
        "abuse_ch_feodotracker": "https://feodotracker.abuse.ch/downloads/ipblocklist.json",
    }
    
    async def collect_iocs(
        self,
        feed_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect IOCs from threat feeds
        
        Args:
            feed_name: Specific feed to collect from (None = all feeds)
        
        Returns:
            List of IOCs with metadata
        """
        logger.info(f"Collecting IOCs from threat feeds (feed={feed_name})")
        
        iocs = []
        feeds_to_collect = [feed_name] if feed_name else list(self.PUBLIC_FEEDS.keys())
        
        for feed in feeds_to_collect:
            if feed in self.PUBLIC_FEEDS:
                feed_iocs = await self._collect_from_feed(feed)
                iocs.extend(feed_iocs)
        
        logger.info(f"Collected {len(iocs)} IOCs from threat feeds")
        return iocs
    
    async def _collect_from_feed(self, feed_name: str) -> List[Dict[str, Any]]:
        """Collect from a specific feed"""
        url = self.PUBLIC_FEEDS.get(feed_name)
        if not url:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_feed_data(feed_name, data)
        except Exception as e:
            logger.error(f"Error collecting from {feed_name}: {e}")
        
        return []
    
    def _parse_feed_data(self, feed_name: str, data: Any) -> List[Dict[str, Any]]:
        """Parse feed-specific data format"""
        iocs = []
        
        # Each feed has its own format - this is a simplified parser
        if isinstance(data, list):
            for item in data[:100]:  # Limit to 100 items
                ioc = {
                    "source": feed_name,
                    "collected_at": datetime.now().isoformat(),
                    "raw_data": item,
                }
                iocs.append(ioc)
        
        return iocs
