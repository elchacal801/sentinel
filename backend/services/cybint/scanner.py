"""
Vulnerability Scanner and CVE Enrichment
Scans for vulnerabilities and enriches with threat intelligence
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
import re

logger = logging.getLogger(__name__)


class VulnerabilityScanner:
    """
    Vulnerability Scanner
    Detects known vulnerabilities in discovered services
    """
    
    def __init__(self):
        self.vulnerability_db = {}  # Cache for vulnerability data
    
    async def scan_service(
        self,
        service_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Scan a service for known vulnerabilities
        
        Args:
            service_info: Service information (name, version, port, etc.)
        
        Returns:
            List of detected vulnerabilities
        """
        vulnerabilities = []
        
        service_name = service_info.get("service", "").lower()
        version = service_info.get("version")
        technologies = service_info.get("technologies", [])
        
        logger.info(f"Scanning {service_name} for vulnerabilities")
        
        # Scan based on detected technologies
        for tech in technologies:
            tech_vulns = await self._check_technology_vulns(tech)
            vulnerabilities.extend(tech_vulns)
        
        # Check for common web vulnerabilities if HTTP service
        if service_name in ["http", "https"]:
            web_vulns = await self._check_web_vulnerabilities(service_info)
            vulnerabilities.extend(web_vulns)
        
        # Check version-specific vulnerabilities
        if version:
            version_vulns = await self._check_version_vulns(service_name, version)
            vulnerabilities.extend(version_vulns)
        
        logger.info(f"Found {len(vulnerabilities)} potential vulnerabilities")
        return vulnerabilities
    
    async def _check_technology_vulns(self, technology: str) -> List[Dict[str, Any]]:
        """Check for vulnerabilities in a specific technology"""
        vulnerabilities = []
        
        # Parse technology string to extract name and version
        tech_lower = technology.lower()
        
        # Common vulnerability patterns
        known_vulns = {
            "apache": [
                {
                    "id": "CVE-2021-41773",
                    "title": "Apache HTTP Server Path Traversal",
                    "severity": "critical",
                    "description": "Path traversal vulnerability in Apache 2.4.49-2.4.50",
                    "affected_versions": ["2.4.49", "2.4.50"],
                }
            ],
            "nginx": [
                {
                    "id": "CVE-2021-23017",
                    "title": "nginx DNS Resolver Off-by-One Heap Write",
                    "severity": "high",
                    "description": "Off-by-one heap write in nginx resolver",
                    "affected_versions": ["<1.20.1"],
                }
            ],
            "wordpress": [
                {
                    "id": "WPVULNDB-GENERIC",
                    "title": "WordPress Potential Vulnerabilities",
                    "severity": "medium",
                    "description": "WordPress installation detected - may have plugin/theme vulnerabilities",
                }
            ],
        }
        
        # Check if technology matches known vulnerable software
        for soft, vulns in known_vulns.items():
            if soft in tech_lower:
                for vuln in vulns:
                    vulnerabilities.append({
                        **vuln,
                        "detected_in": technology,
                        "confidence": 0.7,
                        "detected_at": datetime.now().isoformat(),
                    })
        
        return vulnerabilities
    
    async def _check_web_vulnerabilities(self, service_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for common web vulnerabilities"""
        vulnerabilities = []
        
        headers = service_info.get("headers", {})
        
        # Check for missing security headers
        security_headers = {
            "Strict-Transport-Security": "HSTS not configured",
            "X-Frame-Options": "Clickjacking protection missing",
            "X-Content-Type-Options": "MIME sniffing protection missing",
            "Content-Security-Policy": "CSP not configured",
            "X-XSS-Protection": "XSS protection header missing",
        }
        
        for header, issue in security_headers.items():
            if header not in headers:
                vulnerabilities.append({
                    "id": f"SEC-HEADER-{header}",
                    "title": f"Missing Security Header: {header}",
                    "description": issue,
                    "severity": "low",
                    "category": "security_misconfiguration",
                    "recommendation": f"Add {header} header to responses",
                    "confidence": 0.9,
                    "detected_at": datetime.now().isoformat(),
                })
        
        # Check for information disclosure
        server_header = headers.get("Server", "")
        if server_header and re.search(r'\d+\.\d+', server_header):
            vulnerabilities.append({
                "id": "INFO-DISCLOSURE-01",
                "title": "Server Version Information Disclosure",
                "description": f"Server header reveals version: {server_header}",
                "severity": "low",
                "category": "information_disclosure",
                "recommendation": "Remove version information from Server header",
                "confidence": 1.0,
                "detected_at": datetime.now().isoformat(),
            })
        
        return vulnerabilities
    
    async def _check_version_vulns(self, service: str, version: str) -> List[Dict[str, Any]]:
        """Check for version-specific vulnerabilities"""
        # This would query a vulnerability database
        # For now, returning empty list (to be implemented with real CVE database)
        return []


class CVEEnricher:
    """
    CVE Enrichment Service
    Enriches CVE IDs with detailed information from NVD and other sources
    """
    
    def __init__(self, nvd_api_key: Optional[str] = None):
        self.nvd_api_key = nvd_api_key
        self.nvd_base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.cache = {}  # Simple in-memory cache
    
    async def enrich_cve(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """
        Enrich a CVE ID with detailed information
        
        Args:
            cve_id: CVE identifier (e.g., CVE-2024-12345)
        
        Returns:
            Enriched CVE data or None if not found
        """
        # Check cache first
        if cve_id in self.cache:
            logger.debug(f"CVE {cve_id} found in cache")
            return self.cache[cve_id]
        
        logger.info(f"Enriching {cve_id} from NVD")
        
        try:
            # Query NVD API
            params = {"cveId": cve_id}
            headers = {}
            if self.nvd_api_key:
                headers["apiKey"] = self.nvd_api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.nvd_base_url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        cve_data = self._parse_nvd_response(data, cve_id)
                        
                        if cve_data:
                            # Cache the result
                            self.cache[cve_id] = cve_data
                            return cve_data
                    elif response.status == 404:
                        logger.warning(f"CVE {cve_id} not found in NVD")
                    elif response.status == 429:
                        logger.warning("NVD API rate limit exceeded")
                    else:
                        logger.error(f"NVD API returned status {response.status}")
        
        except Exception as e:
            logger.error(f"Error enriching {cve_id}: {e}")
        
        return None
    
    def _parse_nvd_response(self, data: Dict, cve_id: str) -> Optional[Dict[str, Any]]:
        """Parse NVD API response"""
        vulnerabilities = data.get("vulnerabilities", [])
        
        if not vulnerabilities:
            return None
        
        # Get first (should be only) vulnerability
        vuln = vulnerabilities[0]
        cve = vuln.get("cve", {})
        
        # Extract CVSS scores
        metrics = cve.get("metrics", {})
        cvss_v3 = metrics.get("cvssMetricV31", [{}])[0] if metrics.get("cvssMetricV31") else {}
        cvss_v2 = metrics.get("cvssMetricV2", [{}])[0] if metrics.get("cvssMetricV2") else {}
        
        cvss_data = cvss_v3.get("cvssData", {}) or cvss_v2.get("cvssData", {})
        
        # Extract descriptions
        descriptions = cve.get("descriptions", [])
        description = ""
        for desc in descriptions:
            if desc.get("lang") == "en":
                description = desc.get("value", "")
                break
        
        # Extract references
        references = []
        for ref in cve.get("references", []):
            references.append({
                "url": ref.get("url"),
                "source": ref.get("source"),
                "tags": ref.get("tags", []),
            })
        
        # Extract CWE
        weaknesses = cve.get("weaknesses", [])
        cwe_ids = []
        for weakness in weaknesses:
            for desc in weakness.get("description", []):
                cwe_id = desc.get("value")
                if cwe_id and cwe_id.startswith("CWE-"):
                    cwe_ids.append(cwe_id)
        
        return {
            "id": cve_id,
            "description": description,
            "cvss_score": cvss_data.get("baseScore"),
            "cvss_vector": cvss_data.get("vectorString"),
            "cvss_severity": cvss_data.get("baseSeverity", "").lower(),
            "cwe_ids": list(set(cwe_ids)),
            "published_date": cve.get("published"),
            "modified_date": cve.get("lastModified"),
            "references": references,
            "source": "nvd",
            "enriched_at": datetime.now().isoformat(),
        }
    
    async def batch_enrich(self, cve_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Enrich multiple CVEs concurrently
        
        Args:
            cve_ids: List of CVE identifiers
        
        Returns:
            Dictionary mapping CVE IDs to enriched data
        """
        logger.info(f"Batch enriching {len(cve_ids)} CVEs")
        
        # Create tasks for concurrent enrichment
        tasks = [self.enrich_cve(cve_id) for cve_id in cve_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build result dictionary
        enriched = {}
        for cve_id, result in zip(cve_ids, results):
            if result and not isinstance(result, Exception):
                enriched[cve_id] = result
        
        logger.info(f"Successfully enriched {len(enriched)} CVEs")
        return enriched
    
    async def check_exploit_availability(self, cve_id: str) -> Dict[str, Any]:
        """
        Check if exploits are available for a CVE
        Checks Exploit-DB and other sources
        """
        # This would query exploit databases
        # Simplified implementation
        return {
            "cve_id": cve_id,
            "exploit_available": False,  # Placeholder
            "exploit_maturity": "unproven",
            "sources": [],
            "checked_at": datetime.now().isoformat(),
        }
