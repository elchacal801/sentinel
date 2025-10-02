"""
Neo4j Knowledge Graph Manager
Handles entity creation, relationships, and graph queries
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from neo4j import AsyncSession
from utils.database import get_neo4j_session

logger = logging.getLogger(__name__)


class KnowledgeGraphManager:
    """Manages the Neo4j knowledge graph"""
    
    @staticmethod
    async def initialize_schema(session: AsyncSession):
        """
        Initialize Neo4j schema with constraints and indexes
        Run this once when setting up the database
        """
        try:
            # Create constraints (ensures uniqueness)
            constraints = [
                "CREATE CONSTRAINT asset_id IF NOT EXISTS FOR (a:Asset) REQUIRE a.id IS UNIQUE",
                "CREATE CONSTRAINT vulnerability_id IF NOT EXISTS FOR (v:Vulnerability) REQUIRE v.id IS UNIQUE",
                "CREATE CONSTRAINT ioc_id IF NOT EXISTS FOR (i:IOC) REQUIRE i.id IS UNIQUE",
                "CREATE CONSTRAINT threat_actor_id IF NOT EXISTS FOR (t:ThreatActor) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT intel_report_id IF NOT EXISTS FOR (r:IntelReport) REQUIRE r.id IS UNIQUE",
            ]
            
            for constraint in constraints:
                await session.run(constraint)
                logger.info(f"Created constraint: {constraint}")
            
            # Create indexes for performance
            indexes = [
                "CREATE INDEX asset_type IF NOT EXISTS FOR (a:Asset) ON (a.type)",
                "CREATE INDEX asset_criticality IF NOT EXISTS FOR (a:Asset) ON (a.criticality)",
                "CREATE INDEX vuln_severity IF NOT EXISTS FOR (v:Vulnerability) ON (v.severity)",
                "CREATE INDEX ioc_type IF NOT EXISTS FOR (i:IOC) ON (i.type)",
                "CREATE INDEX intel_source IF NOT EXISTS FOR (r:IntelReport) ON (r.source_type)",
            ]
            
            for index in indexes:
                await session.run(index)
                logger.info(f"Created index: {index}")
            
            logger.info("Neo4j schema initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise
    
    @staticmethod
    async def create_asset(session: AsyncSession, asset_data: Dict[str, Any]) -> str:
        """
        Create or update an asset node in the graph
        """
        query = """
        MERGE (a:Asset {id: $id})
        SET a.type = $type,
            a.value = $value,
            a.criticality = $criticality,
            a.status = $status,
            a.discovered = datetime($discovered),
            a.last_seen = datetime($last_seen),
            a.ports = $ports,
            a.services = $services,
            a.technologies = $technologies,
            a.tags = $tags,
            a.updated_at = datetime()
        RETURN a.id as id
        """
        
        params = {
            "id": asset_data["id"],
            "type": asset_data["type"],
            "value": asset_data["value"],
            "criticality": asset_data.get("criticality", "unknown"),
            "status": asset_data.get("status", "unknown"),
            "discovered": asset_data.get("discovered", datetime.now().isoformat()),
            "last_seen": asset_data.get("last_seen", datetime.now().isoformat()),
            "ports": asset_data.get("ports", []),
            "services": asset_data.get("services", []),
            "technologies": asset_data.get("technologies", []),
            "tags": asset_data.get("tags", []),
        }
        
        result = await session.run(query, params)
        record = await result.single()
        return record["id"] if record else None
    
    @staticmethod
    async def create_vulnerability(session: AsyncSession, vuln_data: Dict[str, Any]) -> str:
        """Create or update a vulnerability node"""
        query = """
        MERGE (v:Vulnerability {id: $id})
        SET v.title = $title,
            v.description = $description,
            v.cvss_score = $cvss_score,
            v.severity = $severity,
            v.exploit_available = $exploit_available,
            v.patch_available = $patch_available,
            v.published_date = datetime($published_date),
            v.updated_at = datetime()
        RETURN v.id as id
        """
        
        params = {
            "id": vuln_data["id"],
            "title": vuln_data["title"],
            "description": vuln_data.get("description", ""),
            "cvss_score": vuln_data.get("cvss_score"),
            "severity": vuln_data.get("severity", "unknown"),
            "exploit_available": vuln_data.get("exploit_available", False),
            "patch_available": vuln_data.get("patch_available", False),
            "published_date": vuln_data.get("published_date", datetime.now().isoformat()),
        }
        
        result = await session.run(query, params)
        record = await result.single()
        return record["id"] if record else None
    
    @staticmethod
    async def create_relationship(
        session: AsyncSession,
        from_id: str,
        from_type: str,
        to_id: str,
        to_type: str,
        relationship: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a relationship between two nodes
        
        Example relationships:
        - Asset HAS_VULNERABILITY Vulnerability
        - Vulnerability EXPLOITED_BY ThreatActor
        - Asset PART_OF Asset (subdomain -> domain)
        """
        props = properties or {}
        props["created_at"] = datetime.now().isoformat()
        props["confidence"] = props.get("confidence", 1.0)
        
        # Build properties string for Cypher
        props_str = ", ".join([f"{k}: ${k}" for k in props.keys()])
        
        query = f"""
        MATCH (a:{from_type} {{id: $from_id}})
        MATCH (b:{to_type} {{id: $to_id}})
        MERGE (a)-[r:{relationship}]->(b)
        SET r += {{{props_str}}}
        RETURN r
        """
        
        params = {
            "from_id": from_id,
            "to_id": to_id,
            **props
        }
        
        try:
            result = await session.run(query, params)
            record = await result.single()
            return record is not None
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            return False
    
    @staticmethod
    async def get_asset(session: AsyncSession, asset_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an asset and its immediate relationships"""
        query = """
        MATCH (a:Asset {id: $asset_id})
        OPTIONAL MATCH (a)-[:HAS_VULNERABILITY]->(v:Vulnerability)
        OPTIONAL MATCH (a)-[:EXPOSED_TO]->(t:ThreatActor)
        RETURN a,
               collect(DISTINCT v) as vulnerabilities,
               collect(DISTINCT t) as threats
        """
        
        result = await session.run(query, {"asset_id": asset_id})
        record = await result.single()
        
        if not record:
            return None
        
        asset = dict(record["a"])
        return {
            "asset": asset,
            "vulnerabilities": [dict(v) for v in record["vulnerabilities"] if v],
            "threats": [dict(t) for t in record["threats"] if t],
        }
    
    @staticmethod
    async def find_attack_paths(
        session: AsyncSession,
        target_asset_id: str,
        max_depth: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find potential attack paths to a target asset
        Uses graph traversal to identify paths through vulnerabilities
        """
        query = """
        MATCH path = (start:Asset)-[*1..$max_depth]-(target:Asset {id: $target_id})
        WHERE start.criticality IN ['low', 'medium']
        AND ANY(rel IN relationships(path) WHERE type(rel) = 'HAS_VULNERABILITY')
        RETURN path,
               length(path) as path_length,
               [node IN nodes(path) | node.id] as node_ids,
               [rel IN relationships(path) | type(rel)] as rel_types
        LIMIT 10
        """
        
        result = await session.run(query, {
            "target_id": target_asset_id,
            "max_depth": max_depth
        })
        
        paths = []
        async for record in result:
            paths.append({
                "length": record["path_length"],
                "nodes": record["node_ids"],
                "relationships": record["rel_types"],
            })
        
        return paths
    
    @staticmethod
    async def query_graph(session: AsyncSession, cypher_query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute a custom Cypher query"""
        result = await session.run(cypher_query, params or {})
        records = []
        async for record in result:
            records.append(dict(record))
        return records
    
    @staticmethod
    async def get_entity_context(session: AsyncSession, entity_id: str, depth: int = 2) -> Optional[Dict[str, Any]]:
        """
        Get an entity and its surrounding context (neighborhood) in the graph
        
        Returns nodes and edges for visualization
        """
        query = """
        MATCH path = (center)-[*1..$depth]-(connected)
        WHERE center.id = $entity_id
        WITH center, collect(DISTINCT connected) as neighbors, collect(DISTINCT path) as paths
        RETURN center,
               neighbors,
               [p IN paths | relationships(p)] as all_relationships
        """
        
        result = await session.run(query, {"entity_id": entity_id, "depth": depth})
        record = await result.single()
        
        if not record:
            return None
        
        # Build nodes list
        nodes = [dict(record["center"])]
        nodes.extend([dict(n) for n in record["neighbors"] if n])
        
        # Build edges list
        edges = []
        for rel_list in record["all_relationships"]:
            for rel in rel_list:
                edges.append({
                    "from": rel.start_node.get("id"),
                    "to": rel.end_node.get("id"),
                    "type": rel.type,
                    "properties": dict(rel)
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    @staticmethod
    async def get_graph_stats(session: AsyncSession) -> Dict[str, int]:
        """Get statistics about the knowledge graph"""
        query = """
        MATCH (a:Asset)
        OPTIONAL MATCH (v:Vulnerability)
        OPTIONAL MATCH (t:ThreatActor)
        OPTIONAL MATCH (i:IOC)
        OPTIONAL MATCH ()-[r]->()
        RETURN 
            count(DISTINCT a) as assets,
            count(DISTINCT v) as vulnerabilities,
            count(DISTINCT t) as threat_actors,
            count(DISTINCT i) as iocs,
            count(DISTINCT r) as relationships
        """
        
        result = await session.run(query)
        record = await result.single()
        
        if record:
            return dict(record)
        return {
            "assets": 0,
            "vulnerabilities": 0,
            "threat_actors": 0,
            "iocs": 0,
            "relationships": 0
        }
