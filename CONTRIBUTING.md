# Contributing to NXT-Dashboard

This guide explains how to make changes to the NXT Infrastructure Velocity Report dashboard.

## Repository Overview

This repository contains:
- **HTML Dashboard Files**: Main dashboard (`index.html`) and individual project RAID pages
- **Python Automation Scripts**: Located in the `agent/` directory for automated research and updates
- **Data Files**: JSON files in the `data/` directory containing project metrics and research logs
- **Assets**: SVG logos and other visual assets

## Making Changes

### 1. Dashboard UI Changes (HTML/CSS)

The main dashboard is in `index.html`. To make changes:

#### Edit Visual Styling
```bash
# Open index.html and locate the <style> section (lines 17+)
# Modify CSS variables in the :root section to change colors:
```

**Example color changes:**
```css
:root {
    --deep-indigo: #1e1b4b;        /* Header background */
    --electric-yellow: #FDFF66;     /* Accent color */
    --white: #ffffff;
    --green: #22c55e;               /* Success indicators */
    --red: #ef4444;                 /* Alert indicators */
}
```

#### Edit Content
```bash
# Dashboard sections are organized with clear HTML comments
# Look for sections like:
# - <!-- Header -->
# - <!-- Main Navigation -->
# - <!-- KPI Dashboard -->
# - etc.
```

#### Test Changes Locally
```bash
# Simply open index.html in a web browser
open index.html           # macOS
xdg-open index.html       # Linux
start index.html          # Windows
```

### 2. Project RAID Pages

Individual project pages follow the naming pattern:
- `AU###_ProjectName_RAID.html` - Automotive projects
- `BT###_ProjectName_RAID.html` - Battery projects
- `DC###_ProjectName_RAID.html` - Data Center projects
- `SE###_ProjectName_RAID.html` - Semiconductor projects
- etc.

To modify a project page:
```bash
# Edit the corresponding HTML file
# Each follows the same structure as index.html
```

### 3. Data Updates

Project data is stored in JSON files in the `data/` directory:

#### `data/projects.json`
Contains project details, timelines, and metrics.

#### `data/portfolio_metrics.json`
Contains aggregated portfolio-level metrics.

#### `data/velocity_scores.json`
Contains project velocity calculations.

**To update data:**
```bash
# Edit the JSON file directly
# Ensure valid JSON syntax
# The Python automation scripts will read these files
```

### 4. Python Automation Scripts

Located in `agent/` directory:

#### Main Files:
- `research_agent.py` - Main research automation entry point
- `analysis_layer.py` - Data analysis logic
- `validation_layer.py` - Data validation
- `update_layer.py` - Dashboard update automation
- `scrapers/` - Web scrapers for data collection

#### Setting Up Python Environment:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (if requirements.txt exists)
pip install anthropic
# Other dependencies as needed
```

#### Running the Research Agent:
```bash
# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Run the agent
python agent/research_agent.py
```

### 5. Common Change Scenarios

#### Change the Header Logo
```bash
# Replace New_HCC_Logo.svg with your own SVG file
# Update the reference in index.html if changing the filename
```

#### Add a New Project
1. Create a new `XX###_ProjectName_RAID.html` file using an existing one as template
2. Update `data/projects.json` with the new project details
3. Add navigation link in `index.html` if needed

#### Update Project Status
1. Open the project's RAID HTML file
2. Locate the status indicators section
3. Update the status badges and risk indicators

#### Modify Color Scheme
1. Edit the CSS variables in `index.html` (lines 18-36)
2. Update any hardcoded colors in specific sections
3. Test in a browser to ensure readability

### 6. Git Workflow

#### Basic workflow:
```bash
# Check current status
git status

# See what changes you've made
git diff

# Stage your changes
git add <filename>
# or add all changes
git add .

# Commit your changes
git commit -m "Brief description of changes"

# Push to GitHub
git push
```

#### Best Practices:
- Make small, focused commits
- Write clear commit messages
- Test changes before committing
- Don't commit sensitive data or API keys

### 7. File Organization

```
NXT-Dashboard/
├── index.html                 # Main dashboard
├── *_RAID.html               # Individual project pages
├── COMPETITIVE.html          # Competitive analysis
├── METHODOLOGY.html          # Methodology documentation
├── POLICY_MONITOR.html       # Policy tracking
├── SUPPLY_CHAIN.html         # Supply chain analysis
├── WORKFORCE.html            # Workforce analysis
├── agent/                    # Python automation scripts
│   ├── research_agent.py
│   ├── analysis_layer.py
│   ├── validation_layer.py
│   ├── update_layer.py
│   └── scrapers/
├── data/                     # JSON data files
│   ├── projects.json
│   ├── portfolio_metrics.json
│   ├── velocity_scores.json
│   └── research_log.json
└── *.svg                     # Logo and icon files
```

### 8. Testing Your Changes

#### For HTML/CSS Changes:
1. Open the file in multiple browsers (Chrome, Firefox, Safari)
2. Test responsive design by resizing the browser window
3. Check that all links and navigation work
4. Verify that data displays correctly

#### For Python Script Changes:
1. Run the script in a test environment first
2. Check the console output for errors
3. Verify that data files are updated correctly
4. Review generated HTML for accuracy

### 9. Need Help?

- Check existing HTML files for examples
- Review the Python scripts for data structure patterns
- Look at recent git commits to see how others made similar changes
- The dashboard is self-contained HTML/CSS/JavaScript, making it easy to experiment

## Quick Reference

### View recent changes
```bash
git log --oneline -10
```

### See what you've modified
```bash
git status
git diff
```

### Undo uncommitted changes to a file
```bash
git checkout -- <filename>
```

### View file history
```bash
git log --follow <filename>
```

## Tips

1. **Always backup before major changes** - Create a copy or use git branches
2. **Test locally first** - Open HTML files in a browser before committing
3. **Keep data files valid** - Use a JSON validator for data files
4. **Document your changes** - Add comments in code for complex modifications
5. **Follow existing patterns** - Look at how similar features are implemented

---

**Note**: This is a static HTML dashboard with optional Python automation. Most changes can be made by editing HTML files directly and viewing in a browser.
