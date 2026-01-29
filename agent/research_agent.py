#!/usr/bin/env python3
"""
NXT Infrastructure Velocity Report - Research Agent
Main entry point for weekly automated research cycle.

This agent:
1. Gathers new information about tracked infrastructure projects
2. Validates findings for credibility and deduplication
3. Analyzes impacts at doctoral-level rigor
4. Updates dashboard files automatically
"""

import json
import hashlib
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import time

from anthropic import Anthropic

# Import custom modules
from scrapers.sec_scraper import SECScraper
from scrapers.news_scraper import NewsScraper
from scrapers.chips_scraper import CHIPSScraper
from scrapers.grid_scraper import GridQueueScraper
from validation_layer import ValidationLayer
from analysis_layer import AnalysisLayer
from update_layer import UpdateLayer

# Configuration
CONFIG = {
    "data_dir": Path("data"),
    "logs_dir": Path("agent/logs"),
    "days_lookback": 7,
    "max_findings_per_project": 20,
    "credibility_threshold": 60,
    "api_delay_seconds": 1,  # Rate limiting
}


class NXTResearchAgent:
    """Main research agent orchestrator."""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize the research agent."""
        self.api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key)
        
        # Initialize components
        self.sec_scraper = SECScraper()
        self.news_scraper = NewsScraper()
        self.chips_scraper = CHIPSScraper()
        self.grid_scraper = GridQueueScraper()
        self.validator = ValidationLayer(self.client)
        self.analyzer = AnalysisLayer(self.client)
        self.updater = UpdateLayer()
        
        # Load data files
        self.projects = self._load_json("projects.json")
        self.research_log = self._load_json("research_log.json")
        self.velocity_scores = self._load_json("velocity_scores.json")
        
        # Initialize run
        self.run_id = datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
        self.run_log = self._init_run_log()
        
    def _load_json(self, filename: str) -> Dict:
        """Load a JSON data file."""
        filepath = CONFIG["data_dir"] / filename
        with open(filepath, "r") as f:
            return json.load(f)
    
    def _save_json(self, filename: str, data: Dict):
        """Save a JSON data file."""
        filepath = CONFIG["data_dir"] / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    def _init_run_log(self) -> Dict:
        """Initialize a new run log."""
        return {
            "run_id": self.run_id,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None,
            "status": "running",
            "projects_researched": 0,
            "findings_discovered": 0,
            "findings_validated": 0,
            "findings_applied": 0,
            "findings_rejected": 0,
            "rejection_reasons": {},
            "projects_updated": [],
            "velocity_changes": [],
            "health_status_changes": [],
            "errors": []
        }
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate MD5 hash of content for deduplication."""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_duplicate(self, finding: Dict) -> bool:
        """Check if finding is a duplicate."""
        content_hash = finding["raw_data"]["content_hash"]
        
        # Check exact hash match
        if content_hash in self.research_log.get("seen_hashes", []):
            return True
        
        # Check same URL and date
        for prior in self.research_log.get("findings", []):
            if (prior["raw_data"]["source_url"] == finding["raw_data"]["source_url"] and
                prior["raw_data"]["publication_date"] == finding["raw_data"]["publication_date"]):
                return True
        
        return False
    
    def research_project(self, project: Dict) -> List[Dict]:
        """Execute all research queries for a single project."""
        findings = []
        project_id = project["id"]
        project_name = project["name"]
        
        print(f"  Researching: {project_name}")
        
        # 1. SEC Filings (if company has ticker)
        if project.get("company_ticker"):
            try:
                sec_results = self.sec_scraper.search(
                    ticker=project["company_ticker"],
                    days_back=CONFIG["days_lookback"]
                )
                for result in sec_results:
                    finding = self._create_finding(
                        project_id=project_id,
                        project_name=project_name,
                        category="financial",
                        source_type="primary",
                        source_name=f"SEC {result['filing_type']}",
                        source_url=result["url"],
                        publication_date=result["filing_date"],
                        extracted_text=result["excerpt"]
                    )
                    findings.append(finding)
                time.sleep(CONFIG["api_delay_seconds"])
            except Exception as e:
                self.run_log["errors"].append(f"SEC search failed for {project_name}: {str(e)}")
        
        # 2. News Search
        try:
            for keyword in project.get("research_keywords", [project_name]):
                news_results = self.news_scraper.search(
                    query=keyword,
                    sources=project.get("news_sources", []),
                    days_back=CONFIG["days_lookback"]
                )
                for result in news_results:
                    finding = self._create_finding(
                        project_id=project_id,
                        project_name=project_name,
                        category=self._categorize_news(result["title"], result["content"]),
                        source_type="secondary",
                        source_name=result["source"],
                        source_url=result["url"],
                        publication_date=result["published_date"],
                        extracted_text=result["content"][:2000]  # Truncate
                    )
                    findings.append(finding)
                time.sleep(CONFIG["api_delay_seconds"])
        except Exception as e:
            self.run_log["errors"].append(f"News search failed for {project_name}: {str(e)}")
        
        # 3. CHIPS Act Status (if applicable)
        if project.get("chips_award"):
            try:
                chips_results = self.chips_scraper.check_status(project_id)
                for result in chips_results:
                    finding = self._create_finding(
                        project_id=project_id,
                        project_name=project_name,
                        category="regulatory",
                        source_type="primary",
                        source_name="Commerce Dept CHIPS Portal",
                        source_url=result["url"],
                        publication_date=result["update_date"],
                        extracted_text=result["status_text"]
                    )
                    findings.append(finding)
            except Exception as e:
                self.run_log["errors"].append(f"CHIPS check failed for {project_name}: {str(e)}")
        
        # 4. Grid Queue Status (if applicable)
        if project.get("grid_operator") and project.get("interconnection_id"):
            try:
                queue_results = self.grid_scraper.check_position(
                    operator=project["grid_operator"],
                    interconnection_id=project["interconnection_id"]
                )
                for result in queue_results:
                    finding = self._create_finding(
                        project_id=project_id,
                        project_name=project_name,
                        category="infrastructure",
                        source_type="primary",
                        source_name=f"{project['grid_operator']} Queue Data",
                        source_url=result["url"],
                        publication_date=result["data_date"],
                        extracted_text=result["status_text"]
                    )
                    findings.append(finding)
            except Exception as e:
                self.run_log["errors"].append(f"Grid check failed for {project_name}: {str(e)}")
        
        return findings[:CONFIG["max_findings_per_project"]]
    
    def _create_finding(self, project_id: str, project_name: str, category: str,
                        source_type: str, source_name: str, source_url: str,
                        publication_date: str, extracted_text: str) -> Dict:
        """Create a standardized finding object."""
        finding_id = f"F-{self.run_id}-{project_id}-{len(self.run_log.get('findings_discovered', 0)):03d}"
        content_hash = self._generate_content_hash(extracted_text)
        
        return {
            "finding_id": finding_id,
            "project_id": project_id,
            "project_name": project_name,
            "timestamp": datetime.utcnow().isoformat(),
            "category": category,
            "raw_data": {
                "source_url": source_url,
                "source_type": source_type,
                "source_name": source_name,
                "publication_date": publication_date,
                "content_hash": content_hash,
                "extracted_text": extracted_text
            },
            "status": "pending_validation"
        }
    
    def _categorize_news(self, title: str, content: str) -> str:
        """Categorize news article by topic."""
        text = (title + " " + content).lower()
        
        if any(word in text for word in ["delay", "postpone", "push back", "timeline", "schedule"]):
            return "timeline"
        elif any(word in text for word in ["funding", "investment", "capital", "financing", "billion", "million"]):
            return "financial"
        elif any(word in text for word in ["construction", "building", "groundbreaking", "completion", "phase"]):
            return "construction"
        elif any(word in text for word in ["workforce", "hiring", "jobs", "employment", "union", "labor"]):
            return "workforce"
        elif any(word in text for word in ["chips act", "subsidy", "award", "grant", "incentive"]):
            return "regulatory"
        elif any(word in text for word in ["grid", "power", "electricity", "interconnection", "utility"]):
            return "infrastructure"
        else:
            return "general"
    
    def run(self):
        """Execute the full research cycle."""
        print(f"\n{'='*60}")
        print(f"NXT Research Agent - Run {self.run_id}")
        print(f"{'='*60}\n")
        
        all_findings = []
        projects_list = self.projects.get("projects", [])
        
        print(f"Processing {len(projects_list)} projects...")
        print("-" * 40)
        
        # Phase 1: Research
        for i, project in enumerate(projects_list, 1):
            print(f"\n[{i}/{len(projects_list)}] {project['name']}")
            
            findings = self.research_project(project)
            
            # Filter duplicates
            new_findings = [f for f in findings if not self._is_duplicate(f)]
            
            print(f"    Found {len(findings)} items, {len(new_findings)} are new")
            
            all_findings.extend(new_findings)
            self.run_log["projects_researched"] += 1
        
        self.run_log["findings_discovered"] = len(all_findings)
        print(f"\n{'='*40}")
        print(f"Research complete: {len(all_findings)} new findings")
        print(f"{'='*40}\n")
        
        # Phase 2: Validation
        print("Validating findings...")
        validated_findings = []
        
        for finding in all_findings:
            credibility = self.validator.verify_credibility(finding)
            finding["credibility"] = credibility
            
            if credibility["score"] >= CONFIG["credibility_threshold"]:
                finding["status"] = "validated"
                validated_findings.append(finding)
                self.run_log["findings_validated"] += 1
            else:
                finding["status"] = "rejected"
                reason = "insufficient_credibility"
                self.run_log["findings_rejected"] += 1
                self.run_log["rejection_reasons"][reason] = \
                    self.run_log["rejection_reasons"].get(reason, 0) + 1
                
                # Log rejection
                self.research_log["rejected_findings"].append({
                    "finding_id": finding["finding_id"],
                    "reason": reason,
                    "credibility_score": credibility["score"]
                })
        
        print(f"Validated: {len(validated_findings)} findings")
        
        # Phase 3: Analysis
        print("\nAnalyzing findings...")
        analyzed_findings = []
        
        for finding in validated_findings:
            # Get current project data
            project_data = self.velocity_scores["scores"].get(finding["project_id"], {})
            
            # Run doctoral-level analysis
            analysis = self.analyzer.analyze_finding(finding, project_data)
            finding["analysis"] = analysis
            analyzed_findings.append(finding)
        
        print(f"Analyzed: {len(analyzed_findings)} findings")
        
        # Phase 4: Update
        print("\nApplying updates...")
        
        for finding in analyzed_findings:
            if finding["analysis"].get("recommended_updates"):
                success = self.updater.apply_updates(
                    finding=finding,
                    velocity_scores=self.velocity_scores,
                    research_log=self.research_log
                )
                
                if success:
                    self.run_log["findings_applied"] += 1
                    
                    # Track velocity changes
                    if finding["analysis"]["velocity_impact"]["net_change"] != 0:
                        self.run_log["velocity_changes"].append({
                            "project_id": finding["project_id"],
                            "change": finding["analysis"]["velocity_impact"]["net_change"]
                        })
                    
                    # Track project updates
                    if finding["project_id"] not in self.run_log["projects_updated"]:
                        self.run_log["projects_updated"].append(finding["project_id"])
                    
                    # Add to research log
                    self.research_log["findings"].append(finding)
                    self.research_log["seen_hashes"].append(
                        finding["raw_data"]["content_hash"]
                    )
        
        # Phase 5: Save results
        print("\nSaving results...")
        
        # Update research log
        self.research_log["last_updated"] = datetime.utcnow().isoformat()
        self.research_log["total_findings_processed"] += len(all_findings)
        self.research_log["run_history"].append(self.run_log)
        
        # Save all data files
        self._save_json("research_log.json", self.research_log)
        self._save_json("velocity_scores.json", self.velocity_scores)
        
        # Recalculate portfolio metrics
        self.updater.recalculate_portfolio_metrics(
            self.projects,
            self.velocity_scores
        )
        
        # Finalize run log
        self.run_log["end_time"] = datetime.utcnow().isoformat()
        self.run_log["status"] = "complete"
        
        # Save run log
        CONFIG["logs_dir"].mkdir(parents=True, exist_ok=True)
        log_path = CONFIG["logs_dir"] / f"run_{self.run_id}.json"
        with open(log_path, "w") as f:
            json.dump(self.run_log, f, indent=2)
        
        # Print summary
        self._print_summary()
        
        return self.run_log
    
    def _print_summary(self):
        """Print run summary."""
        print(f"\n{'='*60}")
        print("RUN SUMMARY")
        print(f"{'='*60}")
        print(f"Run ID: {self.run_id}")
        print(f"Projects researched: {self.run_log['projects_researched']}")
        print(f"Findings discovered: {self.run_log['findings_discovered']}")
        print(f"Findings validated: {self.run_log['findings_validated']}")
        print(f"Findings applied: {self.run_log['findings_applied']}")
        print(f"Findings rejected: {self.run_log['findings_rejected']}")
        print(f"Projects updated: {len(self.run_log['projects_updated'])}")
        print(f"Velocity changes: {len(self.run_log['velocity_changes'])}")
        print(f"Errors: {len(self.run_log['errors'])}")
        
        if self.run_log["errors"]:
            print("\nErrors:")
            for error in self.run_log["errors"]:
                print(f"  - {error}")
        
        print(f"\n{'='*60}\n")


def main():
    """Main entry point."""
    agent = NXTResearchAgent()
    agent.run()


if __name__ == "__main__":
    main()
