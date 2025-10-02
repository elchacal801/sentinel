"""
Predictive Analytics

Forecasts future security events based on:
- Historical trends
- Threat intelligence patterns
- Asset behavior
- Industry patterns
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)


class PredictiveAnalytics:
    """
    Predictive analytics for security intelligence
    
    Analyzes trends and predicts future threats
    """
    
    def __init__(self):
        self.logger = logger
    
    async def predict_vulnerability_trends(
        self,
        historical_vulns: List[Dict[str, Any]],
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Predict vulnerability discovery trends
        
        Args:
            historical_vulns: Historical vulnerability data
            days_ahead: Days to forecast
        
        Returns:
            Trend predictions and forecasts
        """
        if not historical_vulns:
            return {
                "trend": "insufficient_data",
                "forecast": [],
                "confidence": "low"
            }
        
        # Group vulnerabilities by date
        vuln_timeline = self._build_timeline(historical_vulns, "discovered")
        
        # Calculate trend
        trend_direction = self._calculate_trend(vuln_timeline)
        
        # Calculate velocity (rate of change)
        velocity = self._calculate_velocity(vuln_timeline)
        
        # Generate forecast
        forecast = self._generate_forecast(vuln_timeline, days_ahead)
        
        # Identify patterns
        patterns = self._identify_patterns(vuln_timeline)
        
        return {
            "trend": trend_direction,
            "velocity": round(velocity, 2),
            "velocity_description": self._describe_velocity(velocity),
            "forecast": forecast,
            "patterns": patterns,
            "confidence": self._calculate_confidence(vuln_timeline),
            "analyzed_at": datetime.now().isoformat()
        }
    
    async def detect_anomalies(
        self,
        events: List[Dict[str, Any]],
        threshold_std: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous security events
        
        Uses statistical analysis to find outliers
        """
        if len(events) < 10:
            return []
        
        # Build time series
        timeline = self._build_timeline(events, "timestamp")
        
        # Calculate statistics
        values = list(timeline.values())
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Find anomalies (values beyond threshold standard deviations)
        anomalies = []
        for date, count in timeline.items():
            z_score = (count - mean) / stdev if stdev > 0 else 0
            
            if abs(z_score) > threshold_std:
                severity = "critical" if abs(z_score) > 3 else "high" if abs(z_score) > 2.5 else "medium"
                
                anomalies.append({
                    "date": date,
                    "event_count": count,
                    "expected_range": f"{mean - (threshold_std * stdev):.0f} - {mean + (threshold_std * stdev):.0f}",
                    "z_score": round(z_score, 2),
                    "severity": severity,
                    "type": "spike" if z_score > 0 else "drop",
                    "description": f"{'Spike' if z_score > 0 else 'Drop'} of {abs(count - mean):.0f} events ({abs(z_score):.1f}σ from normal)"
                })
        
        return sorted(anomalies, key=lambda x: abs(x["z_score"]), reverse=True)
    
    async def predict_attack_likelihood(
        self,
        asset: Dict[str, Any],
        threat_intel: List[Dict[str, Any]],
        historical_attacks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Predict likelihood of asset being attacked
        
        Based on:
        - Asset characteristics
        - Threat intelligence
        - Historical attack patterns
        """
        likelihood_factors = []
        
        # Factor 1: Asset exposure
        exposure_score = self._assess_exposure(asset)
        likelihood_factors.append(("exposure", exposure_score))
        
        # Factor 2: Asset criticality
        criticality_score = self._assess_criticality(asset)
        likelihood_factors.append(("criticality", criticality_score))
        
        # Factor 3: Current threat landscape
        threat_score = self._assess_threat_landscape(threat_intel)
        likelihood_factors.append(("threat_landscape", threat_score))
        
        # Factor 4: Historical targeting
        history_score = self._assess_historical_targeting(asset, historical_attacks)
        likelihood_factors.append(("historical_targeting", history_score))
        
        # Factor 5: Vulnerability count
        vuln_score = len(asset.get("vulnerabilities", [])) / 10.0  # Normalize to 0-1
        likelihood_factors.append(("vulnerabilities", min(1.0, vuln_score)))
        
        # Calculate weighted likelihood
        weights = {
            "exposure": 0.25,
            "criticality": 0.15,
            "threat_landscape": 0.30,
            "historical_targeting": 0.20,
            "vulnerabilities": 0.10
        }
        
        likelihood = sum(
            score * weights.get(factor, 0.2)
            for factor, score in likelihood_factors
        )
        
        # Determine time window
        time_window = self._predict_time_to_attack(likelihood)
        
        return {
            "asset_id": asset.get("id"),
            "likelihood": round(likelihood, 3),
            "likelihood_label": self._get_likelihood_label(likelihood),
            "predicted_timeframe": time_window,
            "factors": {factor: round(score, 3) for factor, score in likelihood_factors},
            "recommendations": self._generate_protection_recommendations(likelihood, asset),
            "confidence": "moderate",
            "predicted_at": datetime.now().isoformat()
        }
    
    async def identify_emerging_threats(
        self,
        recent_intel: List[Dict[str, Any]],
        historical_baseline: List[Dict[str, Any]],
        days_window: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Identify emerging threats by comparing recent activity to baseline
        """
        # Extract threat actors and malware from recent intel
        recent_actors = Counter(
            i.get("threat_actor") for i in recent_intel
            if i.get("threat_actor")
        )
        
        recent_malware = Counter(
            i.get("malware_family") for i in recent_intel
            if i.get("malware_family")
        )
        
        # Extract from historical baseline
        baseline_actors = Counter(
            i.get("threat_actor") for i in historical_baseline
            if i.get("threat_actor")
        )
        
        baseline_malware = Counter(
            i.get("malware_family") for i in historical_baseline
            if i.get("malware_family")
        )
        
        emerging_threats = []
        
        # Find new or significantly increased actors
        for actor, recent_count in recent_actors.items():
            baseline_count = baseline_actors.get(actor, 0)
            
            if baseline_count == 0:
                # Completely new actor
                emerging_threats.append({
                    "type": "threat_actor",
                    "name": actor,
                    "status": "new",
                    "recent_activity": recent_count,
                    "trend": "emerging",
                    "severity": "high" if recent_count > 5 else "medium"
                })
            elif recent_count > baseline_count * 2:
                # Significantly increased activity
                increase_pct = ((recent_count - baseline_count) / baseline_count) * 100
                emerging_threats.append({
                    "type": "threat_actor",
                    "name": actor,
                    "status": "escalating",
                    "recent_activity": recent_count,
                    "baseline_activity": baseline_count,
                    "increase_percentage": round(increase_pct, 1),
                    "trend": "escalating",
                    "severity": "high" if increase_pct > 300 else "medium"
                })
        
        # Find new or significantly increased malware
        for malware, recent_count in recent_malware.items():
            baseline_count = baseline_malware.get(malware, 0)
            
            if baseline_count == 0 and recent_count > 2:
                emerging_threats.append({
                    "type": "malware",
                    "name": malware,
                    "status": "new",
                    "recent_activity": recent_count,
                    "trend": "emerging",
                    "severity": "high" if recent_count > 10 else "medium"
                })
        
        return sorted(emerging_threats, key=lambda x: x.get("recent_activity", 0), reverse=True)
    
    async def forecast_risk_trajectory(
        self,
        current_risk: float,
        historical_risks: List[Tuple[datetime, float]],
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Forecast how risk will evolve over time
        """
        if len(historical_risks) < 5:
            return {
                "forecast": "insufficient_data",
                "confidence": "low"
            }
        
        # Calculate trend
        x = list(range(len(historical_risks)))
        y = [risk for _, risk in historical_risks]
        
        # Simple linear regression
        slope = self._calculate_slope(x, y)
        
        # Generate forecast points
        forecast_points = []
        for day in range(1, days_ahead + 1):
            forecasted_risk = current_risk + (slope * day)
            forecasted_risk = max(0.0, min(10.0, forecasted_risk))  # Clamp to 0-10
            
            forecast_points.append({
                "day": day,
                "date": (datetime.now() + timedelta(days=day)).isoformat(),
                "predicted_risk": round(forecasted_risk, 2)
            })
        
        # Determine trajectory
        if slope > 0.05:
            trajectory = "increasing"
            severity = "critical" if slope > 0.2 else "high" if slope > 0.1 else "medium"
        elif slope < -0.05:
            trajectory = "decreasing"
            severity = "low"
        else:
            trajectory = "stable"
            severity = "medium"
        
        return {
            "current_risk": round(current_risk, 2),
            "trajectory": trajectory,
            "severity": severity,
            "slope": round(slope, 4),
            "forecast": forecast_points,
            "peak_risk": round(max(p["predicted_risk"] for p in forecast_points), 2),
            "recommendation": self._trajectory_recommendation(trajectory, slope),
            "confidence": "moderate",
            "forecasted_at": datetime.now().isoformat()
        }
    
    # Helper methods
    
    def _build_timeline(
        self,
        events: List[Dict[str, Any]],
        date_field: str
    ) -> Dict[str, int]:
        """Build timeline of event counts by date"""
        timeline = defaultdict(int)
        
        for event in events:
            date = event.get(date_field)
            if date:
                if isinstance(date, str):
                    date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                
                date_key = date.strftime("%Y-%m-%d")
                timeline[date_key] += 1
        
        return dict(sorted(timeline.items()))
    
    def _calculate_trend(self, timeline: Dict[str, int]) -> str:
        """Calculate overall trend direction"""
        if len(timeline) < 3:
            return "insufficient_data"
        
        values = list(timeline.values())
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)
        
        if avg_second > avg_first * 1.2:
            return "increasing"
        elif avg_second < avg_first * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_velocity(self, timeline: Dict[str, int]) -> float:
        """Calculate rate of change"""
        if len(timeline) < 2:
            return 0.0
        
        values = list(timeline.values())
        
        # Calculate day-over-day changes
        changes = [values[i] - values[i-1] for i in range(1, len(values))]
        
        return statistics.mean(changes) if changes else 0.0
    
    def _describe_velocity(self, velocity: float) -> str:
        """Describe velocity in human terms"""
        if velocity > 5:
            return "rapidly_increasing"
        elif velocity > 2:
            return "increasing"
        elif velocity > -2:
            return "stable"
        elif velocity > -5:
            return "decreasing"
        else:
            return "rapidly_decreasing"
    
    def _generate_forecast(
        self,
        timeline: Dict[str, int],
        days_ahead: int
    ) -> List[Dict[str, Any]]:
        """Generate simple forecast"""
        if len(timeline) < 3:
            return []
        
        values = list(timeline.values())
        avg = statistics.mean(values)
        velocity = self._calculate_velocity(timeline)
        
        forecast = []
        for day in range(1, days_ahead + 1):
            predicted = max(0, avg + (velocity * day))
            forecast.append({
                "day": day,
                "predicted_count": round(predicted, 1)
            })
        
        return forecast
    
    def _identify_patterns(self, timeline: Dict[str, int]) -> List[str]:
        """Identify patterns in the timeline"""
        patterns = []
        
        if len(timeline) < 7:
            return patterns
        
        values = list(timeline.values())
        
        # Check for weekly patterns
        if len(values) >= 14:
            # Simple check: compare same day of week
            patterns.append("Analyzing for weekly patterns...")
        
        # Check for spikes
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        spikes = sum(1 for v in values if v > mean + (2 * stdev))
        if spikes > 0:
            patterns.append(f"Detected {spikes} spike(s) above normal")
        
        return patterns
    
    def _calculate_confidence(self, timeline: Dict[str, int]) -> str:
        """Calculate confidence in predictions"""
        if len(timeline) < 7:
            return "low"
        elif len(timeline) < 30:
            return "moderate"
        else:
            return "high"
    
    def _assess_exposure(self, asset: Dict[str, Any]) -> float:
        """Assess asset exposure (0-1)"""
        tags = asset.get("tags", [])
        
        if "internet-facing" in tags or "public" in tags:
            return 1.0
        elif "dmz" in tags:
            return 0.7
        elif "internal" in tags:
            return 0.3
        else:
            return 0.5
    
    def _assess_criticality(self, asset: Dict[str, Any]) -> float:
        """Assess asset criticality (0-1)"""
        criticality = asset.get("criticality", "medium")
        
        mapping = {
            "critical": 1.0,
            "high": 0.7,
            "medium": 0.5,
            "low": 0.3
        }
        
        return mapping.get(criticality, 0.5)
    
    def _assess_threat_landscape(self, threat_intel: List[Dict[str, Any]]) -> float:
        """Assess current threat landscape (0-1)"""
        if not threat_intel:
            return 0.3
        
        # Check for active campaigns
        active_campaigns = sum(
            1 for t in threat_intel
            if t.get("active_exploitation") or t.get("targeted_campaign")
        )
        
        return min(1.0, active_campaigns / 10.0 + 0.3)
    
    def _assess_historical_targeting(
        self,
        asset: Dict[str, Any],
        historical_attacks: List[Dict[str, Any]]
    ) -> float:
        """Assess historical targeting (0-1)"""
        asset_id = asset.get("id")
        
        # Count attacks on this asset
        attacks_on_asset = sum(
            1 for attack in historical_attacks
            if attack.get("target_asset_id") == asset_id
        )
        
        return min(1.0, attacks_on_asset / 5.0)
    
    def _predict_time_to_attack(self, likelihood: float) -> str:
        """Predict timeframe for potential attack"""
        if likelihood >= 0.8:
            return "within_days"
        elif likelihood >= 0.6:
            return "within_weeks"
        elif likelihood >= 0.4:
            return "within_months"
        else:
            return "beyond_quarter"
    
    def _get_likelihood_label(self, likelihood: float) -> str:
        """Get likelihood label"""
        if likelihood >= 0.8:
            return "very_high"
        elif likelihood >= 0.6:
            return "high"
        elif likelihood >= 0.4:
            return "moderate"
        elif likelihood >= 0.2:
            return "low"
        else:
            return "very_low"
    
    def _generate_protection_recommendations(
        self,
        likelihood: float,
        asset: Dict[str, Any]
    ) -> List[str]:
        """Generate protection recommendations"""
        recommendations = []
        
        if likelihood >= 0.7:
            recommendations.append("Implement 24/7 monitoring for this asset")
            recommendations.append("Consider moving to more secure network segment")
        
        if likelihood >= 0.5:
            recommendations.append("Ensure all patches are current")
            recommendations.append("Review and strengthen access controls")
        
        if "internet-facing" in asset.get("tags", []):
            recommendations.append("Consider WAF or additional perimeter defense")
        
        recommendations.append("Regular security assessments recommended")
        
        return recommendations
    
    def _calculate_slope(self, x: List[float], y: List[float]) -> float:
        """Calculate slope of linear regression"""
        n = len(x)
        if n < 2:
            return 0.0
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _trajectory_recommendation(self, trajectory: str, slope: float) -> str:
        """Generate recommendation based on trajectory"""
        if trajectory == "increasing":
            if slope > 0.2:
                return "URGENT: Risk rapidly increasing - immediate intervention required"
            else:
                return "Risk trending upward - review security posture"
        elif trajectory == "decreasing":
            return "Risk decreasing - current controls effective"
        else:
            return "Risk stable - maintain current security measures"
