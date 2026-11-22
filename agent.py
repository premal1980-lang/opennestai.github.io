"""TCS Intel Brief Agent.

Generates a McKinsey-style intelligence brief for each UK retail account using
Claude with Anthropic's server-side web search tool, then posts a header message
and one threaded reply per account to Slack.

Required environment variables:
    ANTHROPIC_API_KEY   Anthropic API key
    SLACK_BOT_TOKEN     Slack bot token (scope: chat:write)
    SLACK_CHANNEL       Slack channel ID to post into (e.g. C0123456789)

Optional:
    MODEL               Anthropic model ID (default: claude-haiku-4-5)
"""

import datetime as dt
import os
import sys

import anthropic
import requests

COMPANIES = [
    "ASOS",
    "John Lewis Partnership",
    "Ocado Group",
    "Ocado Retail",
    "Waitrose",
]

MODEL = os.environ.get("MODEL") or "claude-haiku-4-5"
LOOKBACK_DAYS = 15
SLACK_API = "https://slack.com/api"

SYSTEM_PROMPT = """You are a senior consultant preparing an intelligence brief for a \
Tata Consultancy Services (TCS) account team. Write in a McKinsey-style: lead with the \
answer, use short bulleted findings, quantify where possible, and separate fact from \
inference. Use web search to find developments from the last {days} days only. \
Cite sources as links. If nothing material happened, say so plainly."""

USER_PROMPT = """Prepare the brief for {company} covering {start} to {end}.

Use exactly these sections, as Slack-friendly markdown (*bold* headings, • bullets):
1. *Executive summary* — 2 sentences.
2. *Key developments* — up to 5 bullets: what happened, why it matters.
3. *Technology & transformation signals* — relevant IT, digital, supply chain or
   AI initiatives, vendor changes, or tenders.
4. *Implications for TCS* — where TCS can add value, and the likely buying window.
5. *Recommended next steps* — up to 3 concrete actions for the account team.
6. *Sources* — links used.

Keep the whole brief under 350 words."""


def generate_brief(client: anthropic.Anthropic, company: str, start: str, end: str) -> str:
    messages = [
        {
            "role": "user",
            "content": USER_PROMPT.format(company=company, start=start, end=end),
        }
    ]
    system = SYSTEM_PROMPT.format(days=LOOKBACK_DAYS)
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 6}]

    # Server-side web search can pause a long turn; resume it until it finishes.
    for _ in range(5):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=system,
            tools=tools,
            messages=messages,
        )
        if response.stop_reason != "pause_turn":
            break
        messages.append({"role": "assistant", "content": response.content})

    text = "".join(block.text for block in response.content if block.type == "text").strip()
    if not text:
        raise RuntimeError(f"Empty response for {company} (stop_reason={response.stop_reason})")
    return text


def slack_post(token: str, channel: str, text: str, thread_ts: str | None = None) -> str:
    payload = {"channel": channel, "text": text, "unfurl_links": False}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    resp = requests.post(
        f"{SLACK_API}/chat.postMessage",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=30,
    )
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack error: {data.get('error')}")
    return data["ts"]


def main() -> int:
    api_key = os.environ["ANTHROPIC_API_KEY"]
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    channel = os.environ["SLACK_CHANNEL"]

    today = dt.datetime.now(dt.timezone.utc).date()
    start = (today - dt.timedelta(days=LOOKBACK_DAYS)).isoformat()
    end = today.isoformat()

    client = anthropic.Anthropic(api_key=api_key)

    header = (
        f":bar_chart: *TCS Intel Brief — UK Retail Accounts*\n"
        f"Period: {start} to {end} · Accounts: {', '.join(COMPANIES)}"
    )
    header_ts = slack_post(slack_token, channel, header)

    failures = []
    for company in COMPANIES:
        try:
            brief = generate_brief(client, company, start, end)
            slack_post(slack_token, channel, f"*{company}*\n{brief}", thread_ts=header_ts)
            print(f"Posted brief for {company}")
        except Exception as exc:  # keep going so one account doesn't block the rest
            failures.append(company)
            print(f"FAILED {company}: {exc}", file=sys.stderr)
            slack_post(
                slack_token,
                channel,
                f"*{company}*\n:warning: Brief generation failed: {exc}",
                thread_ts=header_ts,
            )

    if failures:
        print(f"Failed accounts: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
