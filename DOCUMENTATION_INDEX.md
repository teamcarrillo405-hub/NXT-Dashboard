# How to Make Changes - Documentation Index

Welcome! This repository now has comprehensive documentation to help you make changes.

## 📚 Documentation Files

### 1. **README.md** - Start Here
The main project overview that explains:
- What this dashboard is
- Quick start guide
- Project structure
- Key features

**Use this**: To understand the project at a high level

---

### 2. **CONTRIBUTING.md** - Complete Guide
Comprehensive guide covering:
- Repository structure
- How to edit HTML/CSS dashboard files
- How to update project data
- How to work with Python automation
- Git workflow
- Testing procedures
- Detailed file organization

**Use this**: When you need detailed instructions for any type of change

---

### 3. **QUICK_REFERENCE.md** - Quick Lookups
Fast reference for common tasks:
- Common file locations
- Quick code snippets
- Git commands
- CSS class names
- Testing commands
- grep commands

**Use this**: When you know what you want to do and need quick syntax

---

### 4. **EXAMPLE_NEW_PROJECT.md** - Step-by-Step Tutorial
Complete walkthrough for adding a new project:
- Step-by-step instructions
- Code examples
- Testing checklist
- Troubleshooting tips

**Use this**: When adding a new infrastructure project to track

---

## 🚀 Quick Start Paths

### "I want to change the dashboard appearance"
1. Read [CONTRIBUTING.md](CONTRIBUTING.md) section 1
2. Edit `index.html` 
3. Look at [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for CSS class names
4. Test in browser

### "I want to update project status"
1. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for project updates
2. Edit the project's `XX###_ProjectName_RAID.html` file
3. Update data files if needed
4. Commit changes

### "I want to add a new project"
1. Follow [EXAMPLE_NEW_PROJECT.md](EXAMPLE_NEW_PROJECT.md) step-by-step
2. Use existing project files as templates
3. Test thoroughly before committing

### "I want to update data/metrics"
1. See [CONTRIBUTING.md](CONTRIBUTING.md) section 3
2. Edit JSON files in `data/` directory
3. Validate JSON syntax
4. Commit changes

### "I'm new and just exploring"
1. Start with [README.md](README.md)
2. Open `index.html` in a browser to see the dashboard
3. Browse through [CONTRIBUTING.md](CONTRIBUTING.md)
4. Try a small change from [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 📁 Repository Structure

```
NXT-Dashboard/
│
├── 📖 Documentation (you are here)
│   ├── README.md                    # Project overview
│   ├── CONTRIBUTING.md              # Complete contribution guide
│   ├── QUICK_REFERENCE.md          # Quick command reference
│   ├── EXAMPLE_NEW_PROJECT.md      # Tutorial for adding projects
│   └── DOCUMENTATION_INDEX.md      # This file
│
├── 🌐 Dashboard Files
│   ├── index.html                   # Main dashboard
│   ├── XX###_*_RAID.html           # Individual project pages
│   ├── METHODOLOGY.html            # Methodology docs
│   ├── POLICY_MONITOR.html         # Policy tracking
│   ├── SUPPLY_CHAIN.html           # Supply chain analysis
│   └── WORKFORCE.html              # Workforce analysis
│
├── 📊 Data Files
│   └── data/
│       ├── projects.json           # Project details
│       ├── portfolio_metrics.json  # Portfolio metrics
│       ├── velocity_scores.json    # Velocity calculations
│       └── research_log.json       # Research findings
│
├── 🤖 Automation Scripts
│   └── agent/
│       ├── research_agent.py       # Main automation
│       ├── analysis_layer.py       # Analysis logic
│       ├── validation_layer.py     # Data validation
│       └── scrapers/               # Data collection
│
└── 🎨 Assets
    ├── New_HCC_Logo.svg
    └── Velocity_Transparent_Logo.svg
```

---

## 💡 Common Questions

### Q: What type of project is this?
A: A static HTML/CSS/JavaScript dashboard with optional Python automation for data collection. No build process needed - just open HTML files in a browser.

### Q: Do I need to know programming?
A: Basic HTML/CSS knowledge helps for dashboard changes. Python knowledge needed only for automation scripts. Most changes can be made by editing HTML files and following examples.

### Q: How do I test my changes?
A: Simply open the HTML file in your web browser. See [CONTRIBUTING.md](CONTRIBUTING.md) section 8 for details.

### Q: Can I break something?
A: Git version control protects you. Use `git status` and `git diff` to see changes before committing. You can always undo uncommitted changes.

### Q: Where do I start?
A: 
1. Open `index.html` in a browser to see the dashboard
2. Read [README.md](README.md) for overview
3. Try a small change from [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
4. Reference [CONTRIBUTING.md](CONTRIBUTING.md) for detailed help

---

## 🛠️ Tool Requirements

### For Dashboard Changes
- ✅ Any web browser (Chrome, Firefox, Safari, etc.)
- ✅ Text editor (VS Code, Sublime, Notepad++, etc.)
- ✅ Git (for version control)

### For Python Automation (Optional)
- Python 3.x
- Anthropic API key (for research agent)
- Basic Python package management

---

## 📞 Need Help?

1. **Check the docs first**: Your question is likely answered in one of the guides above
2. **Look at examples**: Browse existing HTML files to see patterns
3. **Check git history**: `git log --oneline` shows recent changes
4. **Review commit diffs**: `git show <commit>` shows what changed

---

## 🎯 Best Practices

1. ✅ **Always test in browser** before committing
2. ✅ **Make small, focused commits** with clear messages  
3. ✅ **Follow existing patterns** in the code
4. ✅ **Validate JSON files** before committing
5. ✅ **Back up before major changes** (or use git branches)

---

## 📝 Quick Command Reference

```bash
# View the dashboard
open index.html

# Check what you changed
git status
git diff

# Commit your changes
git add .
git commit -m "Description of changes"
git push

# Undo uncommitted changes
git checkout -- filename.html
```

---

**Ready to make changes?** Pick a starting point above and dive in! The documentation has your back. 🚀
