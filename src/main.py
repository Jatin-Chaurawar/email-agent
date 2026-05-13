# src/main.py  — entry point for the email agent
import asyncio
import logging
import signal
import sys
from pathlib import Path
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from rich.console import Console
from rich.panel import Panel
from rich.logging import RichHandler

from src.config import settings

# ── Logging setup (Rich gives colour output on Windows too) ──────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        RichHandler(rich_tracebacks=True, markup=True),
        logging.FileHandler(settings.log_path, encoding="utf-8"),
    ],
)
log = logging.getLogger("email-agent")
console = Console()

# ── Placeholder pipeline steps (we will fill each file in next steps) ────────
# Each import below will be replaced with the real module as we build them.

async def poll_inbox() -> list[dict]:
    """Step 1: Fetch unseen emails from Gmail. Returns list of raw email dicts."""
    log.info("📥  Polling inbox...")
    # TODO: replace with real Gmail ingestion in src/ingestion/gmail.py
    return []

async def classify_email(email: dict) -> dict:
    """Step 2: Rule engine → Claude classifier. Returns classification result."""
    log.info(f"🧠  Classifying: {email.get('subject', '(no subject)')}")
    # TODO: replace with src/classifier/engine.py
    return {"priority": "NORMAL", "category": "other", "confidence": 0.5}

def plan_actions(result: dict) -> list[dict]:
    """Step 3: Map classification to candidate actions."""
    actions = []
    priority = result.get("priority", "NORMAL")

    if priority == "HIGH":
        if settings.allow_auto_flag:
            actions.append({"type": "flag",  "auto": True})
        if settings.allow_auto_label:
            actions.append({"type": "label", "auto": True,  "label": "Job/Important"})
        # draft reply always needs approval
        actions.append({"type": "draft_reply", "auto": False})

    elif priority == "NORMAL":
        if settings.allow_auto_label:
            actions.append({"type": "label", "auto": True, "label": "Job/Normal"})

    else:  # LOW
        if settings.allow_auto_label:
            actions.append({"type": "label", "auto": True, "label": "Job/Low"})

    return actions

async def execute_with_guardrails(actions: list[dict], email: dict) -> None:
    """Step 4: Execute safe actions immediately; queue risky ones for approval."""
    auto_actions  = [a for a in actions if a.get("auto")]
    human_actions = [a for a in actions if not a.get("auto")]

    for action in auto_actions:
        log.info(f"  ✅  Auto-executing: {action['type']}")
        # TODO: wire up real executor in src/executor/actions.py

    if human_actions:
        log.info(f"  ⏳  {len(human_actions)} action(s) queued for your approval")
        # TODO: push to pending queue in src/storage/queue.py

async def run_pipeline() -> None:
    """Full pipeline: poll → classify → plan → execute."""
    try:
        emails = await poll_inbox()

        if not emails:
            log.info("📭  No new emails.")
            return

        log.info(f"📬  {len(emails)} new email(s) found.")

        for email in emails:
            result  = await classify_email(email)
            actions = plan_actions(result)
            await execute_with_guardrails(actions, email)

    except Exception as exc:
        log.error(f"Pipeline error: {exc}", exc_info=True)
        # Never crash the scheduler — log and continue

def print_banner() -> None:
    console.print(Panel.fit(
        "[bold]Email Agent[/bold] — Job-focused · Privacy-first\n"
        f"[dim]Poll interval : {settings.poll_interval_seconds}s[/dim]\n"
        f"[dim]Auto-send     : {'[red]DISABLED[/red]' if not settings.allow_auto_send else '[yellow]ENABLED[/yellow]'}[/dim]\n"
        f"[dim]Log file      : {settings.log_path}[/dim]\n"
        f"[dim]Started at    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        title="🤖 Agent Status",
        border_style="blue",
    ))

def shutdown(scheduler: AsyncIOScheduler) -> None:
    log.info("Shutting down agent gracefully...")
    scheduler.shutdown(wait=False)
    sys.exit(0)

async def main() -> None:
    print_banner()

    # Validate essential config before starting
    if not settings.anthropic_api_key:
        console.print("[red]ERROR:[/red] ANTHROPIC_API_KEY is missing in your .env file.")
        sys.exit(1)

    if not settings.credentials_path.exists():
        console.print("[red]ERROR:[/red] credentials.json not found. "
                      "Download it from Google Cloud Console first.")
        sys.exit(1)

    scheduler = AsyncIOScheduler(timezone="UTC")

    # Register shutdown handlers (Ctrl+C works on Windows too)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: shutdown(scheduler))
        except NotImplementedError:
            # Windows doesn't support add_signal_handler for all signals
            # KeyboardInterrupt (Ctrl+C) will still work
            pass

    scheduler.add_job(
        run_pipeline,
        trigger=IntervalTrigger(seconds=settings.poll_interval_seconds),
        id="email_pipeline",
        name="Email Pipeline",
        replace_existing=True,
        max_instances=1,        # never run two pipelines at once
    )

    scheduler.start()
    log.info(f"Scheduler started. Next run in {settings.poll_interval_seconds}s.")

    # Run once immediately on startup so you don't wait 5 minutes
    await run_pipeline()

    # Keep the event loop alive
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        shutdown(scheduler)

if __name__ == "__main__":
    asyncio.run(main())