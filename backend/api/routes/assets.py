"""
Assets API Routes
Endpoints for attack surface management and asset discovery
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from utils.database import get_neo4j_session
from utils.graph import KnowledgeGraphManager

router = APIRouter()


# Pydantic models
class Asset(BaseModel):
    id: str
    type: str  # domain, ip, service, cloud_resource
    value: str
    discovered: datetime
    last_seen: datetime
    criticality: str  # critical, high, medium, low
    status: str  # active, inactive, unknown
    tags: List[str] = []


class AssetDiscoveryRequest(BaseModel):
    target: str
    scan_type: str = "passive"  # passive, active, comprehensive


class AssetResponse(BaseModel):
    classification: str = "UNCLASSIFIED"
    data: Asset
    metadata: dict


# Endpoints
@router.get("/", summary="List all assets")
async def list_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    criticality: Optional[str] = None,
    asset_type: Optional[str] = None,
    session = Depends(get_neo4j_session)
):
    """
    List all discovered assets with optional filtering
    
    **Returns:** Paginated list of assets in the knowledge graph
    """
    # Build Cypher query with filters
    where_clauses = []
    params = {"skip": skip, "limit": limit}
    
    if criticality:
        where_clauses.append("a.criticality = $criticality")
        params["criticality"] = criticality
    
    if asset_type:
        where_clauses.append("a.type = $asset_type")
        params["asset_type"] = asset_type
    
    where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    # Query assets
    query = f"""
    MATCH (a:Asset)
    {where_clause}
    RETURN a
    ORDER BY a.discovered DESC
    SKIP $skip
    LIMIT $limit
    """
    
    count_query = f"""
    MATCH (a:Asset)
    {where_clause}
    RETURN count(a) as total
    """
    
    graph_mgr = KnowledgeGraphManager()
    assets_result = await graph_mgr.query_graph(session, query, params)
    count_result = await graph_mgr.query_graph(session, count_query, params)
    
    total = count_result[0]["total"] if count_result else 0
    assets = [dict(record["a"]) for record in assets_result]
    
    return {
        "classification": "UNCLASSIFIED",
        "total": total,
        "skip": skip,
        "limit": limit,
        "assets": assets
    }


@router.get("/{asset_id}", summary="Get asset details")
async def get_asset(asset_id: str, session = Depends(get_neo4j_session)):
    """
    Get detailed information about a specific asset
    
    **Returns:** Complete asset profile with vulnerabilities and threat intelligence
    """
    graph_mgr = KnowledgeGraphManager()
    asset_data = await graph_mgr.get_asset(session, asset_id)
    
    if not asset_data:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    
    return {
        "classification": "UNCLASSIFIED",
        "asset_id": asset_id,
        "asset": asset_data["asset"],
        "vulnerabilities": asset_data["vulnerabilities"],
        "threats": asset_data["threats"],
        "vulnerability_count": len(asset_data["vulnerabilities"]),
        "threat_count": len(asset_data["threats"])
    }


@router.post("/discover", summary="Initiate asset discovery")
async def discover_assets(request: AssetDiscoveryRequest):
    """
    Initiate attack surface discovery for a target
    
    **Process:**
    - Subdomain enumeration
    - Port scanning
    - Service fingerprinting
    - Technology detection
    - Vulnerability scanning
    """
    from workers.tasks import discover_assets_task
    
    # Initiate async task
    task = discover_assets_task.delay(request.target, request.scan_type)
    
    return {
        "classification": "UNCLASSIFIED",
        "status": "initiated",
        "target": request.target,
        "scan_type": request.scan_type,
        "task_id": task.id,
        "message": "Asset discovery initiated - check task status",
        "estimated_time": "5-15 minutes",
        "check_status_url": f"/api/v1/tasks/{task.id}"
    }


@router.get("/{asset_id}/vulnerabilities", summary="Get asset vulnerabilities")
async def get_asset_vulnerabilities(asset_id: str):
    """Get all vulnerabilities associated with an asset"""
    return {
        "classification": "UNCLASSIFIED",
        "asset_id": asset_id,
        "vulnerabilities": [],
        "message": "Vulnerability correlation not yet implemented"
    }


@router.get("/{asset_id}/threats", summary="Get asset threat intelligence")
async def get_asset_threats(asset_id: str):
    """Get threat intelligence relevant to an asset"""
    return {
        "classification": "UNCLASSIFIED",
        "asset_id": asset_id,
        "threats": [],
        "message": "Threat intelligence correlation not yet implemented"
    }


@router.get("/{asset_id}/attack-paths", summary="Get attack paths")
async def get_attack_paths(
    asset_id: str,
    max_depth: int = Query(5, ge=1, le=10),
    session = Depends(get_neo4j_session)
):
    """
    Get potential attack paths targeting this asset
    
    **Returns:** Graph of attack paths with likelihood and difficulty scores
    """
    graph_mgr = KnowledgeGraphManager()
    paths = await graph_mgr.find_attack_paths(session, asset_id, max_depth)
    
    return {
        "classification": "UNCLASSIFIED//FOUO",
        "asset_id": asset_id,
        "max_depth": max_depth,
        "attack_paths": paths,
        "path_count": len(paths),
        "analysis": f"Found {len(paths)} potential attack paths to {asset_id}" if paths else "No attack paths detected"
    }


@router.delete("/{asset_id}", summary="Remove asset")
async def delete_asset(asset_id: str):
    """Remove an asset from monitoring"""
    return {
        "classification": "UNCLASSIFIED",
        "status": "deleted",
        "asset_id": asset_id,
        "message": "Asset deletion not yet implemented"
    }
