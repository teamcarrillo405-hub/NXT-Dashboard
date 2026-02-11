# Example: Adding a New Project to the Dashboard

This guide walks through adding a new infrastructure project to the NXT Dashboard.

## Step 1: Choose a Project Code

Project codes follow this format: `XX###_ProjectName_RAID.html`

Where:
- `XX` = Category code (AU=Automotive, BT=Battery, DC=Data Center, SE=Semiconductor, etc.)
- `###` = Sequential number within category
- `ProjectName` = Short project identifier

**Example**: `BT015_Tesla_Nevada_RAID.html` for a new Tesla battery facility

## Step 2: Create the Project RAID File

Copy an existing project file as a template:

```bash
# Copy a similar project file
cp BT001_Panasonic_Kansas_RAID.html BT015_Tesla_Nevada_RAID.html
```

Then edit the new file to customize:

1. **Title** (around line 10):
   ```html
   <title>BT015: Tesla Nevada Gigafactory Expansion | RAID Analysis</title>
   ```

2. **Project Header** (search for the project name section):
   ```html
   <h1>Tesla Nevada Gigafactory Expansion</h1>
   <div class="project-code">BT015</div>
   ```

3. **Key Details** (find the project details section):
   ```html
   <div class="detail-item">
       <div class="detail-label">Location</div>
       <div class="detail-value">Sparks, Nevada</div>
   </div>
   <div class="detail-item">
       <div class="detail-label">Investment</div>
       <div class="detail-value">$3.6B</div>
   </div>
   <div class="detail-item">
       <div class="detail-label">Capacity</div>
       <div class="detail-value">100 GWh/year</div>
   </div>
   ```

4. **RAID Content** (update all four sections):
   - Risks
   - Actions  
   - Issues
   - Decisions

## Step 3: Add to Project Data

Edit `data/projects.json` and add your new project:

```json
{
  "id": "BT015",
  "name": "Tesla Nevada Gigafactory Expansion",
  "category": "Battery Manufacturing",
  "location": "Sparks, Nevada",
  "investment_usd": 3600000000,
  "status": "Construction",
  "start_date": "2024-01-15",
  "target_completion": "2026-12-31",
  "velocity_score": 75,
  "risk_level": "Medium",
  "jobs_created": 3000,
  "capacity": "100 GWh/year",
  "key_milestones": [
    {
      "date": "2024-01-15",
      "event": "Construction begins",
      "status": "Completed"
    },
    {
      "date": "2025-06-01", 
      "event": "Equipment installation",
      "status": "On Track"
    }
  ]
}
```

## Step 4: Add Navigation Link

In `index.html`, find the appropriate project category section and add a link:

```html
<!-- In the Battery Manufacturing section -->
<div class="project-card">
    <a href="BT015_Tesla_Nevada_RAID.html" class="project-link">
        <div class="project-header">
            <h3>Tesla Nevada Expansion</h3>
            <span class="project-code">BT015</span>
        </div>
        <div class="project-meta">
            <span class="location">Nevada</span>
            <span class="investment">$3.6B</span>
        </div>
        <div class="status-badge status-construction">Construction</div>
    </a>
</div>
```

## Step 5: Test Your Changes

1. **Open in browser**:
   ```bash
   open index.html
   ```

2. **Check that**:
   - New project appears in the correct category
   - Link to RAID page works
   - RAID page displays correctly
   - All data is accurate

3. **Test responsiveness**:
   - Resize browser window
   - Check on mobile view
   - Verify all sections are readable

## Step 6: Commit Your Changes

```bash
# Check what you've changed
git status

# Add your new files
git add BT015_Tesla_Nevada_RAID.html
git add data/projects.json
git add index.html

# Commit with descriptive message
git commit -m "Add BT015: Tesla Nevada Gigafactory Expansion project"

# Push to GitHub
git push
```

## Common Customizations

### Add a Risk Alert
```html
<div class="risk-item risk-high">
    <div class="risk-label">SUPPLY CHAIN</div>
    <div class="risk-description">
        Lithium supply constraints may delay equipment installation by 3-6 months.
    </div>
    <div class="risk-mitigation">
        Mitigation: Secured alternative suppliers in Australia and Chile.
    </div>
</div>
```

### Add a Recent Update
```html
<div class="update-item">
    <div class="update-date">Feb 11, 2024</div>
    <div class="update-content">
        <strong>Groundbreaking completed.</strong> Site preparation 85% complete.
        Equipment delivery scheduled for Q2 2024.
    </div>
</div>
```

### Add Key Stakeholders
```html
<div class="stakeholder-item">
    <div class="stakeholder-name">Tesla Inc.</div>
    <div class="stakeholder-role">Owner/Operator</div>
</div>
<div class="stakeholder-item">
    <div class="stakeholder-name">State of Nevada</div>
    <div class="stakeholder-role">$330M tax incentives</div>
</div>
```

## Tips

1. **Copy similar projects** - Use existing files as templates
2. **Maintain consistency** - Follow the same structure and styling
3. **Validate data** - Double-check all numbers and dates
4. **Test thoroughly** - View in browser before committing
5. **Update incrementally** - Make small changes and test frequently

## Troubleshooting

### Link doesn't work
- Check filename matches exactly (case-sensitive)
- Verify file is in the root directory
- Check that the href in index.html is correct

### Styling looks broken
- Make sure you copied all the CSS from the template
- Check for missing closing tags
- Validate HTML syntax

### JSON syntax error
- Use a JSON validator (jsonlint.com)
- Check for missing commas or quotes
- Ensure proper bracket matching

---

**Next Steps**: After adding your project, you may want to:
1. Add it to the `COMPETITIVE.html` analysis if relevant
2. Update `SUPPLY_CHAIN.html` if it has supply chain implications
3. Add workforce data to `WORKFORCE.html`
4. Update portfolio metrics in `data/portfolio_metrics.json`
