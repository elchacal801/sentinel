"""
Intelligence Products API Routes
Endpoints for generating and retrieving intelligence products
"""
from fastapi import APIRouter, Query, Depends
from fastapi.responses import Response
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from utils.database import get_neo4j_session
from utils.graph import KnowledgeGraphManager
from services.products.current_intel import CurrentIntelligenceGenerator
from services.products.iw_alerts import IndicationsWarningSystem
from services.products.target_packages import TargetPackageGenerator
from services.products.executive_briefs import ExecutiveBriefingGenerator

router = APIRouter()


# Pydantic models
class IntelligenceProduct(BaseModel):
    id: str
    type: str  # current_intelligence, indications_warning, target_package, executive_briefing
    title: str
    classification: str
    generated: datetime
    format: str  # json, pdf, html


# Endpoints
@router.get("/", summary="List intelligence products")
async def list_products(
    product_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000)
):
    """
    List all generated intelligence products
    
    **Product Types:**
    - Current Intelligence (daily briefings)
    - Indications & Warning (I&W alerts)
    - Target Packages (asset profiles)
    - Executive Briefings (strategic assessments)
    """
    return {
        "classification": "UNCLASSIFIED",
        "total": 0,
        "products": [],
        "message": "Intelligence product generation not yet implemented"
    }


@router.get("/current-intelligence", summary="Generate current intelligence")
async def generate_current_intelligence(
    time_period_hours: int = Query(24, ge=1, le=168),
    session = Depends(get_neo4j_session)
):
    """
    Generate current intelligence briefing
    
    **Contents:**
    - Executive summary
    - Last 24 hours key developments
    - New threats detected
    - Attack surface changes
    - Priority actions
    - Intelligence gaps
    """
    graph_mgr = KnowledgeGraphManager()
    intel_gen = CurrentIntelligenceGenerator()
    
    # Query data from graph
    assets_query = "MATCH (a:Asset) RETURN a LIMIT 1000"
    assets_result = await graph_mgr.query_graph(session, assets_query, {})
    assets = [dict(r["a"]) for r in assets_result]
    
    vulns_query = "MATCH (v:Vulnerability) RETURN v LIMIT 1000"
    vulns_result = await graph_mgr.query_graph(session, vulns_query, {})
    vulnerabilities = [dict(r["v"]) for r in vulns_result]
    
    threats_query = "MATCH (t:ThreatActor) RETURN t LIMIT 1000"
    threats_result = await graph_mgr.query_graph(session, threats_query, {})
    threats = [dict(r["t"]) for r in threats_result]
    
    # Generate briefing
    briefing = await intel_gen.generate_daily_brief(
        assets, vulnerabilities, threats, None, time_period_hours
    )
    
    return briefing


@router.get("/indications-warning", summary="Get I&W alerts")
async def get_indications_warning(
    severity: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168),
    session = Depends(get_neo4j_session)
):
    """
    Get Indications & Warning (I&W) alerts
    
    **Monitors:**
    - Reconnaissance activity
    - Suspicious infrastructure changes
    - IOC sightings
    - Threat actor activity
    - Vulnerability weaponization
    """
    graph_mgr = KnowledgeGraphManager()
    iw_system = IndicationsWarningSystem()
    
    # Query data from graph
    assets_query = "MATCH (a:Asset) RETURN a LIMIT 1000"
    assets_result = await graph_mgr.query_graph(session, assets_query, {})
    assets = [dict(r["a"]) for r in assets_result]
    
    vulns_query = "MATCH (v:Vulnerability) RETURN v LIMIT 1000"
    vulns_result = await graph_mgr.query_graph(session, vulns_query, {})
    vulnerabilities = [dict(r["v"]) for r in vulns_result]
    
    threats_query = "MATCH (t:ThreatActor) RETURN t LIMIT 1000"
    threats_result = await graph_mgr.query_graph(session, threats_query, {})
    threats = [dict(r["t"]) for r in threats_result]
    
    # Generate alerts
    alerts = await iw_system.generate_iw_alerts(
        assets, vulnerabilities, threats, None, None
    )
    
    # Filter by severity if specified
    if severity:
        alerts = [a for a in alerts if a.get("severity") == severity]
    
    # Generate summary
    summary = await iw_system.generate_iw_summary(alerts)
    
    return summary


@router.post("/target-package/{asset_id}", summary="Generate target package")
async def generate_target_package(
    asset_id: str,
    session = Depends(get_neo4j_session)
):
    """
    Generate comprehensive target package for an asset
    
    **Includes:**
    - Asset profile
    - Technical details
    - Vulnerability summary
    - Threat intelligence
    - Attack paths
    - Historical timeline
    - Recommendations
    """
    graph_mgr = KnowledgeGraphManager()
    target_gen = TargetPackageGenerator()
    
    # Get target asset
    target_asset = await graph_mgr.get_asset(session, asset_id)
    if not target_asset:
        return {
            "classification": "UNCLASSIFIED",
            "error": "Asset not found",
            "asset_id": asset_id
        }
    
    # Get related assets
    related_query = """
    MATCH (a:Asset {id: $asset_id})-[r]-(related:Asset)
    RETURN related
    LIMIT 50
    """
    related_result = await graph_mgr.query_graph(session, related_query, {"asset_id": asset_id})
    related_assets = [dict(r["related"]) for r in related_result]
    
    # Get vulnerabilities
    vulns_query = """
    MATCH (a:Asset {id: $asset_id})-[:HAS_VULNERABILITY]->(v:Vulnerability)
    RETURN v
    """
    vulns_result = await graph_mgr.query_graph(session, vulns_query, {"asset_id": asset_id})
    vulnerabilities = [dict(r["v"]) for r in vulns_result]
    
    # Get threats
    threats_query = """
    MATCH (t:ThreatActor)-[r]->(a:Asset {id: $asset_id})
    RETURN t
    """
    threats_result = await graph_mgr.query_graph(session, threats_query, {"asset_id": asset_id})
    threats = [dict(r["t"]) for r in threats_result]
    
    # Generate package
    package = await target_gen.generate_target_package(
        target_asset["asset"],
        related_assets,
        vulnerabilities,
        threats,
        None,  # attack_paths
        None   # risk_assessment
    )
    
    return package


@router.get("/target-package/{product_id}", summary="Get target package")
async def get_target_package(product_id: str, format: str = Query("json", regex="^(json|pdf|html)$")):
    """Get previously generated target package"""
    return {
        "classification": "UNCLASSIFIED//FOUO",
        "product_id": product_id,
        "format": format,
        "data": None,
        "message": "Target package retrieval not yet implemented"
    }


@router.post("/executive-briefing", summary="Generate executive briefing")
async def generate_executive_briefing(
    period: str = Query("weekly", regex="^(daily|weekly|monthly)$"),
    session = Depends(get_neo4j_session)
):
    """
    Generate executive-level strategic briefing
    
    **Contents:**
    - Threat landscape overview
    - Risk posture assessment
    - Key metrics and trends
    - Strategic recommendations
    - Budget implications
    """
    graph_mgr = KnowledgeGraphManager()
    exec_gen = ExecutiveBriefingGenerator()
    
    # Query data from graph
    assets_query = "MATCH (a:Asset) RETURN a LIMIT 1000"
    assets_result = await graph_mgr.query_graph(session, assets_query, {})
    assets = [dict(r["a"]) for r in assets_result]
    
    vulns_query = "MATCH (v:Vulnerability) RETURN v LIMIT 1000"
    vulns_result = await graph_mgr.query_graph(session, vulns_query, {})
    vulnerabilities = [dict(r["v"]) for r in vulns_result]
    
    threats_query = "MATCH (t:ThreatActor) RETURN t LIMIT 1000"
    threats_result = await graph_mgr.query_graph(session, threats_query, {})
    threats = [dict(r["t"]) for r in threats_result]
    
    # Generate briefing
    briefing = await exec_gen.generate_executive_briefing(
        period,
        assets,
        vulnerabilities,
        threats,
        None,  # incidents
        None,  # risk_metrics
        None   # previous_briefing
    )
    
    return briefing


@router.get("/executive-briefing/{product_id}", summary="Get executive briefing")
async def get_executive_briefing(product_id: str, format: str = Query("json", regex="^(json|pdf|pptx)$")):
    """Get previously generated executive briefing"""
    return {
        "classification": "UNCLASSIFIED",
        "product_id": product_id,
        "format": format,
        "data": None,
        "message": "Executive briefing retrieval not yet implemented"
    }


@router.get("/threat-report/{threat_id}", summary="Generate threat report")
async def generate_threat_report(threat_id: str):
    """
    Generate detailed threat intelligence report
    
    **Analysis:**
    - Threat actor profile
    - TTPs (MITRE ATT&CK)
    - Infrastructure
    - Campaign timeline
    - Indicators
    - Recommendations
    """
    return {
        "classification": "UNCLASSIFIED//FOUO",
        "product_type": "threat_report",
        "threat_id": threat_id,
        "report": None,
        "message": "Threat report generation not yet implemented"
    }


@router.get("/dashboard-data", summary="Get dashboard data")
async def get_dashboard_data():
    """
    Get real-time data for intelligence dashboard
    
    **Metrics:**
    - Assets monitored
    - Active threats
    - Collection sources
    - Recent activity
    - Risk trends
    """
    return {
        "classification": "UNCLASSIFIED",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "assets_monitored": 0,
            "threats_detected": 0,
            "intelligence_sources": 0,
            "active_collections": 0,
            "recent_alerts": 0
        },
        "activity_feed": [],
        "threat_map": [],
        "risk_distribution": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "message": "Dashboard data generation not yet implemented"
    }


@router.post("/export/{product_id}", summary="Export product")
async def export_product(
    product_id: str,
    format: str = Query("pdf", regex="^(pdf|html|json|docx)$")
):
    """
    Export intelligence product in specified format
    
    **Formats:** PDF, HTML, JSON, DOCX
    """
    return {
        "classification": "UNCLASSIFIED",
        "product_id": product_id,
        "format": format,
        "message": "Product export not yet implemented",
        "download_url": None
    }


@router.get("/templates", summary="List product templates")
async def list_templates():
    """List available intelligence product templates"""
    return {
        "classification": "UNCLASSIFIED",
        "templates": [
            {"id": "current_intel", "name": "Current Intelligence Briefing"},
            {"id": "iw_alert", "name": "Indications & Warning Alert"},
            {"id": "target_pkg", "name": "Target Package"},
            {"id": "exec_brief", "name": "Executive Briefing"},
            {"id": "threat_report", "name": "Threat Intelligence Report"}
        ],
        "message": "Templates available for future product generation"
    }
