"""
Sends triggered signals to a Discord channel via a webhook URL.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_CONTENT_LIMIT = 2000
SAFE_CONTENT_LIMIT = 1900


def _split_discord_messages(lines: list[str]) -> list[str]:
    """Split alert lines into webhook messages under Discord's content limit."""
    messages = []
    current = ""

    for line in lines:
        next_part = line if not current else f"{current}\n\n{line}"
        if len(next_part) <= SAFE_CONTENT_LIMIT:
            current = next_part
            continue

        if current:
            messages.append(current)

        if len(line) > SAFE_CONTENT_LIMIT:
            messages.append(line[: SAFE_CONTENT_LIMIT - 3] + "...")
            current = ""
        else:
            current = line

    if current:
        messages.append(current)

    return messages


def send_discord_alert(
    triggered_signals: list[dict],
    screened_count: int | None = None,
    error_count: int = 0,
) -> None:
    if not WEBHOOK_URL:
        print("  [WARN] DISCORD_WEBHOOK_URL not set in .env - skipping Discord alert.")
        return

    if triggered_signals:
        lines = [f"**MarketPulse: {len(triggered_signals)} signal(s) triggered**"]
        for sig in triggered_signals:
            lines.append(
                f"**{sig['symbol']}** - `{sig['rule_name']}`\n"
                f"{sig['details']}\n"
                f"Price at signal: ${sig['close_at_signal']:.2f}"
            )
    else:
        screened_text = f" Screened {screened_count} ticker(s)." if screened_count is not None else ""
        error_text = f" {error_count} ticker(s) failed to process." if error_count else ""
        lines = [f"**MarketPulse ran successfully.**{screened_text} No signals triggered.{error_text}"]

    try:
        messages = _split_discord_messages(lines)
        for index, message in enumerate(messages, start=1):
            if len(messages) > 1:
                message = f"{message}\n\n_Part {index}/{len(messages)}_"
            response = requests.post(WEBHOOK_URL, json={"content": message[:DISCORD_CONTENT_LIMIT]}, timeout=10)
            response.raise_for_status()
        print(f"  Discord alert sent ({len(triggered_signals)} signal(s), {len(messages)} message(s)).")
    except requests.exceptions.RequestException as e:
        print(f"  [WARN] Failed to send Discord alert: {e}")
