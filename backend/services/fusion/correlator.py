"""
Multi-INT Intelligence Correlation
Fuses intelligence from multiple sources to produce high-confidence assessments
"""

import logging
from typing import List, Dict, Any, Set, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """
    Calculates confidence scores for intelligence assessments
    Uses structured analytical techniques from the Intelligence Community
    """
    
    # Confidence levels (IC standard)
    CONFIDENCE_LEVELS = {
        "high": (0.8, 1.0),
        "moderate": (0.5, 0.8),
        "low": (0.2, 0.5),
        "minimal": (0.0, 0.2),
    }
    
    @staticmethod
    def calculate_source_confidence(source_type: str, source_reputation: float = 0.8) -> float:
        """
        Calculate confidence based on source type and reputation
        
        Args:
            source_type: Type of intelligence source (OSINT, SIGINT, etc.)
            source_reputation: Reputation score of the specific source
        
        Returns:
            Confidence score 0.0-1.0
        """
        # Base confidence by source type
        base_confidence = {
            "osint": 0.7,      # Open source - verifiable but may be stale
            "sigint": 0.85,    # Signals - technical, hard to spoof
            "cybint": 0.9,     # Cyber - technical, verifiable
            "geoint": 0.8,     # Geographic - visual, verifiable
            "humint": 0.6,     # Human - valuable but subjective
        }
        
        source_conf = base_confidence.get(source_type.lower(), 0.5)
        
        # Combine with source reputation
        return (source_conf + source_reputation) / 2
    
    @staticmethod
    def calculate_multi_source_confidence(sources: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence when multiple sources corroborate
        
        Uses Bayesian-like updating:
        - Multiple independent sources increase confidence
        - Different source types increase confidence more
        """
        if not sources:
            return 0.0
        
        if len(sources) == 1:
            return ConfidenceScorer.calculate_source_confidence(
                sources[0].get("type", "osint"),
                sources[0].get("reputation", 0.8)
            )
        
        # Calculate base confidence from primary source
        primary = sources[0]
        confidence = ConfidenceScorer.calculate_source_confidence(
            primary.get("type", "osint"),
            primary.get("reputation", 0.8)
        )
        
        # Count unique source types
        source_types = set(s.get("type", "").lower() for s in sources)
        
        # Bonus for multiple independent sources
        for source in sources[1:]:
            source_conf = ConfidenceScorer.calculate_source_confidence(
                source.get("type", "osint"),
                source.get("reputation", 0.8)
            )
            
            # If different type, higher boost
            if source.get("type", "").lower() not in [primary.get("type", "").lower()]:
                confidence = min(confidence + (source_conf * 0.15), 1.0)
            else:
                # Same type, smaller boost
                confidence = min(confidence + (source_conf * 0.05), 1.0)
        
        # Extra boost for diverse source types
        diversity_bonus = (len(source_types) - 1) * 0.05
        confidence = min(confidence + diversity_bonus, 1.0)
        
        return confidence
    
    @staticmethod
    def calculate_temporal_confidence(
        observed_time: datetime,
        current_time: Optional[datetime] = None,
        decay_days: int = 30
    ) -> float:
        """
        Calculate confidence decay based on age of intelligence
        
        Fresh intelligence is more confident than old intelligence
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Handle timezone-naive datetimes
        if observed_time.tzinfo is None and current_time.tzinfo is not None:
            observed_time = observed_time.replace(tzinfo=current_time.tzinfo)
        elif observed_time.tzinfo is not None and current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=observed_time.tzinfo)
        
        age_days = (current_time - observed_time).days
        
        if age_days < 0:
            return 1.0  # Future date, assume fresh
        
        # Exponential decay
        decay_rate = 1.0 / decay_days
        confidence = max(1.0 - (age_days * decay_rate), 0.1)
        
        return confidence
    
    @staticmethod
    def get_confidence_label(score: float) -> str:
        """Get IC-standard confidence label from score"""
        for label, (min_score, max_score) in ConfidenceScorer.CONFIDENCE_LEVELS.items():
            if min_score <= score < max_score:
                return label
        return "minimal"


class MultiINTCorrelator:
    """
    Correlates intelligence from multiple INT disciplines
    Identifies patterns, relationships, and high-confidence assessments
    """
    
    def __init__(self, temporal_window_hours: int = 24):
        self.temporal_window = timedelta(hours=temporal_window_hours)
        self.confidence_scorer = ConfidenceScorer()
    
    async def correlate_indicators(
        self,
        indicators: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Correlate indicators of compromise (IOCs) across sources
        
        Args:
            indicators: List of IOC records with source attribution
        
        Returns:
            Correlated IOC clusters with confidence scores
        """
        logger.info(f"Correlating {len(indicators)} indicators")
        
        # Group by IOC value
        ioc_groups = defaultdict(list)
        for indicator in indicators:
            ioc_value = indicator.get("value", "").lower()
            if ioc_value:
                ioc_groups[ioc_value].append(indicator)
        
        # Build correlation results
        correlations = []
        for ioc_value, group in ioc_groups.items():
            if len(group) > 1:
                # Multiple sources for same IOC - high confidence
                sources = [{"type": i.get("source_type"), "reputation": 0.8} for i in group]
                confidence = self.confidence_scorer.calculate_multi_source_confidence(sources)
                
                # Extract unique attributes
                threat_actors = set()
                malware_families = set()
                tags = set()
                
                for ioc in group:
                    if ioc.get("threat_actor"):
                        threat_actors.add(ioc["threat_actor"])
                    if ioc.get("malware_family"):
                        malware_families.add(ioc["malware_family"])
                    tags.update(ioc.get("tags", []))
                
                correlations.append({
                    "ioc_value": ioc_value,
                    "ioc_type": group[0].get("type"),
                    "occurrence_count": len(group),
                    "sources": [i.get("source_type") for i in group],
                    "confidence": confidence,
                    "confidence_label": self.confidence_scorer.get_confidence_label(confidence),
                    "threat_actors": list(threat_actors),
                    "malware_families": list(malware_families),
                    "tags": list(tags),
                    "first_seen": min(i.get("first_seen", datetime.now()) for i in group),
                    "last_seen": max(i.get("last_seen", datetime.now()) for i in group),
                })
        
        logger.info(f"Found {len(correlations)} correlated IOC clusters")
        return sorted(correlations, key=lambda x: x["confidence"], reverse=True)
    
    async def correlate_vulnerabilities_with_threats(
        self,
        vulnerabilities: List[Dict[str, Any]],
        threat_intel: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Correlate vulnerability data with threat intelligence
        Identifies which vulnerabilities are actively being exploited
        """
        logger.info(f"Correlating {len(vulnerabilities)} vulns with {len(threat_intel)} threat reports")
        
        correlations = []
        
        for vuln in vulnerabilities:
            cve_id = vuln.get("id")
            if not cve_id or not cve_id.startswith("CVE-"):
                continue
            
            # Find threat intel mentioning this CVE
            related_threats = []
            for threat in threat_intel:
                # Check if CVE mentioned in threat data
                threat_cves = threat.get("cve_ids", [])
                threat_description = threat.get("description", "").upper()
                
                if cve_id in threat_cves or cve_id in threat_description:
                    related_threats.append(threat)
            
            if related_threats:
                # This vulnerability has active threat intelligence
                sources = [
                    {"type": "cybint", "reputation": 0.9},  # CVE data
                    *[{"type": t.get("source", "osint"), "reputation": 0.8} for t in related_threats]
                ]
                
                confidence = self.confidence_scorer.calculate_multi_source_confidence(sources)
                
                correlations.append({
                    "cve_id": cve_id,
                    "cvss_score": vuln.get("cvss_score"),
                    "severity": vuln.get("severity"),
                    "threat_intelligence": len(related_threats),
                    "active_exploitation": any(t.get("active_exploitation") for t in related_threats),
                    "threat_actors": list(set(t.get("threat_actor") for t in related_threats if t.get("threat_actor"))),
                    "confidence": confidence,
                    "confidence_label": self.confidence_scorer.get_confidence_label(confidence),
                    "risk_multiplier": 2.5 if any(t.get("active_exploitation") for t in related_threats) else 1.0,
                    "recommendation": "URGENT: Patch immediately" if confidence > 0.8 else "Prioritize patching",
                })
        
        logger.info(f"Found {len(correlations)} vulnerability-threat correlations")
        return sorted(correlations, key=lambda x: (x["confidence"], x.get("cvss_score", 0)), reverse=True)
    
    async def temporal_correlation(
        self,
        events: List[Dict[str, Any]],
        window_hours: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find events that occurred within a temporal window
        Identifies campaigns and coordinated activity
        """
        if window_hours:
            window = timedelta(hours=window_hours)
        else:
            window = self.temporal_window
        
        logger.info(f"Performing temporal correlation with {window.total_seconds()/3600}h window")
        
        # Sort events by time
        sorted_events = sorted(
            events,
            key=lambda x: x.get("timestamp", x.get("observed_time", datetime.min))
        )
        
        # Find temporal clusters
        clusters = []
        current_cluster = []
        cluster_start = None
        
        for event in sorted_events:
            event_time = event.get("timestamp", event.get("observed_time"))
            
            if not isinstance(event_time, datetime):
                continue
            
            if not current_cluster:
                current_cluster = [event]
                cluster_start = event_time
            else:
                # Check if within window of cluster start
                if event_time - cluster_start <= window:
                    current_cluster.append(event)
                else:
                    # Start new cluster
                    if len(current_cluster) > 1:
                        clusters.append(current_cluster)
                    current_cluster = [event]
                    cluster_start = event_time
        
        # Don't forget last cluster
        if len(current_cluster) > 1:
            clusters.append(current_cluster)
        
        # Build correlation results
        correlations = []
        for idx, cluster in enumerate(clusters):
            cluster_sources = [{"type": e.get("source_type", "osint"), "reputation": 0.8} for e in cluster]
            confidence = self.confidence_scorer.calculate_multi_source_confidence(cluster_sources)
            
            correlations.append({
                "cluster_id": f"temporal-cluster-{idx+1}",
                "event_count": len(cluster),
                "time_span_hours": (cluster[-1].get("timestamp", datetime.now()) - cluster[0].get("timestamp", datetime.now())).total_seconds() / 3600,
                "start_time": cluster[0].get("timestamp"),
                "end_time": cluster[-1].get("timestamp"),
                "sources": list(set(e.get("source_type") for e in cluster)),
                "confidence": confidence,
                "confidence_label": self.confidence_scorer.get_confidence_label(confidence),
                "events": cluster,
                "analysis": f"Detected {len(cluster)} related events within {window.total_seconds()/3600}h window",
            })
        
        logger.info(f"Found {len(correlations)} temporal clusters")
        return correlations
    
    async def spatial_correlation(
        self,
        entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Correlate entities by geographic location
        Identifies regional targeting or infrastructure clustering
        """
        logger.info(f"Performing spatial correlation on {len(entities)} entities")
        
        # Group by country/region
        location_groups = defaultdict(list)
        for entity in entities:
            location = entity.get("country") or entity.get("region") or entity.get("location")
            if location:
                location_groups[location].append(entity)
        
        # Find significant clusters
        correlations = []
        for location, group in location_groups.items():
            if len(group) > 2:  # At least 3 entities in same location
                sources = [{"type": e.get("source_type", "geoint"), "reputation": 0.8} for e in group]
                confidence = self.confidence_scorer.calculate_multi_source_confidence(sources)
                
                correlations.append({
                    "location": location,
                    "entity_count": len(group),
                    "entity_types": list(set(e.get("type") for e in group)),
                    "confidence": confidence,
                    "confidence_label": self.confidence_scorer.get_confidence_label(confidence),
                    "entities": [e.get("id") for e in group],
                    "analysis": f"Detected {len(group)} entities clustered in {location}",
                })
        
        logger.info(f"Found {len(correlations)} spatial correlations")
        return sorted(correlations, key=lambda x: x["entity_count"], reverse=True)
    
    async def identify_campaigns(
        self,
        ioc_correlations: List[Dict[str, Any]],
        temporal_clusters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify potential threat campaigns from correlated intelligence
        Combines IOC, temporal, and behavioral patterns
        """
        logger.info("Identifying potential threat campaigns")
        
        campaigns = []
        
        # Look for high-confidence IOC clusters with temporal correlation
        for ioc_corr in ioc_correlations:
            if ioc_corr["confidence"] < 0.7:
                continue
            
            # Check if any temporal clusters involve these IOCs
            related_temporal = []
            for temporal in temporal_clusters:
                # Check if temporal cluster events reference this IOC
                if any(ioc_corr["ioc_value"] in str(e) for e in temporal.get("events", [])):
                    related_temporal.append(temporal)
            
            if related_temporal or ioc_corr["occurrence_count"] > 3:
                # Potential campaign
                confidence = min(ioc_corr["confidence"] * 1.1, 1.0)  # Boost for campaign indicators
                
                campaigns.append({
                    "campaign_id": f"campaign-{len(campaigns)+1}",
                    "ioc": ioc_corr["ioc_value"],
                    "ioc_type": ioc_corr["ioc_type"],
                    "threat_actors": ioc_corr.get("threat_actors", []),
                    "malware_families": ioc_corr.get("malware_families", []),
                    "temporal_clusters": len(related_temporal),
                    "total_events": sum(t.get("event_count", 0) for t in related_temporal),
                    "confidence": confidence,
                    "confidence_label": self.confidence_scorer.get_confidence_label(confidence),
                    "first_observed": ioc_corr.get("first_seen"),
                    "last_observed": ioc_corr.get("last_seen"),
                    "assessment": "Coordinated threat campaign detected based on correlated indicators and temporal patterns",
                })
        
        logger.info(f"Identified {len(campaigns)} potential threat campaigns")
        return sorted(campaigns, key=lambda x: x["confidence"], reverse=True)
