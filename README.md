# NXT-Dashboard

NXT Infrastructure Velocity Report - An automated research and analysis dashboard for tracking major US infrastructure projects.

## Overview

This dashboard tracks velocity and health metrics for major infrastructure projects across sectors including:
- Automotive & EV Manufacturing
- Battery Production
- Data Centers & AI Infrastructure
- Semiconductors
- Solar Energy
- Steel Production
- Hydrogen & Energy Storage
- Pharmaceuticals

## Setup

### Prerequisites

- Python 3.8 or higher
- An Anthropic API key (for the research agent)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/teamcarrillo405-hub/NXT-Dashboard.git
   cd NXT-Dashboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

#### Adding Your Anthropic API Key

The research agent requires an Anthropic API key to function. You can set this up in two ways:

**Option 1: Local Environment Variable**

For local development, set the environment variable:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Option 2: GitHub Secrets (for GitHub Actions)**

To add your Anthropic API key as a GitHub Secret:

1. Go to your repository on GitHub
2. Click on **Settings** (in the repository menu)
3. In the left sidebar, click on **Secrets and variables** → **Actions**
4. Click the **New repository secret** button
5. Enter the following:
   - **Name**: `ANTHROPIC_API_KEY`
   - **Secret**: Your Anthropic API key (paste your actual key)
6. Click **Add secret**

Once added, GitHub Actions workflows can access this secret using:

```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

**Getting an Anthropic API Key:**

If you don't have an API key yet:
1. Visit [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Go to **API Keys** in the settings
4. Click **Create Key**
5. Copy the key (you won't be able to see it again)

## Usage

### Running the Research Agent

```bash
python agent/research_agent.py
```

The agent will:
1. Gather new information about tracked infrastructure projects
2. Validate findings for credibility and deduplication
3. Analyze impacts at doctoral-level rigor
4. Update dashboard files automatically

### Viewing the Dashboard

Open `index.html` in a web browser to view the dashboard.

## Project Structure

```
NXT-Dashboard/
├── agent/                  # Research agent components
│   ├── research_agent.py  # Main agent orchestrator
│   ├── validation_layer.py
│   ├── analysis_layer.py
│   ├── update_layer.py
│   └── scrapers/          # Data collection modules
├── data/                  # Project data and metrics
│   ├── projects.json
│   ├── velocity_scores.json
│   └── research_log.json
└── *.html                 # Dashboard pages and project reports
```

## License

See LICENSE file for details.