#!/usr/bin/env python3
"""
NXT Research Agent - Analysis Layer

Applies doctoral-level construction economics analysis to validated findings.
Uses Claude to generate rigorous analysis with proper academic methodology.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from anthropic import Anthropic


class AnalysisLayer:
    """
    Doctoral-level analysis of infrastructure research findings.
    
    Methodology based on construction economics principles:
    - Schedule Performance Index (SPI) analysis
    - Cost Variance (CV) tracking
    - Earned Value Management (EVM) concepts
    - Risk-adjusted timeline forecasting
    """
    
    # Analysis prompt template for Claude
    ANALYSIS_PROMPT = """You are a doctoral-level analyst specializing in construction economics and infrastructure development. Your analysis must meet academic publication standards with rigorous methodology.

FINDING TO ANALYZE:
Project: {project_name} ({project_id})
Category: {category}
Source: {source_name} ({source_type})
Publication Date: {publication_date}
Credibility Score: {credibility_score}

CONTENT:
{extracted_text}

CURRENT PROJECT DATA:
- Velocity Score: {current_velocity}
- Health Status: {health_status}
- Capital Committed: ${capital_committed:,.0f}
- Capital Deployed: ${capital_deployed:,.0f}
- Original Target: {original_target}
- Current Target: {current_target}
- Workforce: {workforce_current}/{workforce_target}
- Grid Queue: {grid_queue_years} years

ANALYSIS REQUIREMENTS:

1. FACTUAL VERIFICATION
- Cross-reference the finding against the current project data
- Identify any inconsistencies with known project status
- Flag if the finding contradicts established facts or company statements

2. VELOCITY IMPACT ASSESSMENT
Assess impact on each of the four velocity factors (scale: -10 to +10 points each):
- Timeline Adherence: Does this affect production timeline?
- Funding Security: Does this impact financial stability or capital deployment?
- Construction Progress: Does this indicate acceleration or delays in physical construction?
- Operator Stability: Does this affect the company's ability to execute?

3. SYSTEMIC IMPLICATIONS
Does this finding have broader implications for:
- Portfolio-wide infrastructure metrics?
- Grid interconnection or power constraints?
- Regional workforce availability?
- Supply chain dependencies?
- Policy or regulatory environment?

4. CONFIDENCE ASSESSMENT
- Confidence level: high (85%+), medium (60-84%), or low (<60%)
- Key assumptions made in your analysis
- What additional data would increase confidence?

5. RECOMMENDED ACTIONS
Based on your analysis, specify:
- Should the velocity score change? By how much and why?
- Should the health status change?
- What should be added to the project's RAID file?
- Any early warnings to flag?

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "summary": "One paragraph executive summary of the finding's significance",
    "factual_verification": {{
        "verified": true/false,
        "inconsistencies": ["list any inconsistencies found"],
        "notes": "additional verification notes"
    }},
    "velocity_impact": {{
        "timeline_adherence": {{"change": 0, "rationale": "explanation"}},
        "funding_security": {{"change": 0, "rationale": "explanation"}},
        "construction_progress": {{"change": 0, "rationale": "explanation"}},
        "operator_stability": {{"change": 0, "rationale": "explanation"}},
        "net_change": 0
    }},
    "systemic_implications": {{
        "portfolio_metrics": ["any portfolio-level impacts"],
        "infrastructure_constraints": ["grid/power impacts"],
        "workforce": ["labor market impacts"],
        "policy_risk": ["regulatory impacts"],
        "supply_chain": ["supply chain impacts"]
    }},
    "confidence": {{
        "level": "high/medium/low",
        "score": 0-100,
        "assumptions": ["key assumptions"],
        "data_gaps": ["what additional data would help"]
    }},
    "recommended_updates": {{
        "velocity_score": {{
            "current": {current_velocity},
            "proposed": 0,
            "change_reason": "explanation or null if no change"
        }},
        "health_status": {{
            "current": "{health_status}",
            "proposed": "same or new status",
            "change_reason": "explanation or null if no change"
        }},
        "raid_file": {{
            "risks": [{{"description": "", "severity": "high/medium/low", "mitigation": ""}}],
            "actions": [{{"description": "", "owner": "", "due": ""}}],
            "issues": [{{"description": "", "impact": "", "resolution": ""}}],
            "decisions": [{{"description": "", "rationale": "", "date": ""}}]
        }},
        "early_warnings": ["any alerts to flag"],
        "milestones": [{{"description": "", "target_date": "", "status": ""}}]
    }}
}}"""

    def __init__(self, anthropic_client: Anthropic):
        """Initialize the analysis layer."""
        self.client = anthropic_client
    
    def analyze_finding(self, finding: Dict, project_data: Dict) -> Dict:
        """
        Apply doctoral-level analysis to a validated finding.
        
        Args:
            finding: Validated research finding
            project_data: Current project data from velocity_scores.json
            
        Returns:
            Analysis dict with velocity impact, recommendations, etc.
        """
        # Build prompt with finding and project context
        prompt = self._build_analysis_prompt(finding, project_data)
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            # Parse JSON response
            analysis = self._parse_analysis_response(response_text)
            
            # Add metadata
            analysis["analysis_id"] = f"A-{finding['finding_id']}"
            analysis["analyzed_at"] = datetime.utcnow().isoformat()
            analysis["model_used"] = "claude-sonnet-4-5-20250929"
            
            return analysis
            
        except Exception as e:
            print(f"    Analysis failed: {e}")
            return self._create_fallback_analysis(finding, project_data)
    
    def _build_analysis_prompt(self, finding: Dict, project_data: Dict) -> str:
        """Build the analysis prompt with all context."""
        raw_data = finding.get("raw_data", {})
        
        # Handle missing project data gracefully
        current_velocity = project_data.get("velocity_score", 50)
        health_status = project_data.get("health_status", "unknown")
        
        return self.ANALYSIS_PROMPT.format(
            project_name=finding.get("project_name", "Unknown"),
            project_id=finding.get("project_id", "Unknown"),
            category=finding.get("category", "general"),
            source_name=raw_data.get("source_name", "Unknown"),
            source_type=raw_data.get("source_type", "secondary"),
            publication_date=raw_data.get("publication_date", "Unknown"),
            credibility_score=finding.get("credibility", {}).get("score", 50),
            extracted_text=raw_data.get("extracted_text", "")[:2000],
            current_velocity=current_velocity,
            health_status=health_status,
            capital_committed=project_data.get("capital_committed", 0),
            capital_deployed=project_data.get("capital_deployed", 0),
            original_target=project_data.get("original_production_date", "Unknown"),
            current_target=project_data.get("current_production_date", "Unknown"),
            workforce_current=project_data.get("workforce_current", 0),
            workforce_target=project_data.get("workforce_target", 0),
            grid_queue_years=project_data.get("grid_queue_years", 0)
        )
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse Claude's JSON response."""
        # Try to extract JSON from response
        try:
            # Find JSON block
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text
            
            return json.loads(json_str.strip())
            
        except json.JSONDecodeError as e:
            print(f"    JSON parse error: {e}")
            # Try to salvage what we can
            return self._extract_partial_analysis(response_text)
    
    def _extract_partial_analysis(self, response_text: str) -> Dict:
        """Extract what we can from a malformed response."""
        analysis = {
            "summary": "",
            "velocity_impact": {"net_change": 0},
            "confidence": {"level": "low", "score": 40},
            "recommended_updates": {
                "velocity_score": {"proposed": None, "change_reason": None},
                "health_status": {"proposed": None, "change_reason": None},
                "raid_file": {"risks": [], "actions": [], "issues": [], "decisions": []},
                "early_warnings": [],
                "milestones": []
            },
            "parse_error": True,
            "raw_response": response_text[:1000]
        }
        
        # Try to extract summary
        if "summary" in response_text.lower():
            lines = response_text.split("\n")
            for i, line in enumerate(lines):
                if "summary" in line.lower() and i + 1 < len(lines):
                    analysis["summary"] = lines[i + 1].strip('" :,')
                    break
        
        return analysis
    
    def _create_fallback_analysis(self, finding: Dict, project_data: Dict) -> Dict:
        """Create minimal analysis when Claude API fails."""
        return {
            "analysis_id": f"A-{finding['finding_id']}",
            "analyzed_at": datetime.utcnow().isoformat(),
            "summary": f"Analysis pending for {finding.get('project_name', 'unknown project')} finding",
            "factual_verification": {
                "verified": False,
                "inconsistencies": [],
                "notes": "Automated analysis unavailable. Manual review required."
            },
            "velocity_impact": {
                "timeline_adherence": {"change": 0, "rationale": "Pending manual review"},
                "funding_security": {"change": 0, "rationale": "Pending manual review"},
                "construction_progress": {"change": 0, "rationale": "Pending manual review"},
                "operator_stability": {"change": 0, "rationale": "Pending manual review"},
                "net_change": 0
            },
            "systemic_implications": {
                "portfolio_metrics": [],
                "infrastructure_constraints": [],
                "workforce": [],
                "policy_risk": [],
                "supply_chain": []
            },
            "confidence": {
                "level": "low",
                "score": 30,
                "assumptions": ["Analysis unavailable"],
                "data_gaps": ["Full analysis required"]
            },
            "recommended_updates": {
                "velocity_score": {
                    "current": project_data.get("velocity_score", 50),
                    "proposed": None,
                    "change_reason": None
                },
                "health_status": {
                    "current": project_data.get("health_status", "unknown"),
                    "proposed": None,
                    "change_reason": None
                },
                "raid_file": {
                    "risks": [],
                    "actions": [],
                    "issues": [],
                    "decisions": []
                },
                "early_warnings": [],
                "milestones": []
            },
            "api_error": True
        }
    
    def batch_analyze(self, findings: List[Dict], 
                      velocity_scores: Dict) -> List[Dict]:
        """
        Analyze multiple findings efficiently.
        
        Groups findings by project for better context and
        implements rate limiting.
        """
        analyzed = []
        
        # Group by project
        by_project = {}
        for finding in findings:
            project_id = finding.get("project_id", "unknown")
            if project_id not in by_project:
                by_project[project_id] = []
            by_project[project_id].append(finding)
        
        # Analyze each project's findings
        for project_id, project_findings in by_project.items():
            project_data = velocity_scores.get("scores", {}).get(project_id, {})
            
            for finding in project_findings:
                analysis = self.analyze_finding(finding, project_data)
                finding["analysis"] = analysis
                analyzed.append(finding)
        
        return analyzed
    
    def calculate_velocity_score(self, project_data: Dict, 
                                  adjustments: Dict) -> int:
        """
        Calculate new velocity score with adjustments.
        
        Uses the four-factor methodology:
        - Timeline Adherence (25%)
        - Funding Security (25%)
        - Construction Progress (25%)
        - Operator Stability (25%)
        
        Plus delay penalty and ahead-of-schedule bonus.
        """
        # Get current factor scores
        current_factors = project_data.get("factor_scores", {})
        
        timeline = current_factors.get("timeline_adherence", 50)
        funding = current_factors.get("funding_security", 50)
        construction = current_factors.get("construction_progress", 50)
        operator = current_factors.get("operator_stability", 50)
        
        # Apply adjustments
        timeline += adjustments.get("timeline_adherence", {}).get("change", 0)
        funding += adjustments.get("funding_security", {}).get("change", 0)
        construction += adjustments.get("construction_progress", {}).get("change", 0)
        operator += adjustments.get("operator_stability", {}).get("change", 0)
        
        # Clamp factor scores to 0-100
        timeline = max(0, min(100, timeline))
        funding = max(0, min(100, funding))
        construction = max(0, min(100, construction))
        operator = max(0, min(100, operator))
        
        # Calculate base score (average)
        base_score = (timeline + funding + construction + operator) / 4
        
        # Apply delay penalty
        delay_penalty = project_data.get("delay_penalty", 0)
        
        # Apply ahead bonus
        ahead_bonus = project_data.get("ahead_bonus", 0)
        
        final_score = base_score - delay_penalty + ahead_bonus
        
        return max(0, min(100, int(final_score)))
    
    def determine_health_status(self, velocity_score: int) -> str:
        """Determine health status from velocity score."""
        if velocity_score >= 80:
            return "executing"
        elif velocity_score >= 65:
            return "on_track"
        elif velocity_score >= 50:
            return "monitoring"
        elif velocity_score >= 35:
            return "distressed"
        elif velocity_score > 0:
            return "critical"
        else:
            return "terminated"


class WeeklySummaryGenerator:
    """Generates the AI Weekly Summary for the Tools tab."""
    
    def __init__(self, anthropic_client: Anthropic):
        """Initialize the summary generator."""
        self.client = anthropic_client
    
    def generate_summary(self, run_log: Dict, 
                         applied_findings: List[Dict],
                         portfolio_metrics: Dict) -> str:
        """
        Generate executive summary of weekly research cycle.
        
        Args:
            run_log: Statistics from the research run
            applied_findings: Findings that were applied
            portfolio_metrics: Current portfolio metrics
            
        Returns:
            Markdown-formatted executive summary
        """
        prompt = f"""You are generating the weekly executive summary for the NXT Infrastructure Velocity Report. 
Write for a C-suite audience with expertise in infrastructure investment and construction economics.

THIS WEEK'S RESEARCH FINDINGS:
- Findings discovered: {run_log.get('findings_discovered', 0)}
- Findings validated: {run_log.get('findings_validated', 0)}
- Findings applied: {run_log.get('findings_applied', 0)}
- Projects updated: {len(run_log.get('projects_updated', []))}
- Velocity changes: {len(run_log.get('velocity_changes', []))}

KEY FINDINGS APPLIED:
{self._format_key_findings(applied_findings)}

PORTFOLIO STATUS:
- Total projects: {portfolio_metrics.get('portfolio_totals', {}).get('total_projects', 54)}
- Capital committed: {portfolio_metrics.get('portfolio_totals', {}).get('total_capital_committed_formatted', '$1.76T')}
- At-risk or worse: {portfolio_metrics.get('at_risk_metrics', {}).get('at_risk_or_worse_pct', 0)}%
- Portfolio velocity: {portfolio_metrics.get('portfolio_velocity', {}).get('current_score', 54)}

Generate a 3-4 paragraph executive summary covering:
1. Most significant development this week (lead with impact)
2. Portfolio health trajectory (improving/declining/stable)
3. Emerging risks or opportunities requiring attention
4. Key milestones to watch in the coming week

Write in a direct, factual style. No speculation. Cite specific projects and data points.
Do not use bullet points or lists. Write in flowing prose paragraphs."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            return f"Weekly summary generation failed: {e}"
    
    def _format_key_findings(self, findings: List[Dict]) -> str:
        """Format key findings for the summary prompt."""
        if not findings:
            return "No significant findings this week."
        
        formatted = []
        for f in findings[:10]:  # Top 10 findings
            project = f.get("project_name", "Unknown")
            category = f.get("category", "general")
            summary = f.get("analysis", {}).get("summary", "")[:200]
            
            formatted.append(f"- {project} ({category}): {summary}")
        
        return "\n".join(formatted)


if __name__ == "__main__":
    # Test the analysis layer
    from anthropic import Anthropic
    
    client = Anthropic()
    analyzer = AnalysisLayer(client)
    
    test_finding = {
        "finding_id": "F-TEST-001",
        "project_id": "SE002",
        "project_name": "Intel Ohio",
        "category": "timeline",
        "raw_data": {
            "source_url": "https://www.sec.gov/...",
            "source_type": "primary",
            "source_name": "SEC 10-K Filing",
            "publication_date": "2026-01-25",
            "extracted_text": """Intel announced in its annual report that the Ohio 
            manufacturing campus timeline has been adjusted. The company now expects 
            initial production from Fab 1 in 2030-2031, citing weak chip demand and 
            the need to optimize capital allocation. Only $1.5 billion of the planned 
            $20 billion has been deployed to date."""
        },
        "credibility": {"score": 92}
    }
    
    test_project_data = {
        "velocity_score": 32,
        "health_status": "critical",
        "capital_committed": 20000000000,
        "capital_deployed": 1500000000,
        "original_production_date": "2025-01-01",
        "current_production_date": "2030-06-01",
        "workforce_current": 450,
        "workforce_target": 3000,
        "grid_queue_years": 4.2
    }
    
    print("Analyzing finding...")
    analysis = analyzer.analyze_finding(test_finding, test_project_data)
    print(json.dumps(analysis, indent=2))
