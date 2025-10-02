"""
Current Intelligence Generator

Generates daily/periodic current intelligence briefings following IC standards:
- Key judgments
- Threat landscape summary
- New developments
- Ongoing activities
- Recommendations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter

logger = logging.getLogger(__name__)


class CurrentIntelligenceGenerator:
    """
    Generates current intelligence products
    
    Follows IC standards for current intelligence reporting
    """
    
    # Classification levels
    CLASSIFICATIONS = {
        "UNCLASSIFIED": "UNCLASSIFIED",
        "CUI": "UNCLASSIFIED//CUI",
        "FOUO": "UNCLASSIFIED//FOUO",
        "SECRET": "SECRET//NOFORN",
    }
    
    def __init__(self):
        self.logger = logger
    
    async def generate_daily_brief(
        self,
        assets: List[Dict[str, Any]],
        vulnerabilities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]],
        incidents: Optional[List[Dict[str, Any]]] = None,
        time_period_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate daily current intelligence briefing
        
        Args:
            assets: Asset data
            vulnerabilities: Vulnerability data
            threats: Threat intelligence
            incidents: Security incidents
            time_period_hours: Time period to cover
        
        Returns:
            Formatted intelligence brief
        """
        # Generate key judgments
        key_judgments = self._generate_key_judgments(
            assets, vulnerabilities, threats, incidents
        )
        
        # Threat landscape summary
        threat_landscape = self._analyze_threat_landscape(threats)
        
        # New developments
        new_developments = self._identify_new_developments(
            vulnerabilities, threats, time_period_hours
        )
        
        # Ongoing activities
        ongoing = self._summarize_ongoing_activities(threats, incidents)
        
        # Critical findings
        critical_findings = self._identify_critical_findings(
            assets, vulnerabilities, threats
        )
        
        # Recommendations
        recommendations = self._generate_recommendations(
            critical_findings, threat_landscape
        )
        
        # Metrics
        metrics = self._calculate_metrics(
            assets, vulnerabilities, threats, incidents
        )
        
        return {
            "classification": self.CLASSIFICATIONS["FOUO"],
            "product_type": "Current Intelligence Brief",
            "period": f"Last {time_period_hours} Hours",
            "generated_at": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(hours=24)).isoformat(),
            "key_judgments": key_judgments,
            "executive_summary": self._generate_executive_summary(
                key_judgments, critical_findings
            ),
            "threat_landscape": threat_landscape,
            "new_developments": new_developments,
            "ongoing_activities": ongoing,
            "critical_findings": critical_findings,
            "recommendations": recommendations,
            "metrics": metrics,
            "confidence": "moderate",
            "sources": self._list_sources(threats)
        }
    
    def _generate_key_judgments(
        self,
        assets: List[Dict[str, Any]],
        vulnerabilities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]],
        incidents: Optional[List[Dict[str, Any]]]
    ) -> List[str]:
        """Generate key judgments (IC standard)"""
        judgments = []
        
        # Critical vulnerabilities
        critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
        if critical_vulns:
            judgments.append(
                f"We assess with MODERATE confidence that {len(critical_vulns)} critical "
                f"vulnerabilities pose IMMEDIATE risk to organizational assets."
            )
        
        # Active threats
        active_threats = [t for t in threats if t.get("active_exploitation")]
        if active_threats:
            threat_actors = set(t.get("threat_actor") for t in active_threats if t.get("threat_actor"))
            if threat_actors:
                judgments.append(
                    f"We assess with HIGH confidence that threat actors {', '.join(threat_actors)} "
                    f"are actively conducting operations targeting similar organizations."
                )
        
        # Asset exposure
        internet_assets = [a for a in assets if "internet-facing" in a.get("tags", [])]
        if internet_assets:
            judgments.append(
                f"We assess with HIGH confidence that {len(internet_assets)} internet-facing "
                f"assets remain exposed to opportunistic scanning and targeting."
            )
        
        # Incidents
        if incidents and len(incidents) > 0:
            judgments.append(
                f"We assess with MODERATE confidence that {len(incidents)} security incidents "
                f"in the past 24 hours indicate elevated threat activity."
            )
        
        # Emerging patterns
        if threats:
            malware_families = [t.get("malware_family") for t in threats if t.get("malware_family")]
            if malware_families:
                common_malware = Counter(malware_families).most_common(1)
                if common_malware:
                    judgments.append(
                        f"We assess with MODERATE confidence that {common_malware[0][0]} malware "
                        f"represents the primary threat vector based on recent intelligence."
                    )
        
        return judgments[:5]  # Top 5 judgments
    
    def _generate_executive_summary(
        self,
        key_judgments: List[str],
        critical_findings: List[Dict[str, Any]]
    ) -> str:
        """Generate executive summary paragraph"""
        summary_parts = []
        
        if key_judgments:
            summary_parts.append(key_judgments[0])
        
        if critical_findings:
            critical_count = len([f for f in critical_findings if f.get("severity") == "critical"])
            if critical_count > 0:
                summary_parts.append(
                    f"Immediate action is required on {critical_count} critical findings."
                )
        
        summary_parts.append(
            "This brief provides situational awareness of the current cyber threat landscape "
            "and actionable recommendations for risk mitigation."
        )
        
        return " ".join(summary_parts)
    
    def _analyze_threat_landscape(
        self,
        threats: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze overall threat landscape"""
        if not threats:
            return {
                "assessment": "Limited threat intelligence available",
                "threat_level": "low",
                "primary_threats": [],
                "targeting_trends": []
            }
        
        # Extract threat actors
        threat_actors = [t.get("threat_actor") for t in threats if t.get("threat_actor")]
        actor_counts = Counter(threat_actors)
        
        # Extract malware
        malware = [t.get("malware_family") for t in threats if t.get("malware_family")]
        malware_counts = Counter(malware)
        
        # Active exploitation
        active_count = len([t for t in threats if t.get("active_exploitation")])
        
        # Determine threat level
        if active_count > 10:
            threat_level = "critical"
        elif active_count > 5:
            threat_level = "high"
        elif active_count > 0:
            threat_level = "elevated"
        else:
            threat_level = "moderate"
        
        return {
            "assessment": f"Threat landscape assessed as {threat_level.upper()}",
            "threat_level": threat_level,
            "active_threats": active_count,
            "primary_threat_actors": [
                {"name": actor, "mentions": count}
                for actor, count in actor_counts.most_common(5)
            ],
            "primary_malware": [
                {"family": mal, "mentions": count}
                for mal, count in malware_counts.most_common(5)
            ],
            "targeting_trends": self._identify_targeting_trends(threats)
        }
    
    def _identify_targeting_trends(
        self,
        threats: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify targeting trends from threat data"""
        trends = []
        
        # Industry targeting
        industries = [t.get("target_industry") for t in threats if t.get("target_industry")]
        if industries:
            common_industry = Counter(industries).most_common(1)[0]
            trends.append(f"Increased targeting of {common_industry[0]} sector")
        
        # Geographic targeting
        regions = [t.get("target_region") for t in threats if t.get("target_region")]
        if regions:
            common_region = Counter(regions).most_common(1)[0]
            trends.append(f"Geographic focus on {common_region[0]} region")
        
        # TTP trends
        ttps = []
        for threat in threats:
            if threat.get("ttps"):
                ttps.extend(threat["ttps"])
        if ttps:
            common_ttp = Counter(ttps).most_common(1)[0]
            trends.append(f"Prevalent use of {common_ttp[0]} technique")
        
        return trends[:3]
    
    def _identify_new_developments(
        self,
        vulnerabilities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]],
        time_period_hours: int
    ) -> List[Dict[str, Any]]:
        """Identify new developments in the time period"""
        developments = []
        cutoff = datetime.now() - timedelta(hours=time_period_hours)
        
        # New critical vulnerabilities
        for vuln in vulnerabilities:
            discovered = vuln.get("discovered")
            if discovered:
                if isinstance(discovered, str):
                    discovered = datetime.fromisoformat(discovered.replace('Z', '+00:00'))
                
                if discovered.replace(tzinfo=None) > cutoff:
                    if vuln.get("severity") in ["critical", "high"]:
                        developments.append({
                            "type": "vulnerability",
                            "severity": "high",
                            "title": f"New {vuln.get('severity', 'high')} vulnerability discovered",
                            "description": vuln.get("title", "Unknown vulnerability"),
                            "cve_id": vuln.get("id"),
                            "timestamp": discovered.isoformat()
                        })
        
        # New threat actor activity
        recent_threats = []
        for threat in threats:
            observed = threat.get("observed_at")
            if observed:
                if isinstance(observed, str):
                    observed = datetime.fromisoformat(observed.replace('Z', '+00:00'))
                
                if observed.replace(tzinfo=None) > cutoff:
                    recent_threats.append(threat)
        
        if recent_threats:
            new_actors = set(t.get("threat_actor") for t in recent_threats if t.get("threat_actor"))
            for actor in new_actors:
                developments.append({
                    "type": "threat_activity",
                    "severity": "medium",
                    "title": f"New activity from {actor}",
                    "description": f"Detected {len([t for t in recent_threats if t.get('threat_actor') == actor])} indicators",
                    "threat_actor": actor,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Sort by severity and timestamp
        severity_order = {"high": 0, "medium": 1, "low": 2}
        developments.sort(key=lambda x: (severity_order.get(x["severity"], 3), x["timestamp"]), reverse=True)
        
        return developments[:10]
    
    def _summarize_ongoing_activities(
        self,
        threats: List[Dict[str, Any]],
        incidents: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Summarize ongoing threat activities"""
        activities = []
        
        # Active campaigns
        campaigns = [t for t in threats if t.get("campaign_name")]
        if campaigns:
            campaign_names = set(t.get("campaign_name") for t in campaigns)
            for campaign in campaign_names:
                campaign_threats = [t for t in campaigns if t.get("campaign_name") == campaign]
                activities.append({
                    "type": "campaign",
                    "name": campaign,
                    "status": "ongoing",
                    "indicators": len(campaign_threats),
                    "description": f"Monitoring {len(campaign_threats)} indicators associated with this campaign"
                })
        
        # Ongoing incidents
        if incidents:
            active_incidents = [i for i in incidents if i.get("status") in ["open", "investigating"]]
            if active_incidents:
                activities.append({
                    "type": "incidents",
                    "name": "Active Security Incidents",
                    "status": "investigating",
                    "count": len(active_incidents),
                    "description": f"{len(active_incidents)} incidents under active investigation"
                })
        
        return activities
    
    def _identify_critical_findings(
        self,
        assets: List[Dict[str, Any]],
        vulnerabilities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify critical findings requiring immediate attention"""
        findings = []
        
        # Critical vulnerabilities with active exploitation
        for vuln in vulnerabilities:
            if vuln.get("severity") == "critical":
                # Check if there's threat intel about this CVE
                cve_id = vuln.get("id")
                related_threats = [
                    t for t in threats
                    if t.get("cve_id") == cve_id or cve_id in t.get("related_cves", [])
                ]
                
                if related_threats and any(t.get("active_exploitation") for t in related_threats):
                    findings.append({
                        "severity": "critical",
                        "type": "vulnerability",
                        "title": f"Critical vulnerability under active exploitation",
                        "description": vuln.get("title", "Unknown vulnerability"),
                        "cve_id": cve_id,
                        "cvss_score": vuln.get("cvss_score"),
                        "action_required": "Immediate patching required",
                        "timeline": "24 hours"
                    })
        
        # Internet-facing assets with critical vulnerabilities
        internet_assets = [a for a in assets if "internet-facing" in a.get("tags", [])]
        for asset in internet_assets:
            asset_vulns = [v for v in vulnerabilities if v.get("asset_id") == asset.get("id")]
            critical_vulns = [v for v in asset_vulns if v.get("severity") == "critical"]
            
            if critical_vulns:
                findings.append({
                    "severity": "critical",
                    "type": "exposed_asset",
                    "title": f"Internet-facing asset with {len(critical_vulns)} critical vulnerabilities",
                    "description": f"Asset {asset.get('value')} exposed with critical vulnerabilities",
                    "asset_id": asset.get("id"),
                    "asset_value": asset.get("value"),
                    "vulnerability_count": len(critical_vulns),
                    "action_required": "Remediate or isolate immediately",
                    "timeline": "24-48 hours"
                })
        
        # Targeted threat actor activity
        targeted_threats = [
            t for t in threats
            if t.get("targeting_organization") or t.get("targeting_industry")
        ]
        if targeted_threats:
            threat_actors = set(t.get("threat_actor") for t in targeted_threats if t.get("threat_actor"))
            if threat_actors:
                findings.append({
                    "severity": "high",
                    "type": "targeted_activity",
                    "title": "Organization or industry targeted by threat actors",
                    "description": f"Threat actors {', '.join(threat_actors)} showing targeting patterns",
                    "threat_actors": list(threat_actors),
                    "indicator_count": len(targeted_threats),
                    "action_required": "Enhanced monitoring and defensive posture",
                    "timeline": "Ongoing"
                })
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        findings.sort(key=lambda x: severity_order.get(x["severity"], 4))
        
        return findings[:10]
    
    def _generate_recommendations(
        self,
        critical_findings: List[Dict[str, Any]],
        threat_landscape: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on critical findings
        if critical_findings:
            critical_count = len([f for f in critical_findings if f.get("severity") == "critical"])
            if critical_count > 0:
                recommendations.append({
                    "priority": "urgent",
                    "category": "vulnerability_management",
                    "action": "Emergency Patching",
                    "description": f"Address {critical_count} critical findings within 24-48 hours",
                    "timeline": "24-48 hours"
                })
        
        # Based on threat landscape
        threat_level = threat_landscape.get("threat_level", "moderate")
        if threat_level in ["critical", "high"]:
            recommendations.append({
                "priority": "high",
                "category": "monitoring",
                "action": "Enhanced Monitoring",
                "description": "Increase monitoring and alerting given elevated threat landscape",
                "timeline": "Immediate"
            })
        
        # Active exploitation
        if threat_landscape.get("active_threats", 0) > 0:
            recommendations.append({
                "priority": "high",
                "category": "threat_hunting",
                "action": "Threat Hunting",
                "description": "Conduct proactive hunt for indicators of compromise",
                "timeline": "1-3 days"
            })
        
        # General recommendations
        recommendations.append({
            "priority": "medium",
            "category": "posture",
            "action": "Security Posture Review",
            "description": "Review and update security controls based on current threat landscape",
            "timeline": "7 days"
        })
        
        recommendations.append({
            "priority": "medium",
            "category": "intelligence",
            "action": "Intelligence Sharing",
            "description": "Share relevant indicators with industry partners and ISACs",
            "timeline": "Ongoing"
        })
        
        return recommendations
    
    def _calculate_metrics(
        self,
        assets: List[Dict[str, Any]],
        vulnerabilities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]],
        incidents: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Calculate key metrics for the brief"""
        return {
            "total_assets": len(assets),
            "internet_facing_assets": len([a for a in assets if "internet-facing" in a.get("tags", [])]),
            "total_vulnerabilities": len(vulnerabilities),
            "critical_vulnerabilities": len([v for v in vulnerabilities if v.get("severity") == "critical"]),
            "high_vulnerabilities": len([v for v in vulnerabilities if v.get("severity") == "high"]),
            "total_threats": len(threats),
            "active_exploitation": len([t for t in threats if t.get("active_exploitation")]),
            "threat_actors": len(set(t.get("threat_actor") for t in threats if t.get("threat_actor"))),
            "incidents": len(incidents) if incidents else 0,
            "open_incidents": len([i for i in (incidents or []) if i.get("status") == "open"])
        }
    
    def _list_sources(self, threats: List[Dict[str, Any]]) -> List[str]:
        """List intelligence sources used"""
        sources = set()
        for threat in threats:
            source = threat.get("source")
            if source:
                sources.add(source)
        
        return sorted(list(sources)) if sources else ["Internal Collection", "OSINT", "Threat Feeds"]
