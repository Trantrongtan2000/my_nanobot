#!/usr/bin/env python3
"""
Self-improvement cron: chỉ chạy khi agent idle (tránh treo agent).
Kết hợp curator-style idle check + error reflection.

Usage:
  python self_improve_cron.py                    # dry-run: show what would be done
  python self_improve_cron.py --run              # actually run
  python self_improve_cron.py --force            # run regardless of idle
  python self_improve_cron.py --report           # just print report
  python self_improve_cron.py --consolidate      # also consolidate old entries
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path("/home/tan/.nanobot/workspace")
MEMORY_DIR = BASE / "memory"
ERROR_LOG = MEMORY_DIR / "nanobot_errors.jsonl"
IMPROVEMENT_LOG = MEMORY_DIR / "nanobot_improvements.jsonl"
HISTORY_FILE = MEMORY_DIR / "history.jsonl"
SELF_IMPROVE = BASE / "nanobot_self_improve.py"
STATE_FILE = MEMORY_DIR / "curator_state.json"
AGENTS_FILE = BASE / "AGENTS.md"

IDLE_THRESHOLD = timedelta(hours=1)
MIN_INTERVAL = timedelta(hours=12)


def get_last_activity() -> datetime | None:
    """Find last activity timestamp from history or log files."""
    newest = None
    for f in [HISTORY_FILE, ERROR_LOG, IMPROVEMENT_LOG]:
        if not f.exists():
            continue
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            if newest is None or mtime > newest:
                newest = mtime
        except OSError:
            pass
    return newest


def get_last_curator_run() -> datetime | None:
    """Read last curator run timestamp from state file."""
    if not STATE_FILE.exists():
        return None
    try:
        data = json.loads(STATE_FILE.read_text())
        ts = data.get("last_run_at")
        if ts:
            return datetime.fromisoformat(ts)
    except (json.JSONDecodeError, KeyError, ValueError):
        return None
    return None


def save_curator_state(run_type: str, stats: dict):
    """Save curator run state."""
    state = {"last_run_at": datetime.now(timezone.utc).isoformat(), "last_run_type": run_type, "stats": stats}
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def is_idle() -> tuple[bool, str]:
    """Check if agent is idle enough for background work."""
    last = get_last_activity()
    if last is None:
        return (True, "no activity recorded")
    idle_for = datetime.now(timezone.utc) - last
    if idle_for >= IDLE_THRESHOLD:
        return (True, f"idle for {idle_for.total_seconds() / 60:.0f}m (threshold: {IDLE_THRESHOLD.total_seconds() / 60:.0f}m)")
    return (False, f"active {idle_for.total_seconds() / 60:.0f}m ago (need >{IDLE_THRESHOLD.total_seconds() / 60:.0f}m idle)")


def should_run() -> tuple[bool, str]:
    """Check if enough time since last curator run."""
    last = get_last_curator_run()
    if last is None:
        return (True, "no previous run")
    since_last = datetime.now(timezone.utc) - last
    if since_last >= MIN_INTERVAL:
        return (True, f"{since_last.total_seconds() / 3600:.1f}h since last run")
    return (False, f"last run {since_last.total_seconds() / 3600:.1f}h ago (need >{MIN_INTERVAL.total_seconds() / 3600:.1f}h)")


def run_self_improve(cmd: str, *args: str) -> str:
    """Run nanobot_self_improve.py subcommand and return output."""
    try:
        result = subprocess.run(
            [sys.executable, str(SELF_IMPROVE), cmd, *args],
            capture_output=True, text=True, timeout=120,
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return f"TIMEOUT: {cmd}"
    except Exception as e:
        return f"ERROR: {e}"


def count_unresolved_errors() -> list[dict]:
    """Count unresolved errors in the log."""
    if not ERROR_LOG.exists():
        return []
    unresolved = []
    with open(ERROR_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if not entry.get("resolved"):
                    unresolved.append(entry)
            except json.JSONDecodeError:
                continue
    return unresolved


def consolidate_old_entries(dry_run: bool = True) -> dict:
    """Consolidate/archive old unresolved errors."""
    stats = {"archived": 0, "kept": 0, "consolidated": 0}
    if not ERROR_LOG.exists():
        return stats
    entries = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=14)
    with open(ERROR_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
                # Archive unresolved errors older than 14 days
                if not entry.get("resolved") and ts < cutoff:
                    entry["resolved"] = True
                    entry["resolution"] = "auto-archived (stale)"
                    stats["archived"] += 1
                entries.append(entry)
            except (json.JSONDecodeError, ValueError):
                entries.append(json.loads(line) if line else None)
    entries = [e for e in entries if e is not None]
    if not dry_run:
        with open(ERROR_LOG, "w") as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return stats


def main():
    is_force = "--force" in sys.argv
    is_run = "--run" in sys.argv
    is_consolidate = "--consolidate" in sys.argv
    just_report = "--report" in sys.argv
    dry_run = not is_run

    if just_report:
        output = run_self_improve("report")
        print(output)
        return

    # 1. Check idle
    idle_ok, idle_msg = is_idle()
    if not idle_ok and not is_force:
        print(f"[CURATOR] SKIP: {idle_msg}")
        return

    # 2. Check interval
    interval_ok, interval_msg = should_run()
    if not interval_ok and not is_force:
        print(f"[CURATOR] SKIP: {interval_msg}")
        return

    print(f"[CURATOR] RUN ({'dry-run' if dry_run else 'live'})")
    print(f"  Idle: {idle_msg}")
    print(f"  Interval: {interval_msg}")

    # 3. Check unresolved errors
    unresolved = count_unresolved_errors()
    print(f"  Unresolved errors: {len(unresolved)}")

    stats = {"unresolved_before": len(unresolved), "reflected": 0, "archived": 0}

    # 4. Reflect on each unresolved error
    for entry in unresolved[:5]:  # max 5 per run to avoid overload
        eid = entry.get("error_id", "unknown")
        print(f"  Reflecting on {eid}: {entry.get('error', '')[:80]}...")
        if not dry_run:
            output = run_self_improve("reflect", "--error_id", eid)
            print(f"    {output[:200]}")
            stats["reflected"] += 1
        else:
            print(f"    (would reflect)")

    # 5. Consolidate old entries
    if is_consolidate:
        print(f"  Consolidating old entries...")
        cstats = consolidate_old_entries(dry_run=dry_run)
        stats.update(cstats)
        print(f"    Archived: {cstats['archived']}, Kept: {cstats['kept']}")

    if not dry_run:
        save_curator_state("full" if is_consolidate else "reflect", stats)
        print(f"[CURATOR] DONE. Stats: {json.dumps(stats)}")
    else:
        print(f"[CURATOR] DRY-RUN. Add --run to execute.")


if __name__ == "__main__":
    main()
