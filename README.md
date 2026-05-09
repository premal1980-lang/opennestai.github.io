# TCS Intel Brief Agent

Generates a McKinsey-style intelligence brief on 5 UK retail accounts and posts it to Slack every 15 days.

## Files
| File | Purpose |
|------|---------|
| `agent.py` | Core agent — web search + brief generation + Slack post |
| `scheduler.py` | Legacy APScheduler (replaced by cloud routine) |
| `run_brief.bat` | Windows Task Scheduler entry point |
| `.env` | API keys (Anthropic + Slack) |
| `requirements.txt` | Python dependencies |
| `cloud_agent_backup.md` | Cloud routine config backup |

## How It Runs
**Primary:** Anthropic Cloud (CCR) — routine ID `trig_01MJAruYhLnNSxQQbryxpJCV`
Runs every 15 days (1st & 16th) at 07:00 BST. Machine does not need to be on.

**Backup:** Windows Task Scheduler task "TCS Intel Agent" — same schedule, runs `run_brief.bat` locally.

## Manual Run
```bash
cd C:\Users\prema\OneDrive\Desktop\tcs_intel_agent
python agent.py
```

## Setup (if reinstalling)
```bash
pip install -r requirements.txt
# Copy .env.example to .env and fill in keys
```

## Output
Posts to `#tcs-intelligence` on Slack — header message + threaded brief sections.

## Companies Covered
ASOS · John Lewis Partnership · Ocado Group · Ocado Retail · Waitrose
