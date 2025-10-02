"""
Executive Briefing Generator

Generates executive-level intelligence briefings:
- High-level strategic overview
- Key judgments
- Critical risks
- Business impact
- Strategic recommendations
- Minimal technical jargon
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ExecutiveBriefingGenerator:
    """
    Generates executive-level intelligence briefings
    
    Focuses on strategic insights and business impact
    """
    
    def __init__(self):
        self.logger = logger
    
    async def generate_executive_briefing(
        self,
        time_period: str = "weekly",
        assets: Optional[List[Dict[str, Any]]] = None,
        vulnerabilities: Optional[List[Dict[str, Any]]] = None,
        threats: Optional[List[Dict[str, Any]]] = None,
        incidents: Optional[List[Dict[str, Any]]] = None,
        risk_metrics: Optional[Dict[str, Any]] = None,
        previous_briefing: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate executive briefing
        
        Args:
            time_period: daily, weekly, monthly
            assets: Asset data
            vulnerabilities: Vulnerability data
            threats: Threat intelligence
            incidents: Security incidents
            risk_metrics: Risk metrics
            previous_briefing: Previous briefing for trend analysis
        
        Returns:
            Executive briefing
        """
        # Executive summary
        exec_summary = self._generate_executive_summary(
            assets, vulnerabilities, threats, incidents, risk_metrics
        )
        
        # Key judgments (strategic)
        key_judgments = self._generate_strategic_judgments(
            vulnerabilities, threats, incidents, risk_metrics
        )
        
        # Security posture assessment
        posture = self._assess_security_posture(
            assets, vulnerabilities, threats, risk_metrics
        )
        
        # Critical risks
        critical_risks = self._identify_critical_risks(
            assets, vulnerabilities, threats, risk_metrics
        )
        
        # Business impact
        business_impact = self._assess_business_impact(
            critical_risks, incidents, posture
        )
        
        # Trends
        trends = self._analyze_trends(
            vulnerabilities, threats, incidents, previous_briefing
        )
        
        # Strategic recommendations
        recommendations = self._generate_strategic_recommendations(
            posture, critical_risks, business_impact
        )
        
        # Metrics (executive-friendly)
        metrics = self._format_executive_metrics(
            assets, vulnerabilities, threats, incidents, risk_metrics
        )
        
        return {
            "classification": "UNCLASSIFIED",
            "product_type": "Executive Intelligence Briefing",
            "period": time_period.capitalize(),
            "generated_at": datetime.now().isoformat(),
            "executive_summary": exec_summary,
            "key_judgments": key_judgments,
            "security_posture": posture,
            "critical_risks": critical_risks,
            "business_impact": business_impact,
            "trends": trends,
            "strategic_recommendations": recommendations,
            "metrics": metrics,
            "bottom_line": self._generate_bottom_line(posture, critical_risks)
        }
    
    def _generate_executive_summary(
        self,
        assets: Optional[List[Dict[str, Any]]],
        vulnerabilities: Optional[List[Dict[str, Any]]],
        threats: Optional[List[Dict[str, Any]]],
        incidents: Optional[List[Dict[str, Any]]],
        risk_metrics: Optional[Dict[str, Any]]
    ) -> str:
        """Generate executive summary paragraph"""
        parts = []
        
        # Opening
        parts.append("This briefing provides strategic oversight of the organization's cyber security posture.")
        
        # Overall assessment
        if risk_metrics:
            overall_risk = risk_metrics.get("overall_risk", 5.0)
            if overall_risk >= 8.0:
                parts.append("The organization currently faces ELEVATED RISK requiring immediate executive attention.")
            elif overall_risk >= 6.0:
                parts.append("The organization maintains a MODERATE risk posture with areas requiring improvement.")
            else:
                parts.append("The organization maintains a STABLE security posture with routine risks.")
        
        # Critical items
        if vulnerabilities:
            critical_count = len([v for v in vulnerabilities if v.get("severity") == "critical"])
            if critical_count > 0:
                parts.append(f"{critical_count} critical security gaps require immediate remediation.")
        
        # Incidents
        if incidents:
            open_incidents = len([i for i in incidents if i.get("status") == "open"])
            if open_incidents > 0:
                parts.append(f"{open_incidents} active security incidents under investigation.")
        
        # Threats
        if threats:
            active_threats = len([t for t in threats if t.get("active_exploitation")])
            if active_threats > 5:
                parts.append("Elevated threat activity observed across multiple vectors.")
        
        return " ".join(parts)
    
    def _generate_strategic_judgments(
        self,
        vulnerabilities: Optional[List[Dict[str, Any]]],
        threats: Optional[List[Dict[str, Any]]],
        incidents: Optional[List[Dict[str, Any]]],
        risk_metrics: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate strategic-level judgments"""
        judgments = []
        
        # Risk posture judgment
        if risk_metrics:
            overall_risk = risk_metrics.get("overall_risk", 5.0)
            if overall_risk >= 8.0:
                judgments.append(
                    "We assess with HIGH confidence that the organization faces elevated cyber risk "
                    "requiring immediate strategic intervention and resource allocation."
                )
            elif overall_risk >= 6.0:
                judgments.append(
                    "We assess with MODERATE confidence that current cyber risk levels are manageable "
                    "but require sustained attention and investment."
                )
        
        # Threat landscape judgment
        if threats:
            threat_actors = set(t.get("threat_actor") for t in threats if t.get("threat_actor"))
            if len(threat_actors) > 3:
                judgments.append(
                    f"We assess with MODERATE confidence that {len(threat_actors)} distinct threat actors "
                    "demonstrate interest in similar organizations, indicating persistent threat environment."
                )
            
            targeted = [t for t in threats if t.get("targeting_industry") or t.get("targeting_organization")]
            if targeted:
                judgments.append(
                    "We assess with HIGH confidence that the organization's industry sector remains under "
                    "active targeting by adversaries seeking intellectual property or operational disruption."
                )
        
        # Vulnerability management judgment
        if vulnerabilities:
            critical_vulns = len([v for v in vulnerabilities if v.get("severity") == "critical"])
            total_vulns = len(vulnerabilities)
            
            if critical_vulns > 10:
                judgments.append(
                    f"We assess with HIGH confidence that vulnerability management processes require "
                    f"improvement, with {critical_vulns} critical exposures present."
                )
        
        # Incident trends
        if incidents and len(incidents) > 5:
            judgments.append(
                f"We assess with MODERATE confidence that incident volume ({len(incidents)} events) "
                "suggests either increased threat activity or improved detection capabilities."
            )
        
        return judgments[:4]  # Top 4 strategic judgments
    
    def _assess_security_posture(
        self,
        assets: Optional[List[Dict[str, Any]]],
        vulnerabilities: Optional[List[Dict[str, Any]]],
        threats: Optional[List[Dict[str, Any]]],
        risk_metrics: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess overall security posture"""
        # Determine posture level
        if risk_metrics:
            overall_risk = risk_metrics.get("overall_risk", 5.0)
            if overall_risk >= 8.0:
                posture_level = "at_risk"
                posture_color = "red"
                posture_label = "AT RISK"
            elif overall_risk >= 6.0:
                posture_level = "needs_improvement"
                posture_color = "yellow"
                posture_label = "NEEDS IMPROVEMENT"
            else:
                posture_level = "acceptable"
                posture_color = "green"
                posture_label = "ACCEPTABLE"
        else:
            posture_level = "unknown"
            posture_color = "gray"
            posture_label = "UNDER ASSESSMENT"
        
        # Strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if assets:
            monitored_assets = len([a for a in assets if "monitored" in a.get("tags", [])])
            if monitored_assets / len(assets) > 0.7:
                strengths.append("Strong asset monitoring coverage")
            else:
                weaknesses.append("Limited asset monitoring coverage")
        
        if vulnerabilities:
            critical_vulns = len([v for v in vulnerabilities if v.get("severity") == "critical"])
            if critical_vulns == 0:
                strengths.append("No critical vulnerabilities present")
            else:
                weaknesses.append(f"{critical_vulns} critical vulnerabilities requiring remediation")
            
            patched_vulns = len([v for v in vulnerabilities if v.get("patch_available")])
            if patched_vulns / len(vulnerabilities) > 0.8:
                strengths.append("Patches available for most vulnerabilities")
        
        if threats:
            active_count = len([t for t in threats if t.get("active_exploitation")])
            if active_count > 5:
                weaknesses.append("Multiple active threats in environment")
        
        return {
            "posture_level": posture_level,
            "posture_label": posture_label,
            "posture_color": posture_color,
            "assessment": self._posture_assessment_text(posture_level),
            "strengths": strengths[:3],
            "weaknesses": weaknesses[:3],
            "trend": self._determine_posture_trend(risk_metrics)
        }
    
    def _posture_assessment_text(self, posture_level: str) -> str:
        """Generate posture assessment text"""
        assessments = {
            "at_risk": "The organization's security posture is AT RISK. Immediate action required to address critical exposures and reduce organizational risk.",
            "needs_improvement": "The organization's security posture NEEDS IMPROVEMENT. While no immediate crisis exists, sustained effort required to strengthen defenses.",
            "acceptable": "The organization maintains an ACCEPTABLE security posture. Continue current efforts with routine improvements.",
            "unknown": "Security posture assessment in progress. Comprehensive evaluation required."
        }
        return assessments.get(posture_level, "Posture assessment unavailable")
    
    def _determine_posture_trend(self, risk_metrics: Optional[Dict[str, Any]]) -> str:
        """Determine if posture is improving, stable, or degrading"""
        # This would compare to previous briefing in production
        # For now, return stable
        return "stable"
    
    def _identify_critical_risks(
        self,
        assets: Optional[List[Dict[str, Any]]],
        vulnerabilities: Optional[List[Dict[str, Any]]],
        threats: Optional[List[Dict[str, Any]]],
        risk_metrics: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify top critical risks (executive perspective)"""
        risks = []
        
        # Critical vulnerabilities
        if vulnerabilities:
            critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
            if critical_vulns:
                risks.append({
                    "risk_level": "critical",
                    "category": "vulnerability_exposure",
                    "title": f"{len(critical_vulns)} Critical Security Vulnerabilities",
                    "business_impact": "Potential for system compromise, data breach, or service outage",
                    "probability": "high" if len(critical_vulns) > 5 else "medium",
                    "financial_impact": "Significant" if len(critical_vulns) > 10 else "Moderate",
                    "recommendation": "Immediate remediation program required"
                })
        
        # Targeted threats
        if threats:
            targeted = [t for t in threats if t.get("targeting_organization") or t.get("targeting_industry")]
            if targeted:
                threat_actors = set(t.get("threat_actor") for t in targeted if t.get("threat_actor"))
                risks.append({
                    "risk_level": "high",
                    "category": "targeted_threat",
                    "title": "Active Threat Actor Targeting",
                    "business_impact": "Risk of coordinated attack, intellectual property theft, or operational disruption",
                    "probability": "medium",
                    "financial_impact": "High",
                    "threat_actors": list(threat_actors),
                    "recommendation": "Enhanced monitoring and defensive posture required"
                })
        
        # Internet exposure
        if assets:
            internet_assets = [a for a in assets if "internet-facing" in a.get("tags", [])]
            critical_assets = [a for a in assets if a.get("criticality") == "critical"]
            exposed_critical = [
                a for a in internet_assets
                if a.get("criticality") == "critical"
            ]
            
            if exposed_critical:
                risks.append({
                    "risk_level": "high",
                    "category": "exposure",
                    "title": f"{len(exposed_critical)} Critical Assets Internet-Exposed",
                    "business_impact": "Direct attack risk to mission-critical systems",
                    "probability": "medium",
                    "financial_impact": "High",
                    "recommendation": "Review necessity of internet exposure, implement additional controls"
                })
        
        # Sort by risk level
        risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        risks.sort(key=lambda x: risk_order.get(x["risk_level"], 4))
        
        return risks[:5]  # Top 5 risks
    
    def _assess_business_impact(
        self,
        critical_risks: List[Dict[str, Any]],
        incidents: Optional[List[Dict[str, Any]]],
        posture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess business impact of security posture"""
        # Calculate potential business impact
        critical_risk_count = len([r for r in critical_risks if r.get("risk_level") == "critical"])
        high_risk_count = len([r for r in critical_risks if r.get("risk_level") == "high"])
        
        if critical_risk_count > 0:
            impact_level = "high"
            impact_description = "Significant business risk present requiring immediate executive action"
        elif high_risk_count > 2:
            impact_level = "medium"
            impact_description = "Moderate business risk requiring prioritized remediation"
        else:
            impact_level = "low"
            impact_description = "Limited immediate business risk, routine security operations adequate"
        
        # Areas of concern
        concerns = []
        for risk in critical_risks:
            if risk.get("business_impact"):
                concerns.append(risk["business_impact"])
        
        # Potential consequences
        consequences = []
        if critical_risk_count > 0 or high_risk_count > 0:
            consequences.extend([
                "Data breach and loss of customer trust",
                "Regulatory penalties and compliance violations",
                "Operational disruption and revenue loss",
                "Reputational damage and brand impact"
            ])
        
        return {
            "impact_level": impact_level,
            "impact_description": impact_description,
            "key_concerns": concerns[:3],
            "potential_consequences": consequences,
            "estimated_exposure": self._estimate_financial_exposure(critical_risks)
        }
    
    def _estimate_financial_exposure(self, risks: List[Dict[str, Any]]) -> str:
        """Estimate potential financial exposure"""
        # Simplified estimation logic
        critical_count = len([r for r in risks if r.get("risk_level") == "critical"])
        high_count = len([r for r in risks if r.get("risk_level") == "high"])
        
        if critical_count > 3:
            return "High (>$1M potential impact)"
        elif critical_count > 0 or high_count > 3:
            return "Moderate ($100K-$1M potential impact)"
        else:
            return "Low (<$100K potential impact)"
    
    def _analyze_trends(
        self,
        vulnerabilities: Optional[List[Dict[str, Any]]],
        threats: Optional[List[Dict[str, Any]]],
        incidents: Optional[List[Dict[str, Any]]],
        previous_briefing: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze security trends"""
        trends = {
            "vulnerability_trend": "stable",
            "threat_trend": "stable",
            "incident_trend": "stable",
            "summary": []
        }
        
        # In production, this would compare to previous briefing
        # For now, provide static analysis
        
        if vulnerabilities:
            recent_critical = len([
                v for v in vulnerabilities
                if v.get("severity") == "critical" and self._is_recent(v.get("discovered"), days=7)
            ])
            if recent_critical > 3:
                trends["vulnerability_trend"] = "increasing"
                trends["summary"].append("Vulnerability discovery rate increasing")
        
        if threats:
            recent_threats = len([
                t for t in threats
                if self._is_recent(t.get("observed_at"), days=7)
            ])
            total_threats = len(threats)
            if recent_threats / max(total_threats, 1) > 0.5:
                trends["threat_trend"] = "increasing"
                trends["summary"].append("Threat activity escalating")
        
        if not trends["summary"]:
            trends["summary"].append("Security metrics remain stable")
        
        return trends
    
    def _is_recent(self, timestamp: Optional[str], days: int = 7) -> bool:
        """Check if timestamp is recent"""
        if not timestamp:
            return False
        
        try:
            if isinstance(timestamp, str):
                ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                ts = timestamp
            
            cutoff = datetime.now() - timedelta(days=days)
            return ts.replace(tzinfo=None) > cutoff
        except Exception:
            return False
    
    def _generate_strategic_recommendations(
        self,
        posture: Dict[str, Any],
        critical_risks: List[Dict[str, Any]],
        business_impact: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate strategic recommendations for executives"""
        recommendations = []
        
        # Based on posture
        posture_level = posture.get("posture_level")
        if posture_level == "at_risk":
            recommendations.append({
                "priority": "immediate",
                "category": "strategic",
                "action": "Convene Security Council",
                "rationale": "Critical security posture requires executive oversight and resource allocation",
                "expected_outcome": "Coordinated response to reduce organizational risk",
                "investment_required": "High"
            })
        
        # Based on critical risks
        if critical_risks:
            critical_count = len([r for r in critical_risks if r.get("risk_level") == "critical"])
            if critical_count > 0:
                recommendations.append({
                    "priority": "high",
                    "category": "risk_mitigation",
                    "action": "Emergency Remediation Program",
                    "rationale": f"{critical_count} critical risks require immediate remediation",
                    "expected_outcome": "Reduce critical risk exposure by 80% within 30 days",
                    "investment_required": "Moderate"
                })
        
        # Based on business impact
        impact_level = business_impact.get("impact_level")
        if impact_level == "high":
            recommendations.append({
                "priority": "high",
                "category": "business_continuity",
                "action": "Review Business Continuity Plans",
                "rationale": "High business impact scenarios require validated response procedures",
                "expected_outcome": "Improved resilience and incident response capability",
                "investment_required": "Low"
            })
        
        # General strategic recommendations
        recommendations.extend([
            {
                "priority": "medium",
                "category": "investment",
                "action": "Security Program Assessment",
                "rationale": "Regular assessment ensures security investment alignment with business risk",
                "expected_outcome": "Optimized security spending and improved risk management",
                "investment_required": "Moderate"
            },
            {
                "priority": "medium",
                "category": "governance",
                "action": "Board-Level Cyber Risk Reporting",
                "rationale": "Executive visibility into cyber risk enables informed strategic decisions",
                "expected_outcome": "Enhanced governance and risk oversight",
                "investment_required": "Low"
            }
        ])
        
        return recommendations[:5]
    
    def _format_executive_metrics(
        self,
        assets: Optional[List[Dict[str, Any]]],
        vulnerabilities: Optional[List[Dict[str, Any]]],
        threats: Optional[List[Dict[str, Any]]],
        incidents: Optional[List[Dict[str, Any]]],
        risk_metrics: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format metrics for executive consumption"""
        metrics = {}
        
        # Risk score (0-10)
        if risk_metrics:
            metrics["overall_risk_score"] = {
                "value": round(risk_metrics.get("overall_risk", 5.0), 1),
                "scale": "0-10",
                "interpretation": "Higher is worse"
            }
        
        # Critical items
        if vulnerabilities:
            critical_vulns = len([v for v in vulnerabilities if v.get("severity") == "critical"])
            metrics["critical_vulnerabilities"] = {
                "value": critical_vulns,
                "status": "red" if critical_vulns > 5 else "yellow" if critical_vulns > 0 else "green"
            }
        
        # Active threats
        if threats:
            active_threats = len([t for t in threats if t.get("active_exploitation")])
            metrics["active_threats"] = {
                "value": active_threats,
                "status": "red" if active_threats > 10 else "yellow" if active_threats > 0 else "green"
            }
        
        # Open incidents
        if incidents:
            open_incidents = len([i for i in incidents if i.get("status") == "open"])
            metrics["open_incidents"] = {
                "value": open_incidents,
                "status": "red" if open_incidents > 5 else "yellow" if open_incidents > 0 else "green"
            }
        
        # Asset coverage
        if assets:
            monitored = len([a for a in assets if "monitored" in a.get("tags", [])])
            coverage_pct = int((monitored / len(assets)) * 100) if assets else 0
            metrics["monitoring_coverage"] = {
                "value": f"{coverage_pct}%",
                "status": "green" if coverage_pct > 80 else "yellow" if coverage_pct > 50 else "red"
            }
        
        return metrics
    
    def _generate_bottom_line(
        self,
        posture: Dict[str, Any],
        critical_risks: List[Dict[str, Any]]
    ) -> str:
        """Generate bottom-line assessment for executives"""
        posture_level = posture.get("posture_level")
        critical_risk_count = len([r for r in critical_risks if r.get("risk_level") == "critical"])
        
        if posture_level == "at_risk" or critical_risk_count > 3:
            return (
                "BOTTOM LINE: The organization faces elevated cyber security risk requiring immediate "
                "executive attention and resource allocation. Recommend convening security council to "
                "coordinate response efforts."
            )
        elif posture_level == "needs_improvement" or critical_risk_count > 0:
            return (
                "BOTTOM LINE: The organization's cyber security posture requires improvement. While no "
                "immediate crisis exists, sustained executive support needed to strengthen defenses and "
                "reduce organizational risk."
            )
        else:
            return (
                "BOTTOM LINE: The organization maintains an acceptable cyber security posture. Continue "
                "current security programs with routine improvements and sustained investment."
            )
