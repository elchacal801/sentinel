"""
Celery Tasks for Intelligence Collection
These tasks run asynchronously in the background
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import uuid

from workers.celery_app import celery_app
from services.asm.discovery import AssetDiscovery
from services.asm.scanner import PortScanner, ServiceFingerprinter
from services.osint.collectors import CTLogCollector, GitHubAdvisoryCollector
from services.cybint.scanner import VulnerabilityScanner, CVEEnricher
from utils.graph import KnowledgeGraphManager
from utils.database import neo4j_driver

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async functions in Celery tasks"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Storage Helper Functions
async def store_assets_in_graph(assets: List[Dict[str, Any]], root_domain: str) -> int:
    """Store discovered assets in Neo4j knowledge graph"""
    stored = 0
    
    async with neo4j_driver.session() as session:
        graph_mgr = KnowledgeGraphManager()
        
        # Create root domain node
        root_asset_id = f"asset-domain-{root_domain.replace('.', '-')}"
        await graph_mgr.create_asset(session, {
            "id": root_asset_id,
            "type": "domain",
            "value": root_domain,
            "criticality": "high",
            "status": "active",
            "discovered": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
        })
        
        # Create subdomain nodes and relationships
        for asset in assets:
            asset_id = f"asset-subdomain-{asset['value'].replace('.', '-')}"
            
            # Create asset node
            await graph_mgr.create_asset(session, {
                "id": asset_id,
                "type": "subdomain",
                "value": asset["value"],
                "criticality": "medium",
                "status": "active",
                "discovered": asset["discovered_at"],
                "last_seen": asset["discovered_at"],
                "ports": [],
                "services": [],
                "technologies": [],
                "tags": [asset["discovery_method"]],
            })
            
            # Create relationship to parent domain
            await graph_mgr.create_relationship(
                session,
                from_id=asset_id,
                from_type="Asset",
                to_id=root_asset_id,
                to_type="Asset",
                relationship="PART_OF",
                properties={"discovered_at": asset["discovered_at"]}
            )
            
            # Create IP address nodes if available
            for ip in asset.get("ip_addresses", []):
                ip_id = f"asset-ip-{ip.replace('.', '-')}"
                await graph_mgr.create_asset(session, {
                    "id": ip_id,
                    "type": "ip",
                    "value": ip,
                    "criticality": "medium",
                    "status": "active",
                    "discovered": asset["discovered_at"],
                    "last_seen": asset["discovered_at"],
                })
                
                # Link subdomain to IP
                await graph_mgr.create_relationship(
                    session,
                    from_id=asset_id,
                    from_type="Asset",
                    to_id=ip_id,
                    to_type="Asset",
                    relationship="RESOLVES_TO",
                    properties={"discovered_at": asset["discovered_at"]}
                )
            
            stored += 1
    
    logger.info(f"Stored {stored} assets in knowledge graph")
    return stored


async def store_vulnerabilities_in_graph(asset_id: str, vulnerabilities: List[Dict[str, Any]]) -> int:
    """Store vulnerabilities and link to assets"""
    stored = 0
    
    async with neo4j_driver.session() as session:
        graph_mgr = KnowledgeGraphManager()
        
        for vuln in vulnerabilities:
            # Create vulnerability node
            vuln_id = vuln.get("id", f"vuln-{uuid.uuid4().hex[:8]}")
            
            await graph_mgr.create_vulnerability(session, {
                "id": vuln_id,
                "title": vuln.get("title", "Unknown Vulnerability"),
                "description": vuln.get("description", ""),
                "cvss_score": vuln.get("cvss_score"),
                "severity": vuln.get("severity", "unknown"),
                "exploit_available": vuln.get("exploit_available", False),
                "patch_available": vuln.get("patch_available", False),
                "published_date": vuln.get("detected_at", datetime.now().isoformat()),
            })
            
            # Link to asset
            await graph_mgr.create_relationship(
                session,
                from_id=asset_id,
                from_type="Asset",
                to_id=vuln_id,
                to_type="Vulnerability",
                relationship="HAS_VULNERABILITY",
                properties={
                    "confidence": vuln.get("confidence", 0.8),
                    "detected_at": vuln.get("detected_at", datetime.now().isoformat())
                }
            )
            
            stored += 1
    
    logger.info(f"Stored {stored} vulnerabilities in knowledge graph")
    return stored


@celery_app.task(bind=True, name="workers.tasks.discover_assets_task")
def discover_assets_task(self, target: str, method: str = "passive") -> Dict[str, Any]:
    """
    Discover assets for a target domain
    
    Args:
        target: Domain to discover
        method: Discovery method (passive, active, comprehensive)
    
    Returns:
        Task result with discovered assets
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Starting asset discovery for {target}")
    
    try:
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "discovering_subdomains", "target": target}
        )
        
        # Run discovery
        discovery = AssetDiscovery()
        assets = run_async(discovery.discover_subdomains(target, method))
        
        # Update state
        self.update_state(
            state="PROGRESS",
            meta={"status": "storing_results", "assets_found": len(assets)}
        )
        
        # Store assets in Neo4j knowledge graph
        stored_count = run_async(store_assets_in_graph(assets, target))
        
        result = {
            "task_id": task_id,
            "target": target,
            "method": method,
            "assets_discovered": len(assets),
            "assets": assets,
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
        }
        
        logger.info(f"[{task_id}] Asset discovery complete: {len(assets)} assets found")
        return result
        
    except Exception as e:
        logger.error(f"[{task_id}] Asset discovery failed: {e}")
        raise


@celery_app.task(bind=True, name="workers.tasks.scan_ports_task")
def scan_ports_task(
    self,
    target: str,
    scan_type: str = "common",
    ports: List[int] = None
) -> Dict[str, Any]:
    """
    Scan ports on a target
    
    Args:
        target: IP or hostname to scan
        scan_type: Type of scan (common, top100, full)
        ports: Specific ports to scan
    
    Returns:
        Task result with scan results
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Starting port scan for {target}")
    
    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "scanning_ports", "target": target}
        )
        
        # Run port scan
        scanner = PortScanner()
        scan_result = run_async(scanner.scan_host(target, ports, scan_type))
        
        # Fingerprint services on open ports
        if scan_result["open_ports"]:
            self.update_state(
                state="PROGRESS",
                meta={"status": "fingerprinting_services", "open_ports": len(scan_result["open_ports"])}
            )
            
            fingerprinter = ServiceFingerprinter()
            services = run_async(
                fingerprinter.fingerprint_services(target, scan_result["open_ports"])
            )
            scan_result["services"] = services
        
        # TODO: Store results in knowledge graph
        
        result = {
            "task_id": task_id,
            "target": target,
            "scan_result": scan_result,
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
        }
        
        logger.info(f"[{task_id}] Port scan complete: {len(scan_result['open_ports'])} open ports")
        return result
        
    except Exception as e:
        logger.error(f"[{task_id}] Port scan failed: {e}")
        raise


@celery_app.task(bind=True, name="workers.tasks.collect_osint_task")
def collect_osint_task(
    self,
    target: str,
    source: str = "ct_logs"
) -> Dict[str, Any]:
    """
    Collect OSINT intelligence for a target
    
    Args:
        target: Target domain or package
        source: OSINT source (ct_logs, github_advisories)
    
    Returns:
        Task result with collected intelligence
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Starting OSINT collection from {source} for {target}")
    
    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "collecting_osint", "source": source, "target": target}
        )
        
        intelligence = []
        
        if source == "ct_logs":
            collector = CTLogCollector()
            intelligence = run_async(collector.collect_certificates(target))
        
        elif source == "github_advisories":
            collector = GitHubAdvisoryCollector()
            # Parse target as ecosystem:package
            parts = target.split(":", 1)
            if len(parts) == 2:
                ecosystem, package = parts
                intelligence = run_async(
                    collector.search_advisories_by_package(package, ecosystem)
                )
            else:
                # Just collect general advisories
                intelligence = run_async(collector.collect_advisories(limit=100))
        
        # TODO: Store in knowledge graph
        
        result = {
            "task_id": task_id,
            "target": target,
            "source": source,
            "intelligence_collected": len(intelligence),
            "intelligence": intelligence,
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
        }
        
        logger.info(f"[{task_id}] OSINT collection complete: {len(intelligence)} items")
        return result
        
    except Exception as e:
        logger.error(f"[{task_id}] OSINT collection failed: {e}")
        raise


@celery_app.task(bind=True, name="workers.tasks.scan_vulnerabilities_task")
def scan_vulnerabilities_task(
    self,
    service_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Scan a service for vulnerabilities
    
    Args:
        service_info: Service information to scan
    
    Returns:
        Task result with vulnerabilities found
    """
    task_id = self.request.id
    service_name = service_info.get("service", "unknown")
    logger.info(f"[{task_id}] Starting vulnerability scan for {service_name}")
    
    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "scanning_vulnerabilities", "service": service_name}
        )
        
        # Scan for vulnerabilities
        scanner = VulnerabilityScanner()
        vulnerabilities = run_async(scanner.scan_service(service_info))
        
        # Enrich CVEs if any found
        if vulnerabilities:
            self.update_state(
                state="PROGRESS",
                meta={"status": "enriching_cves", "vulns_found": len(vulnerabilities)}
            )
            
            enricher = CVEEnricher()
            cve_ids = [v["id"] for v in vulnerabilities if v["id"].startswith("CVE-")]
            
            if cve_ids:
                enriched_cves = run_async(enricher.batch_enrich(cve_ids))
                
                # Add enriched data to vulnerabilities
                for vuln in vulnerabilities:
                    if vuln["id"] in enriched_cves:
                        vuln["enriched_data"] = enriched_cves[vuln["id"]]
        
        # Store vulnerabilities in knowledge graph if asset_id provided
        if vulnerabilities and service_info.get("asset_id"):
            stored = run_async(
                store_vulnerabilities_in_graph(service_info["asset_id"], vulnerabilities)
            )
            logger.info(f"Stored {stored} vulnerabilities for asset {service_info['asset_id']}")
        
        result = {
            "task_id": task_id,
            "service": service_name,
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
        }
        
        logger.info(f"[{task_id}] Vulnerability scan complete: {len(vulnerabilities)} found")
        return result
        
    except Exception as e:
        logger.error(f"[{task_id}] Vulnerability scan failed: {e}")
        raise


@celery_app.task(bind=True, name="workers.tasks.comprehensive_asset_scan")
def comprehensive_asset_scan(self, target: str) -> Dict[str, Any]:
    """
    Comprehensive scan: discovery + port scan + vulnerability scan
    
    This is a workflow task that chains multiple tasks together
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Starting comprehensive scan for {target}")
    
    workflow_results = {
        "task_id": task_id,
        "target": target,
        "started_at": datetime.now().isoformat(),
        "steps": [],
    }
    
    try:
        # Step 1: Discover assets
        self.update_state(state="PROGRESS", meta={"step": "asset_discovery"})
        discovery_result = discover_assets_task(target, "comprehensive")
        workflow_results["steps"].append({
            "step": "discovery",
            "result": discovery_result
        })
        
        # Step 2: Scan each discovered asset
        assets = discovery_result.get("assets", [])
        for asset in assets[:5]:  # Limit to first 5 assets for demo
            ip = asset.get("ip_addresses", [None])[0]
            if ip:
                self.update_state(
                    state="PROGRESS",
                    meta={"step": "port_scanning", "target": ip}
                )
                scan_result = scan_ports_task(ip, "common")
                workflow_results["steps"].append({
                    "step": "port_scan",
                    "target": ip,
                    "result": scan_result
                })
        
        workflow_results["status"] = "completed"
        workflow_results["completed_at"] = datetime.now().isoformat()
        
        logger.info(f"[{task_id}] Comprehensive scan complete")
        return workflow_results
        
    except Exception as e:
        logger.error(f"[{task_id}] Comprehensive scan failed: {e}")
        workflow_results["status"] = "failed"
        workflow_results["error"] = str(e)
        raise
