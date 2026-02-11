# Quick Reference Guide - Common Changes

Quick reference for making common changes to the NXT Dashboard.

## Viewing the Dashboard

```bash
# Open main dashboard
open index.html

# Open specific project
open SE001_TSMC_Arizona_RAID.html
```

## Editing Dashboard Content

### Change Dashboard Title
**File**: `index.html`  
**Line**: ~15  
```html
<title>Your New Title | Executive Intelligence Platform</title>
```

### Update Color Scheme
**File**: `index.html`  
**Lines**: 18-36  
```css
:root {
    --deep-indigo: #1e1b4b;      /* Main background */
    --electric-yellow: #FDFF66;   /* Accent color */
    --green: #22c55e;             /* Success/positive */
    --red: #ef4444;               /* Alerts/negative */
}
```

### Update Data Freshness Timestamp
**File**: `index.html`  
**Search for**: `class="freshness-timestamp"`  
```html
<span class="freshness-timestamp">Updated Feb 11, 2024, 4:00 PM ET</span>
```

### Change Header Logo
**File**: `index.html`  
**Search for**: `brand-logo`  
```html
<img src="Your_Logo.svg" alt="Logo" class="brand-logo">
```

Replace `New_HCC_Logo.svg` with your own SVG file.

## Project Updates

### Update Project Status
**File**: `XX###_ProjectName_RAID.html`  
**Search for**: `status-badge`  
```html
<div class="status-badge status-construction">Construction</div>
<!-- Options: status-planning, status-construction, status-operational, status-delayed -->
```

### Add a Risk Item
**File**: `XX###_ProjectName_RAID.html`  
**In the Risks section**:
```html
<div class="risk-item risk-high">
    <div class="risk-label">RISK CATEGORY</div>
    <div class="risk-description">
        Description of the risk.
    </div>
    <div class="risk-mitigation">
        Mitigation: How you're addressing it.
    </div>
</div>
```

Risk levels: `risk-low`, `risk-medium`, `risk-high`, `risk-critical`

### Add an Action Item
**File**: `XX###_ProjectName_RAID.html`  
**In the Actions section**:
```html
<div class="action-item action-pending">
    <div class="action-header">
        <span class="action-label">ACTION REQUIRED</span>
        <span class="action-owner">Owner: John Doe</span>
    </div>
    <div class="action-description">
        Description of the action needed.
    </div>
    <div class="action-deadline">Deadline: Feb 28, 2024</div>
</div>
```

Action status: `action-pending`, `action-in-progress`, `action-completed`

### Add an Issue
**File**: `XX###_ProjectName_RAID.html`  
**In the Issues section**:
```html
<div class="issue-item issue-open">
    <div class="issue-header">
        <span class="issue-id">#042</span>
        <span class="issue-severity">HIGH</span>
    </div>
    <div class="issue-title">Issue Title</div>
    <div class="issue-description">
        Detailed description of the issue.
    </div>
    <div class="issue-status">Status: Under Investigation</div>
</div>
```

### Add a Decision
**File**: `XX###_ProjectName_RAID.html`  
**In the Decisions section**:
```html
<div class="decision-item">
    <div class="decision-date">Feb 11, 2024</div>
    <div class="decision-title">Decision Title</div>
    <div class="decision-description">
        What was decided and why.
    </div>
    <div class="decision-impact">
        Impact: Description of the impact.
    </div>
</div>
```

## Data File Updates

### Update Project Investment Amount
**File**: `data/projects.json`  
```json
{
  "id": "SE001",
  "investment_usd": 40000000000,  // $40B
  ...
}
```

### Update Velocity Score
**File**: `data/velocity_scores.json`  
```json
{
  "SE001": {
    "velocity_score": 85,
    "risk_adjusted_score": 78,
    "trend": "improving"
  }
}
```

### Add Research Finding
**File**: `data/research_log.json`  
```json
{
  "date": "2024-02-11",
  "project_id": "SE001",
  "finding": "Construction milestone achieved ahead of schedule",
  "source": "Company press release",
  "credibility_score": 95,
  "impact": "positive"
}
```

## Git Commands

### Check Status
```bash
git status              # See modified files
git diff                # See detailed changes
git log --oneline -5    # See recent commits
```

### Make Changes
```bash
git add index.html                    # Stage specific file
git add .                             # Stage all changes
git commit -m "Update project status" # Commit with message
git push                              # Push to GitHub
```

### Undo Changes
```bash
git checkout -- index.html   # Undo changes to one file
git reset --hard            # Undo all uncommitted changes (CAREFUL!)
```

## Python Automation

### Run Research Agent
```bash
# Set API key
export ANTHROPIC_API_KEY="your-key"

# Run the agent
cd /home/runner/work/NXT-Dashboard/NXT-Dashboard
python agent/research_agent.py
```

### Check Agent Logs
```bash
# View recent logs
ls -lt agent/logs/
tail -f agent/logs/latest.log
```

## Testing Changes

### Browser Testing
```bash
# Open in default browser
open index.html

# Or specific browser
chrome index.html
firefox index.html
```

### Check for Broken Links
```bash
# Find all HTML files
find . -name "*.html" -type f

# Grep for links
grep -r "href=" index.html | head -20
```

### Validate JSON
```bash
# Check JSON syntax
python -m json.tool data/projects.json
python -m json.tool data/velocity_scores.json
```

## Common File Locations

```
Main Dashboard:        index.html
Project RAID Pages:    XX###_ProjectName_RAID.html
Project Data:          data/projects.json
Velocity Scores:       data/velocity_scores.json
Portfolio Metrics:     data/portfolio_metrics.json
Research Log:          data/research_log.json
Main Logo:            New_HCC_Logo.svg
Automation Scripts:    agent/research_agent.py
```

## Status Class Names

### Project Status
- `status-planning` - Planning phase
- `status-construction` - Under construction
- `status-operational` - Operational
- `status-delayed` - Delayed
- `status-cancelled` - Cancelled

### Risk Levels
- `risk-low` - Low risk (green)
- `risk-medium` - Medium risk (yellow)
- `risk-high` - High risk (orange)
- `risk-critical` - Critical risk (red)

### Velocity Indicators
- `velocity-excellent` - 90-100 (dark green)
- `velocity-good` - 75-89 (green)
- `velocity-fair` - 60-74 (yellow)
- `velocity-poor` - 40-59 (orange)
- `velocity-critical` - 0-39 (red)

## Useful Grep Commands

```bash
# Find all projects with status "Construction"
grep -r "status-construction" *.html

# Find all high-risk items
grep -r "risk-high" *.html

# Find specific project code
grep -r "SE001" .

# Find all investment amounts
grep -r "investment_usd" data/
```

## Tips

1. **Always test in browser** before committing
2. **Keep backups** of files you're changing
3. **Make small commits** with clear messages
4. **Follow existing patterns** in the code
5. **Validate JSON** before committing data files
6. **Check mobile view** after CSS changes

## Need Help?

- See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guides
- See [EXAMPLE_NEW_PROJECT.md](EXAMPLE_NEW_PROJECT.md) for adding projects
- Check existing files for examples
- Review git history: `git log --oneline`
