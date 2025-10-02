"""
Indications & Warning (I&W) Alert System

Generates tactical warning alerts for:
- Imminent threats
- Active exploitation
- Critical vulnerabilities
- Suspicious activity patterns
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class IndicationsWarningSystem:
    """
    Indications & Warning (I&W) alert generation
    
    Follows IC I&W methodology for tactical warnings
    """
    
    # Alert severity levels
    SEVERITY_LEVELS = {
        "critical": {
            "level": 1,
            "label": "CRITICAL WARNING",
            "response_time": "immediate",
            "color": "red"
        },
        "high": {
            "level": 2,
            "label": "HIGH WARNING",
            "response_time": "1-4 hours",
            "color": "orange"
        },
        "medium": {
            "level": 3,
            "label": "MODERATE WARNING",
            "response_time": "24 hours",
            "color": "yellow"
        },
        "low": {
            "level": 4,
            "label": "LOW WARNING",
            "response_time": "72 hours",
            "color": "green"
        }
    }
    
    def __init__(self):
        self.logger = logger
    
    async def generate_iw_alerts(
        self,
        assets: List[Dict[str, Any]],
        vulnerabilities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]],
        risk_scores: Optional[List[Dict[str, Any]]] = None,
        attack_paths: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate I&W alerts based on current intelligence
        
        Args:
            assets: Asset data
            vulnerabilities: Vulnerability data
            threats: Threat intelligence
            risk_scores: Risk assessment data
            attack_paths: Attack path analysis
        
        Returns:
            List of I&W alerts
        """
        alerts = []
        
        # Critical vulnerability alerts
        alerts.extend(self._check_critical_vulnerabilities(vulnerabilities, threats))
        
        # Active exploitation alerts
        alerts.extend(self._check_active_exploitation(threats, vulnerabilities))
        
        # Targeted activity alerts
        alerts.extend(self._check_targeted_activity(threats, assets))
        
        # Exposed asset alerts
        alerts.extend(self._check_exposed_assets(assets, vulnerabilities))
        
        # Attack path alerts
        if attack_paths:
            alerts.extend(self._check_attack_paths(attack_paths))
        
        # Risk score alerts
        if risk_scores:
            alerts.extend(self._check_risk_scores(risk_scores))
        
        # Pattern-based alerts
        alerts.extend(self._check_patterns(threats))
        
        # Sort by severity
        alerts.sort(key=lambda x: self.SEVERITY_LEVELS[x["severity"]]["level"])
        
        # Add alert IDs and timestamps
        for idx, alert in enumerate(alerts, 1):
            alert["alert_id"] = f"IW-{datetime.now().strftime('%Y%m%d')}-{idx:04d}"
            alert["generated_at"] = datetime.now().isoformat()
        
        return alerts
    
    def _check_critical_vulnerabilities(
        self,
        vulnerabilities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for critical vulnerabilities requiring immediate attention"""
        alerts = []
        
        critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
        
        for vuln in critical_vulns:
            cve_id = vuln.get("id")
            
            # Check if actively exploited
            related_threats = [
                t for t in threats
                if t.get("cve_id") == cve_id or cve_id in t.get("related_cves", [])
            ]
            
            is_exploited = any(t.get("active_exploitation") for t in related_threats)
            has_weaponized = vuln.get("exploit_status") == "weaponized"
            
            if is_exploited or has_weaponized:
                alerts.append({
                    "severity": "critical",
                    "type": "critical_vulnerability",
                    "title": f"CRITICAL: {cve_id} Under Active Exploitation",
                    "description": vuln.get("title", "Critical vulnerability detected"),
                    "indicators": {
                        "cve_id": cve_id,
                        "cvss_score": vuln.get("cvss_score"),
                        "exploit_available": has_weaponized,
                        "active_exploitation": is_exploited
                    },
                    "impact": "Potential system compromise, data breach, or service disruption",
                    "recommendation": "Immediate patching or mitigation required",
                    "response_time": "immediate",
                    "affected_assets": vuln.get("affected_assets", [])
                })
        
        return alerts
    
    def _check_active_exploitation(
        self,
        threats: List[Dict[str, Any]],
        vulnerabilities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for active exploitation in the wild"""
        alerts = []
        
        active_threats = [t for t in threats if t.get("active_exploitation")]
        
        if active_threats:
            # Group by threat actor
            by_actor = {}
            for threat in active_threats:
                actor = threat.get("threat_actor", "Unknown")
                if actor not in by_actor:
                    by_actor[actor] = []
                by_actor[actor].append(threat)
            
            for actor, actor_threats in by_actor.items():
                # Check if any affect our vulnerabilities
                cves_exploited = set()
                for threat in actor_threats:
                    if threat.get("cve_id"):
                        cves_exploited.add(threat["cve_id"])
                    cves_exploited.update(threat.get("related_cves", []))
                
                # Check if we have these vulnerabilities
                our_vulns = [
                    v for v in vulnerabilities
                    if v.get("id") in cves_exploited
                ]
                
                if our_vulns:
                    alerts.append({
                        "severity": "critical",
                        "type": "active_exploitation",
                        "title": f"CRITICAL: {actor} Actively Exploiting Vulnerabilities Present in Environment",
                        "description": f"{actor} observed exploiting {len(cves_exploited)} CVEs, {len(our_vulns)} present in our environment",
                        "indicators": {
                            "threat_actor": actor,
                            "cves_exploited": list(cves_exploited),
                            "our_affected_cves": [v.get("id") for v in our_vulns],
                            "indicator_count": len(actor_threats)
                        },
                        "impact": "Direct threat to organizational assets",
                        "recommendation": "Immediate defensive measures and threat hunting required",
                        "response_time": "immediate"
                    })
                else:
                    # Still alert but lower severity
                    alerts.append({
                        "severity": "high",
                        "type": "active_exploitation",
                        "title": f"HIGH: {actor} Active Exploitation Detected (Not Currently Affecting Environment)",
                        "description": f"{actor} exploiting {len(cves_exploited)} CVEs - monitor for indicators",
                        "indicators": {
                            "threat_actor": actor,
                            "cves_exploited": list(cves_exploited),
                            "indicator_count": len(actor_threats)
                        },
                        "impact": "Potential future risk",
                        "recommendation": "Monitor for related indicators and update defenses",
                        "response_time": "1-4 hours"
                    })
        
        return alerts
    
    def _check_targeted_activity(
        self,
        threats: List[Dict[str, Any]],
        assets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for targeted activity against organization"""
        alerts = []
        
        # Organization-specific targeting
        org_targeted = [t for t in threats if t.get("targeting_organization")]
        if org_targeted:
            threat_actors = set(t.get("threat_actor") for t in org_targeted if t.get("threat_actor"))
            
            alerts.append({
                "severity": "critical",
                "type": "targeted_activity",
                "title": "CRITICAL: Organization Under Direct Targeting",
                "description": f"Threat actors {', '.join(threat_actors)} showing direct targeting patterns",
                "indicators": {
                    "threat_actors": list(threat_actors),
                    "indicator_count": len(org_targeted),
                    "targeting_type": "organization_specific"
                },
                "impact": "Coordinated attack campaign probable",
                "recommendation": "Activate incident response team, enhanced monitoring, threat hunting",
                "response_time": "immediate"
            })
        
        # Industry targeting
        industry_targeted = [t for t in threats if t.get("targeting_industry")]
        if industry_targeted and not org_targeted:  # Don't duplicate
            alerts.append({
                "severity": "high",
                "type": "targeted_activity",
                "title": "HIGH: Industry-Wide Targeting Campaign Detected",
                "description": f"Threat actors targeting industry - {len(industry_targeted)} indicators",
                "indicators": {
                    "threat_actors": list(set(t.get("threat_actor") for t in industry_targeted if t.get("threat_actor"))),
                    "indicator_count": len(industry_targeted),
                    "targeting_type": "industry"
                },
                "impact": "Increased risk to organizational assets",
                "recommendation": "Review security posture, monitor for industry-specific TTPs",
                "response_time": "1-4 hours"
            })
        
        return alerts
    
    def _check_exposed_assets(
        self,
        assets: List[Dict[str, Any]],
        vulnerabilities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for exposed assets with vulnerabilities"""
        alerts = []
        
        internet_assets = [a for a in assets if "internet-facing" in a.get("tags", [])]
        
        for asset in internet_assets:
            asset_vulns = [
                v for v in vulnerabilities
                if v.get("asset_id") == asset.get("id")
            ]
            
            critical_vulns = [v for v in asset_vulns if v.get("severity") == "critical"]
            high_vulns = [v for v in asset_vulns if v.get("severity") == "high"]
            
            if critical_vulns:
                alerts.append({
                    "severity": "critical",
                    "type": "exposed_vulnerability",
                    "title": f"CRITICAL: Internet-Facing Asset with {len(critical_vulns)} Critical Vulnerabilities",
                    "description": f"Asset {asset.get('value')} exposed to internet with critical vulnerabilities",
                    "indicators": {
                        "asset_id": asset.get("id"),
                        "asset_value": asset.get("value"),
                        "asset_type": asset.get("type"),
                        "critical_vulnerabilities": len(critical_vulns),
                        "high_vulnerabilities": len(high_vulns),
                        "cve_ids": [v.get("id") for v in critical_vulns]
                    },
                    "impact": "Direct exploitation risk from internet",
                    "recommendation": "Immediate remediation or isolation required",
                    "response_time": "immediate"
                })
            elif len(high_vulns) >= 3:
                alerts.append({
                    "severity": "high",
                    "type": "exposed_vulnerability",
                    "title": f"HIGH: Internet-Facing Asset with Multiple High-Severity Vulnerabilities",
                    "description": f"Asset {asset.get('value')} has {len(high_vulns)} high-severity vulnerabilities",
                    "indicators": {
                        "asset_id": asset.get("id"),
                        "asset_value": asset.get("value"),
                        "high_vulnerabilities": len(high_vulns)
                    },
                    "impact": "Elevated exploitation risk",
                    "recommendation": "Prioritize patching within 48 hours",
                    "response_time": "1-4 hours"
                })
        
        return alerts
    
    def _check_attack_paths(
        self,
        attack_paths: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for high-risk attack paths"""
        alerts = []
        
        # High likelihood, low detectability paths
        dangerous_paths = [
            p for p in attack_paths
            if p.get("likelihood", 0) > 0.7 and p.get("detectability", 1) < 0.3
        ]
        
        if dangerous_paths:
            for path in dangerous_paths[:3]:  # Top 3
                alerts.append({
                    "severity": "high",
                    "type": "attack_path",
                    "title": f"HIGH: High-Probability Attack Path with Low Detectability",
                    "description": f"Attack path to {path.get('target')} is highly exploitable with low detection chance",
                    "indicators": {
                        "source": path.get("source"),
                        "target": path.get("target"),
                        "likelihood": path.get("likelihood"),
                        "detectability": path.get("detectability"),
                        "path_length": path.get("path_length")
                    },
                    "impact": "Potential undetected compromise",
                    "recommendation": "Implement monitoring along attack path, consider network segmentation",
                    "response_time": "1-4 hours"
                })
        
        return alerts
    
    def _check_risk_scores(
        self,
        risk_scores: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for critical risk scores"""
        alerts = []
        
        critical_assets = [r for r in risk_scores if r.get("severity") == "critical"]
        
        if len(critical_assets) >= 5:
            alerts.append({
                "severity": "high",
                "type": "risk_assessment",
                "title": f"HIGH: {len(critical_assets)} Assets at Critical Risk Level",
                "description": "Multiple assets assessed at critical risk - coordinated response required",
                "indicators": {
                    "critical_asset_count": len(critical_assets),
                    "top_assets": [
                        {
                            "asset_id": a.get("asset_id"),
                            "risk_score": a.get("overall_risk")
                        }
                        for a in sorted(critical_assets, key=lambda x: x.get("overall_risk", 0), reverse=True)[:5]
                    ]
                },
                "impact": "Elevated organizational risk posture",
                "recommendation": "Coordinate remediation efforts across critical assets",
                "response_time": "1-4 hours"
            })
        
        return alerts
    
    def _check_patterns(
        self,
        threats: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for suspicious patterns in threat data"""
        alerts = []
        
        # Sudden spike in activity
        recent_24h = [
            t for t in threats
            if self._is_recent(t.get("observed_at"), hours=24)
        ]
        
        recent_7d = [
            t for t in threats
            if self._is_recent(t.get("observed_at"), hours=168)
        ]
        
        # If 24h activity is > 50% of 7-day activity, it's a spike
        if len(recent_7d) > 0 and len(recent_24h) > (len(recent_7d) * 0.5):
            alerts.append({
                "severity": "medium",
                "type": "anomaly",
                "title": "MODERATE: Significant Spike in Threat Intelligence",
                "description": f"50%+ increase in threat activity in last 24 hours",
                "indicators": {
                    "recent_24h": len(recent_24h),
                    "recent_7d": len(recent_7d),
                    "increase_percentage": ((len(recent_24h) / (len(recent_7d) / 7)) - 1) * 100
                },
                "impact": "Possible campaign escalation",
                "recommendation": "Review recent intelligence for coordinated activity",
                "response_time": "24 hours"
            })
        
        return alerts
    
    def _is_recent(self, timestamp: Optional[str], hours: int = 24) -> bool:
        """Check if timestamp is within recent hours"""
        if not timestamp:
            return False
        
        try:
            if isinstance(timestamp, str):
                ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                ts = timestamp
            
            cutoff = datetime.now() - timedelta(hours=hours)
            return ts.replace(tzinfo=None) > cutoff
        except Exception:
            return False
    
    async def generate_iw_summary(
        self,
        alerts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary of I&W alerts"""
        if not alerts:
            return {
                "classification": "UNCLASSIFIED",
                "alert_status": "GREEN",
                "total_alerts": 0,
                "critical_alerts": 0,
                "message": "No active warnings at this time"
            }
        
        critical_count = len([a for a in alerts if a.get("severity") == "critical"])
        high_count = len([a for a in alerts if a.get("severity") == "high"])
        
        # Determine overall alert status
        if critical_count > 0:
            status = "RED"
            message = f"{critical_count} CRITICAL warnings require immediate attention"
        elif high_count > 0:
            status = "ORANGE"
            message = f"{high_count} HIGH warnings require urgent response"
        else:
            status = "YELLOW"
            message = "Moderate warnings present - monitor situation"
        
        return {
            "classification": "UNCLASSIFIED//FOUO",
            "alert_status": status,
            "total_alerts": len(alerts),
            "critical_alerts": critical_count,
            "high_alerts": high_count,
            "medium_alerts": len([a for a in alerts if a.get("severity") == "medium"]),
            "low_alerts": len([a for a in alerts if a.get("severity") == "low"]),
            "message": message,
            "generated_at": datetime.now().isoformat(),
            "alerts": alerts[:10]  # Top 10 alerts
        }
