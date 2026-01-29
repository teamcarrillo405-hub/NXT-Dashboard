#!/usr/bin/env python3
"""
Update Layer for NXT Research Agent.
Applies validated and analyzed findings to dashboard data files.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class UpdateLayer:
    """
    Applies research findings to dashboard JSON files.
    Handles RAID updates, velocity recalculation, and portfolio aggregation.
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize update layer."""
        self.data_dir = Path(data_dir)
        
        # Health status thresholds
        self.health_thresholds = {
            "executing": (80, 100),
            "on_track": (65, 79),
            "monitoring": (50, 64),
            "distressed": (35, 49),
            "critical": (0, 34),
        }
    
    def apply_updates(self, finding: Dict, velocity_scores: Dict, 
                      research_log: Dict) -> bool:
        """
        Apply a finding's recommended updates to data files.
        
        Args:
            finding: Analyzed finding with recommendations
            velocity_scores: Current velocity scores data
            research_log: Research log for audit trail
            
        Returns:
            True if updates were applied successfully
        """
        try:
            project_id = finding["project_id"]
            analysis = finding.get("analysis", {})
            
            if not analysis:
                return False
            
            # 1. Update velocity score
            impact = analysis.get("velocity_impact", {})
            if impact.get("net_change", 0) != 0:
                self._update_velocity_score(
                    velocity_scores, 
                    project_id, 
                    impact
                )
            
            # 2. Update research log
            finding["status"] = "applied"
            finding["applied_timestamp"] = datetime.utcnow().isoformat()
            
            # 3. Update statistics
            self._update_statistics(research_log, finding)
            
            return True
            
        except Exception as e:
            print(f"    Update failed: {e}")
            return False
    
    def _update_velocity_score(self, velocity_scores: Dict, 
                                project_id: str, impact: Dict):
        """Update velocity score for a project."""
        if project_id not in velocity_scores.get("scores", {}):
            return
        
        project_scores = velocity_scores["scores"][project_id]
        
        # Get current values
        current_score = project_scores.get("velocity_score", 50)
        current_factors = project_scores.get("factor_scores", {})
        
        # Apply factor impacts (multiply by 2 for sensitivity)
        new_factors = {}
        for factor in ["timeline_adherence", "funding_security", 
                       "construction_progress", "operator_stability"]:
            current = current_factors.get(factor, 50)
            change = impact.get(factor, 0) * 2
            new_factors[factor] = max(0, min(100, current + change))
        
        # Calculate new base score
        base_score = sum(new_factors.values()) / 4
        
        # Apply delay penalty
        delay_penalty = project_scores.get("delay_penalty", 0)
        new_score = max(0, min(100, base_score - delay_penalty))
        
        # Determine health status
        new_health = self._determine_health(new_score)
        
        # Record previous score
        previous_scores = project_scores.get("previous_scores", [])
        previous_scores.insert(0, {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "score": current_score
        })
        previous_scores = previous_scores[:10]  # Keep last 10
        
        # Calculate trend
        if len(previous_scores) >= 2:
            trend = new_score - previous_scores[0]["score"]
            trend_str = f"+{trend}" if trend > 0 else str(trend)
        else:
            trend_str = "0"
        
        # Update project scores
        project_scores["velocity_score"] = round(new_score, 1)
        project_scores["health_status"] = new_health
        project_scores["factor_scores"] = new_factors
        project_scores["trend_30d"] = trend_str
        project_scores["previous_scores"] = previous_scores
        
        # Update timestamp
        velocity_scores["last_updated"] = datetime.utcnow().isoformat()
    
    def _determine_health(self, score: float) -> str:
        """Determine health status from velocity score."""
        for status, (min_score, max_score) in self.health_thresholds.items():
            if min_score <= score <= max_score:
                return status
        return "critical"
    
    def _update_statistics(self, research_log: Dict, finding: Dict):
        """Update research log statistics."""
        stats = research_log.get("statistics", {})
        
        # Update totals
        stats["total_findings_applied"] = stats.get("total_findings_applied", 0) + 1
        
        # Update source breakdown
        source_name = finding["raw_data"]["source_name"].lower()
        source_breakdown = stats.get("source_breakdown", {})
        
        if "sec" in source_name:
            source_breakdown["sec_filings"] = source_breakdown.get("sec_filings", 0) + 1
        elif "chips" in source_name:
            source_breakdown["chips_portal"] = source_breakdown.get("chips_portal", 0) + 1
        elif any(grid in source_name for grid in ["pjm", "ercot", "caiso", "miso"]):
            source_breakdown["grid_operators"] = source_breakdown.get("grid_operators", 0) + 1
        elif "reuters" in source_name:
            source_breakdown["news_reuters"] = source_breakdown.get("news_reuters", 0) + 1
        elif "wsj" in source_name:
            source_breakdown["news_wsj"] = source_breakdown.get("news_wsj", 0) + 1
        else:
            source_breakdown["other"] = source_breakdown.get("other", 0) + 1
        
        stats["source_breakdown"] = source_breakdown
        research_log["statistics"] = stats
    
    def recalculate_portfolio_metrics(self, projects: Dict, 
                                       velocity_scores: Dict) -> Dict:
        """
        Recalculate all portfolio-level metrics.
        
        Args:
            projects: Projects registry
            velocity_scores: Updated velocity scores
            
        Returns:
            Updated portfolio metrics
        """
        metrics = self._load_json("portfolio_metrics.json")
        scores = velocity_scores.get("scores", {})
        projects_list = projects.get("projects", [])
        
        # Reset counters
        health_counts = {
            "executing": 0,
            "on_track": 0,
            "monitoring": 0,
            "distressed": 0,
            "critical": 0,
            "terminated": 0
        }
        
        total_capital = 0
        total_velocity = 0
        project_count = 0
        
        top_improvers = []
        biggest_declines = []
        sector_data = {}
        
        for project in projects_list:
            project_id = project["id"]
            project_scores = scores.get(project_id, {})
            
            # Count health status
            health = project_scores.get("health_status", "monitoring")
            health_counts[health] = health_counts.get(health, 0) + 1
            
            # Sum capital
            capital = project.get("capital_committed", 0)
            total_capital += capital
            
            # Sum velocity (for average)
            velocity = project_scores.get("velocity_score", 50)
            if health != "terminated":
                total_velocity += velocity
                project_count += 1
            
            # Track trends
            trend_str = project_scores.get("trend_30d", "0")
            try:
                if trend_str == "NEW":
                    trend = 100  # New projects sort to top
                else:
                    trend = int(trend_str.replace("+", ""))
            except ValueError:
                trend = 0
            
            trend_entry = {
                "project_id": project_id,
                "project_name": project.get("name", project_id),
                "sector": project.get("sector", "other"),
                "score": velocity,
                "change": trend_str
            }
            
            if trend > 0:
                top_improvers.append(trend_entry)
            elif trend < 0:
                biggest_declines.append(trend_entry)
            
            # Aggregate sector data
            sector = project.get("sector", "other")
            if sector not in sector_data:
                sector_data[sector] = {
                    "total_velocity": 0,
                    "count": 0,
                    "capital": 0,
                    "executing": 0,
                    "on_track": 0,
                    "distressed_or_worse": 0
                }
            
            sector_data[sector]["total_velocity"] += velocity
            sector_data[sector]["count"] += 1
            sector_data[sector]["capital"] += capital
            
            if health == "executing":
                sector_data[sector]["executing"] += 1
            elif health == "on_track":
                sector_data[sector]["on_track"] += 1
            elif health in ["distressed", "critical", "terminated"]:
                sector_data[sector]["distressed_or_worse"] += 1
        
        # Sort and limit trends
        top_improvers.sort(key=lambda x: -int(x["change"].replace("+", "").replace("NEW", "100")))
        biggest_declines.sort(key=lambda x: int(x["change"]))
        
        # Update portfolio totals
        metrics["portfolio_totals"]["total_capital_committed"] = total_capital
        metrics["portfolio_totals"]["total_capital_committed_formatted"] = self._format_currency(total_capital)
        metrics["portfolio_totals"]["total_projects"] = len(projects_list)
        metrics["portfolio_totals"]["active_projects"] = len(projects_list) - health_counts["terminated"]
        metrics["portfolio_totals"]["terminated_projects"] = health_counts["terminated"]
        
        # Update health distribution
        total = len(projects_list)
        metrics["portfolio_health"] = {
            status: {
                "count": count,
                "percentage": round(count / total * 100) if total > 0 else 0
            }
            for status, count in health_counts.items()
        }
        
        # Calculate at-risk percentage
        at_risk_count = (health_counts["monitoring"] + health_counts["distressed"] + 
                         health_counts["critical"])
        at_risk_pct = round(at_risk_count / total * 100) if total > 0 else 0
        metrics["at_risk_metrics"]["at_risk_or_worse_count"] = at_risk_count
        metrics["at_risk_metrics"]["at_risk_or_worse_pct"] = at_risk_pct
        
        # Update portfolio velocity
        if project_count > 0:
            metrics["portfolio_velocity"]["current_score"] = round(total_velocity / project_count, 1)
        
        # Update trends
        metrics["top_improvers_30d"] = [
            {**entry, "rank": i+1} for i, entry in enumerate(top_improvers[:5])
        ]
        metrics["biggest_declines_30d"] = [
            {**entry, "rank": i+1} for i, entry in enumerate(biggest_declines[:5])
        ]
        
        # Update sector performance
        for sector, data in sector_data.items():
            if sector in metrics.get("sector_performance", {}):
                if data["count"] > 0:
                    metrics["sector_performance"][sector]["velocity_score"] = round(
                        data["total_velocity"] / data["count"], 1
                    )
                metrics["sector_performance"][sector]["total_capital"] = data["capital"]
                metrics["sector_performance"][sector]["project_counts"] = {
                    "executing": data["executing"],
                    "on_track": data["on_track"],
                    "distressed_or_worse": data["distressed_or_worse"]
                }
        
        # Update timestamp
        metrics["last_updated"] = datetime.utcnow().isoformat()
        
        # Save updated metrics
        self._save_json("portfolio_metrics.json", metrics)
        
        return metrics
    
    def _format_currency(self, amount: int) -> str:
        """Format large currency amounts."""
        if amount >= 1_000_000_000_000:
            return f"${amount / 1_000_000_000_000:.2f}T"
        elif amount >= 1_000_000_000:
            return f"${amount / 1_000_000_000:.1f}B"
        elif amount >= 1_000_000:
            return f"${amount / 1_000_000:.1f}M"
        else:
            return f"${amount:,.0f}"
    
    def _load_json(self, filename: str) -> Dict:
        """Load a JSON file from data directory."""
        filepath = self.data_dir / filename
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_json(self, filename: str, data: Dict):
        """Save a JSON file to data directory."""
        filepath = self.data_dir / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    def generate_weekly_summary(self, run_log: Dict, 
                                 findings_applied: List[Dict]) -> str:
        """
        Generate executive summary text for the dashboard.
        
        Args:
            run_log: Completed run log
            findings_applied: List of applied findings
            
        Returns:
            Markdown-formatted summary text
        """
        date_str = datetime.utcnow().strftime("%B %d, %Y")
        
        # Count significant changes
        velocity_increases = len([
            c for c in run_log.get("velocity_changes", [])
            if c.get("change", 0) > 0
        ])
        velocity_decreases = len([
            c for c in run_log.get("velocity_changes", [])
            if c.get("change", 0) < 0
        ])
        
        summary = f"""## Weekly Research Summary
**Week Ending {date_str}**

### Research Activity
- **Projects Researched:** {run_log.get('projects_researched', 0)}
- **New Findings Discovered:** {run_log.get('findings_discovered', 0)}
- **Findings Validated:** {run_log.get('findings_validated', 0)}
- **Updates Applied:** {run_log.get('findings_applied', 0)}

### Velocity Changes
- **Projects Improved:** {velocity_increases}
- **Projects Declined:** {velocity_decreases}
- **Projects Updated:** {len(run_log.get('projects_updated', []))}

### Key Findings
"""
        
        # Add top findings
        for finding in findings_applied[:5]:
            project_name = finding.get("project_name", "Unknown")
            category = finding.get("category", "general")
            summary += f"- **{project_name}** ({category}): "
            summary += finding.get("analysis", {}).get("summary", "Update applied")[:100]
            summary += "\n"
        
        summary += f"""
### Data Quality
- **Credibility Threshold:** 60/100
- **Rejection Rate:** {run_log.get('findings_rejected', 0)} findings
- **Errors:** {len(run_log.get('errors', []))}

*Generated by NXT Research Agent v1.0*
"""
        
        return summary


if __name__ == "__main__":
    # Test update layer
    updater = UpdateLayer()
    
    # Load test data
    velocity_scores = updater._load_json("velocity_scores.json")
    projects = updater._load_json("projects.json")
    
    if velocity_scores and projects:
        metrics = updater.recalculate_portfolio_metrics(projects, velocity_scores)
        print(f"Portfolio velocity: {metrics['portfolio_velocity']['current_score']}")
        print(f"At-risk projects: {metrics['at_risk_metrics']['at_risk_or_worse_pct']}%")
