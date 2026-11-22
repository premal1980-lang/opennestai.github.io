# TCS Intel Brief Agent

Generates a McKinsey-style intelligence brief on 5 UK retail accounts and posts it to Slack every 15 days.

## Files
| File | Purpose |
|------|---------|
| `agent.py` | Core agent — Claude + web search brief generation, Slack post |
| `requirements.txt` | Python dependencies |
| `.github/workflows/tcs-intel-brief.yml` | GitHub Actions schedule and runner |

## How It Runs
GitHub Actions workflow `TCS Intel Brief` runs on the 1st and 16th of each month at 06:00 UTC (07:00 BST). It can also be started manually from the Actions tab (`workflow_dispatch`). GitHub's scheduled runs can start a few minutes late.

## Setup
Add these in the repo's **Settings → Secrets and variables → Actions**:

| Name | Type | Value |
|------|------|-------|
| `ANTHROPIC_API_KEY` | Secret | Anthropic API key |
| `SLACK_BOT_TOKEN` | Secret | Slack bot token with `chat:write` scope |
| `SLACK_CHANNEL` | Variable | Slack channel ID for `#tcs-intelligence` (the bot must be invited) |
| `MODEL` | Variable (optional) | Anthropic model ID; defaults to `claude-haiku-4-5` |

## Local Run
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=... SLACK_BOT_TOKEN=... SLACK_CHANNEL=C0123456789
python agent.py
```

## Output
Posts to `#tcs-intelligence` on Slack — header message + threaded brief sections.

## Companies Covered
ASOS · John Lewis Partnership · Ocado Group · Ocado Retail · Waitrose
