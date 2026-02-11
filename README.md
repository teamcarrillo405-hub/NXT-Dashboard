# NXT Infrastructure Velocity Report

An executive intelligence dashboard tracking $2.5T+ in U.S. infrastructure megaprojects across semiconductors, data centers, automotive, batteries, and more.

## Overview

This dashboard provides real-time tracking and analysis of major infrastructure projects including:
- **Semiconductors (SE)**: TSMC, Intel, Samsung, Micron, and more
- **Data Centers (DC)**: Meta, Google, Oracle, Amazon, Microsoft, Apple
- **Automotive (AU)**: Ford, GM, Rivian, Hyundai, Toyota
- **Battery Manufacturing (BT)**: Panasonic, SK, LG Energy, Honda
- **Hydrogen (HY)**: Plug Power, Air Products
- **Pharmaceuticals (PH)**: Eli Lilly, Novo Nordisk, Amgen
- **Steel (ST)**: Nucor, Steel Dynamics
- **Solar (SO)**: Qcells, First Solar
- **Energy Storage (ES)**: Form Energy

## Quick Start

### View the Dashboard
Simply open `index.html` in your web browser:
```bash
open index.html
```

### Project Structure
```
├── index.html              # Main dashboard
├── *_RAID.html            # Individual project RAID analyses
├── METHODOLOGY.html       # Research methodology
├── POLICY_MONITOR.html    # Policy tracking
├── agent/                 # Python automation scripts
└── data/                  # JSON data files
```

## Making Changes

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions on how to make changes to the dashboard.

Quick tips:
- **Edit dashboard**: Modify `index.html`
- **Update project data**: Edit JSON files in `data/`
- **Customize styling**: Update CSS variables in `index.html`
- **Add projects**: Create new `*_RAID.html` files

## Features

- Real-time project status tracking
- RAID (Risks, Actions, Issues, Decisions) analysis per project
- Portfolio-level metrics and velocity scoring
- Competitive landscape analysis
- Infrastructure constraints monitoring
- Workforce and supply chain tracking
- Policy impact monitoring

## Technologies

- Pure HTML/CSS/JavaScript (no build process required)
- Python automation scripts for data collection and analysis
- Static files for easy deployment

## License

All rights reserved.